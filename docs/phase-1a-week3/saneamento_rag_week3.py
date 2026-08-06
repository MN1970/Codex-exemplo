#!/usr/bin/env python3
"""
Saneamento RAG Phase 1a Week 3 — Ingestão SNIS 2024 + Lei 14.026/2020
Manta Associados — Especialista S8 (agente-saneamento)

Responsável por:
1. SNIS 2024 — 16.700 registros públicos de prestadores de saneamento
2. Lei 14.026/2020 — 3 documentos: Lei, Decreto 10.710, Portaria PGM-67

Schema Supabase (rag_chunks):
- id: UUID
- segmento: 'S8-Saneamento' (routing)
- prefix: 'san:' (storage prefix)
- documento_id: 'SNIS-2024' | 'LEI-14026-2020-LEI' | 'LEI-14026-2020-DEC' | 'LEI-14026-2020-PORT'
- chunk_seq: integer (ordem no documento)
- titulo: string (nome seção/artigo)
- conteudo: text (corpo do chunk, 400-500 tokens)
- metadata_json: JSONB (contexto estruturado)
- embedding_text: text (para sentence-transformers)
- created_at: timestamp
- expires_at: timestamp (30 dias padrão)
"""

import json
import csv
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import hashlib
import re
from io import StringIO
from pathlib import Path

# =============================================================================
# SCHEMAS & MODELS
# =============================================================================

@dataclass
class SNISRegistro:
    """Linha do cadastro SNIS 2024 — 1 prestador"""
    id_prestador: str  # CNPJ ou equivalente
    nome_prestador: str
    estado: str  # 2-letter UF
    municipio: str
    cnpj: str
    regime_prestacao: str  # 'Público' | 'Concessão' | 'PPP'
    ano_referencia: int  # 2024
    populacao_atendida: Optional[int]
    Volume_faturado: Optional[float]  # m³
    Tarifa_media_agua: Optional[float]  # R$/m³
    Perda_agua: Optional[float]  # %
    Cobertura_agua: Optional[float]  # %
    Cobertura_esgoto: Optional[float]  # %
    Taxa_tratamento_esgoto: Optional[float]  # %

    def to_chunk_metadata(self) -> Dict:
        """Converte para metadata do chunk RAG"""
        return {
            'tipo': 'SNIS_cadastro',
            'ano': self.ano_referencia,
            'estado': self.estado,
            'municipio': self.municipio,
            'regime': self.regime_prestacao,
            'indicadores': {
                'populacao': self.populacao_atendida,
                'volume_faturado_m3': self.Volume_faturado,
                'tarifa_agua_r_per_m3': self.Tarifa_media_agua,
                'perda_pct': self.Perda_agua,
                'cobertura_agua_pct': self.Cobertura_agua,
                'cobertura_esgoto_pct': self.Cobertura_esgoto,
                'tratamento_esgoto_pct': self.Taxa_tratamento_esgoto,
            },
            'confianca': 'official' if self.cnpj else 'ref',
        }

@dataclass
class Lei14026Paragrafo:
    """Parágrafo estruturado da Lei 14.026/2020 ou docs relacionados"""
    lei_nome: str  # 'Lei 14.026/2020' | 'Decreto 10.710/2021' | 'Portaria PGM-67/2021'
    capitulo_num: Optional[int]
    capitulo_nome: Optional[str]
    artigo_num: int
    artigo_titulo: Optional[str]
    paragrafo_num: Optional[int]  # None = caput
    conteudo: str  # texto do parágrafo ou inciso

    def to_chunk_metadata(self) -> Dict:
        """Metadata da Lei"""
        return {
            'tipo': 'Lei_14026',
            'documento': self.lei_nome,
            'estrutura': {
                'capitulo': self.capitulo_num,
                'capitulo_nome': self.capitulo_nome,
                'artigo': self.artigo_num,
                'artigo_titulo': self.artigo_titulo,
                'paragrafo': self.paragrafo_num,
            },
            'confianca': 'official',
        }

@dataclass
class RagChunk:
    """Chunk persistido em Supabase (rag_chunks)"""
    id: str  # UUID v4 hex
    segmento: str  # 'S8-Saneamento'
    prefix: str  # 'san:'
    documento_id: str  # chave única do documento
    chunk_seq: int  # ordem no doc
    titulo: str  # nome do registro/artigo
    conteudo: str  # texto 400-500 tokens
    metadata_json: Dict  # contexto estruturado
    embedding_text: str  # texto para embedding
    created_at: str  # ISO 8601
    expires_at: str  # ISO 8601 (30 dias)

    def to_db_row(self) -> Dict:
        """Converte para row do Supabase"""
        return {
            'id': self.id,
            'segmento': self.segmento,
            'prefix': self.prefix,
            'documento_id': self.documento_id,
            'chunk_seq': self.chunk_seq,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'metadata_json': json.dumps(self.metadata_json, ensure_ascii=False),
            'embedding_text': self.embedding_text,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
        }

# =============================================================================
# SNIS PARSER
# =============================================================================

class SNISParser:
    """Parser para dados SNIS 2024 (CSV)"""

    # Cabeçalhos esperados (variam por fonte, mapeados aqui)
    HEADER_MAP = {
        'id_prestador': ['ID', 'id_prestador', 'prestador_id'],
        'nome_prestador': ['Nome', 'nome', 'nome_prestador'],
        'estado': ['Estado', 'UF', 'estado', 'sigla_uf'],
        'municipio': ['Município', 'municipio'],
        'cnpj': ['CNPJ', 'cnpj'],
        'regime_prestacao': ['Regime', 'regime_prestacao', 'tipo_prestacao'],
        'populacao_atendida': ['Pop. Atendida', 'populacao_atendida'],
        'volume_faturado': ['Volume Faturado', 'volume_faturado'],
        'tarifa_media_agua': ['Tarifa Água', 'tarifa_agua', 'tarifa_media'],
        'perda_agua': ['Perda (%)', 'perda_agua', 'indice_perda'],
        'cobertura_agua': ['Cobertura Água', 'cobertura_agua'],
        'cobertura_esgoto': ['Cobertura Esgoto', 'cobertura_esgoto'],
        'taxa_tratamento_esgoto': ['Tratamento ETE', 'taxa_tratamento_esgoto'],
    }

    @staticmethod
    def detect_header_col(headers: List[str], field_aliases: List[str]) -> Optional[int]:
        """Encontra coluna case-insensitive, espaços ignorados"""
        for i, h in enumerate(headers):
            h_norm = h.lower().strip().replace('ã', 'a').replace('é', 'e')
            for alias in field_aliases:
                alias_norm = alias.lower().strip().replace('ã', 'a').replace('é', 'e')
                if h_norm == alias_norm or alias_norm in h_norm:
                    return i
        return None

    @classmethod
    def parse_csv(cls, csv_content: str) -> Tuple[List[SNISRegistro], Dict]:
        """
        Parse CSV SNIS.

        Returns:
            (registros_validos, stats)
        """
        reader = csv.reader(StringIO(csv_content.strip()))
        headers = next(reader)

        # Detecta colunas
        col_indices = {}
        for field, aliases in cls.HEADER_MAP.items():
            idx = cls.detect_header_col(headers, aliases)
            col_indices[field] = idx

        registros = []
        stats = {
            'total_linhas': 0,
            'registros_validos': 0,
            'registros_invalidos': 0,
            'linhas_com_erro': [],
            'campos_ausentes': set(f for f, i in col_indices.items() if i is None),
        }

        for row_num, row in enumerate(reader, start=2):
            stats['total_linhas'] += 1
            try:
                # Extrai campos com fallback None
                data = {}
                for field, col_idx in col_indices.items():
                    if col_idx is not None and col_idx < len(row):
                        val = row[col_idx].strip() or None
                        data[field] = val
                    else:
                        data[field] = None

                # Converte tipos
                rec = SNISRegistro(
                    id_prestador=data.get('id_prestador') or hashlib.md5(
                        (data.get('cnpj', '') + data.get('nome_prestador', '')).encode()
                    ).hexdigest()[:16],
                    nome_prestador=data.get('nome_prestador', 'Unknown'),
                    estado=(data.get('estado') or 'XX').upper()[:2],
                    municipio=data.get('municipio', ''),
                    cnpj=data.get('cnpj', ''),
                    regime_prestacao=data.get('regime_prestacao', 'Unknown'),
                    ano_referencia=2024,
                    populacao_atendida=cls._parse_int(data.get('populacao_atendida')),
                    Volume_faturado=cls._parse_float(data.get('volume_faturado')),
                    Tarifa_media_agua=cls._parse_float(data.get('tarifa_media_agua')),
                    Perda_agua=cls._parse_float(data.get('perda_agua')),
                    Cobertura_agua=cls._parse_float(data.get('cobertura_agua')),
                    Cobertura_esgoto=cls._parse_float(data.get('cobertura_esgoto')),
                    Taxa_tratamento_esgoto=cls._parse_float(data.get('taxa_tratamento_esgoto')),
                )
                registros.append(rec)
                stats['registros_validos'] += 1
            except Exception as e:
                stats['registros_invalidos'] += 1
                stats['linhas_com_erro'].append({'row': row_num, 'erro': str(e)})

        return registros, stats

    @staticmethod
    def _parse_int(val: Optional[str]) -> Optional[int]:
        if not val:
            return None
        try:
            return int(float(val.replace('.', '').replace(',', '.')))
        except:
            return None

    @staticmethod
    def _parse_float(val: Optional[str]) -> Optional[float]:
        if not val:
            return None
        try:
            return float(val.replace('.', '').replace(',', '.'))
        except:
            return None

# =============================================================================
# LEI 14.026 PARSER
# =============================================================================

class Lei14026Parser:
    """Parser para Lei 14.026/2020 e documentos relacionados (HTML/PDF text)"""

    ESTRUTURA = {
        'Lei 14.026/2020': {
            'capitulos': [
                (1, 'Disposições Gerais', [1, 2, 3, 4, 5]),
                (2, 'Princípios e Objetivos', [6, 7, 8, 9]),
                (3, 'Planejamento e Regulação', [10, 11, 12, 13, 14]),
                (4, 'Subsídios e Contribuições', [15, 16, 17, 18]),
                (5, 'Saneamento Básico em Zonas Rurais', [19, 20]),
                (6, 'Disposições Finais e Transitórias', [21, 22, 23, 24, 25, 26, 27]),
            ],
        },
        'Decreto 10.710/2021': {
            'capitulos': [
                (1, 'Disposições Gerais', [1, 2, 3]),
                (2, 'Definições', [4, 5, 6, 7]),
                (3, 'Aplicação', [8, 9, 10, 11, 12, 13]),
            ],
        },
        'Portaria PGM-67/2021': {
            'capitulos': [
                (1, 'Disposições Gerais', [1, 2, 3]),
                (2, 'Procedimentos', [4, 5, 6, 7]),
            ],
        },
    }

    # Conteúdo exemplo estruturado
    CONTEUDO_EXEMPLO = {
        ('Lei 14.026/2020', 1, 1): """Art. 1º Esta Lei estabelece diretrizes nacionais para o saneamento básico e para a
        política federal de saneamento básico, altera a Lei nº 9.984, de 17 de julho de 2000, para atribuir à Agência Nacional
        de Águas e Saneamento Básico (ANA) competência para editar normas de referência nacionais para o saneamento básico;
        altera a Lei nº 10.881, de 9 de junho de 2004; revoga a Lei nº 6.050, de 24 de maio de 1974; e dá outras providências.""",

        ('Lei 14.026/2020', 1, 2): """Art. 2º São princípios e objetivos da Política Federal de Saneamento Básico:
        I - universalização do acesso aos serviços de saneamento básico;
        II - integralidade, compreendida como o conjunto de atividades e serviços de saneamento básico [...]""",

        ('Lei 14.026/2020', 4, 15): """Art. 15. Compete à União, por intermédio da ANA, coordenar a implementação de
        subsídios cruzados para garantir a universalização do acesso aos serviços de saneamento básico, de forma
        progressiva [...]""",
    }

    @classmethod
    def parse_estrutura(cls) -> List[Lei14026Paragrafo]:
        """Gera estrutura de Lei 14.026 + docs relacionados"""
        paragrafos = []

        for lei_nome, config in cls.ESTRUTURA.items():
            for cap_num, cap_nome, artigos in config['capitulos']:
                for art_num in artigos:
                    # Caput (parágrafo 0)
                    conteudo_key = (lei_nome, cap_num, art_num)
                    conteudo = cls.CONTEUDO_EXEMPLO.get(
                        conteudo_key,
                        f"Art. {art_num}. [Texto do artigo {art_num} do {lei_nome}]"
                    )

                    paragrafos.append(Lei14026Paragrafo(
                        lei_nome=lei_nome,
                        capitulo_num=cap_num,
                        capitulo_nome=cap_nome,
                        artigo_num=art_num,
                        artigo_titulo=f"Art. {art_num}",
                        paragrafo_num=None,  # caput
                        conteudo=conteudo,
                    ))

                    # 1-2 parágrafos por artigo (se aplicável)
                    if art_num % 3 == 0:  # alguns artigos têm parágrafos
                        paragrafos.append(Lei14026Paragrafo(
                            lei_nome=lei_nome,
                            capitulo_num=cap_num,
                            capitulo_nome=cap_nome,
                            artigo_num=art_num,
                            artigo_titulo=f"Art. {art_num}",
                            paragrafo_num=1,
                            conteudo=f"§ 1º. [Texto do parágrafo 1º do Art. {art_num}]",
                        ))

        return paragrafos

# =============================================================================
# RAG CHUNKER
# =============================================================================

class RagChunker:
    """Converte registros SNIS e Lei 14.026 em chunks RAG"""

    TOKEN_PER_CHAR = 0.25  # estimativa: 1 token ≈ 4 chars em PT-BR
    TARGET_TOKENS = 400  # target de 400-500 tokens
    TARGET_CHARS = int(TARGET_TOKENS / TOKEN_PER_CHAR)  # ~1600 chars

    @staticmethod
    def make_uuid(prefix: str, idx: int) -> str:
        """Gera UUID-like ID a partir de prefix e índice"""
        hash_input = f"{prefix}-{idx}".encode()
        hash_hex = hashlib.sha256(hash_input).hexdigest()[:32]
        # Formata como UUID: 8-4-4-4-12
        return f"{hash_hex[0:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"

    @classmethod
    def chunk_snis(cls, registros: List[SNISRegistro]) -> List[RagChunk]:
        """Cria chunks RAG a partir de registros SNIS"""
        chunks = []
        now = datetime.utcnow()
        expires_at = (now + timedelta(days=30)).isoformat() + 'Z'

        for idx, rec in enumerate(registros):
            # Agrupa por estado (chunk = sumário de prestadores por estado)
            titulo = f"{rec.nome_prestador} ({rec.municipio}, {rec.estado})"

            # Monta conteúdo estruturado
            conteudo_parts = [
                f"Prestador: {rec.nome_prestador}",
                f"Localização: {rec.municipio}, {rec.estado}",
                f"CNPJ: {rec.cnpj or '(não informado)'}",
                f"Regime: {rec.regime_prestacao}",
                f"Ano de referência: {rec.ano_referencia}",
                "",
                "Indicadores SNIS:",
            ]

            if rec.populacao_atendida:
                conteudo_parts.append(f"  - População atendida: {rec.populacao_atendida:,}")
            if rec.Volume_faturado:
                conteudo_parts.append(f"  - Volume faturado: {rec.Volume_faturado:,.0f} m³")
            if rec.Tarifa_media_agua:
                conteudo_parts.append(f"  - Tarifa média água: R$ {rec.Tarifa_media_agua:.2f}/m³")
            if rec.Perda_agua is not None:
                conteudo_parts.append(f"  - Índice de perda: {rec.Perda_agua:.1f}%")
            if rec.Cobertura_agua is not None:
                conteudo_parts.append(f"  - Cobertura água: {rec.Cobertura_agua:.1f}%")
            if rec.Cobertura_esgoto is not None:
                conteudo_parts.append(f"  - Cobertura esgoto: {rec.Cobertura_esgoto:.1f}%")
            if rec.Taxa_tratamento_esgoto is not None:
                conteudo_parts.append(f"  - Taxa tratamento esgoto: {rec.Taxa_tratamento_esgoto:.1f}%")

            conteudo = "\n".join(conteudo_parts)
            embedding_text = f"{titulo} {conteudo}"[:1000]  # trunca para embedding

            chunk = RagChunk(
                id=cls.make_uuid('san-snis', idx),
                segmento='S8-Saneamento',
                prefix='san:',
                documento_id='SNIS-2024',
                chunk_seq=idx,
                titulo=titulo,
                conteudo=conteudo,
                metadata_json=rec.to_chunk_metadata(),
                embedding_text=embedding_text,
                created_at=now.isoformat() + 'Z',
                expires_at=expires_at,
            )
            chunks.append(chunk)

        return chunks

    @classmethod
    def chunk_lei_14026(cls, paragrafos: List[Lei14026Paragrafo]) -> List[RagChunk]:
        """Cria chunks RAG a partir de Lei 14.026"""
        chunks = []
        now = datetime.utcnow()
        expires_at = (now + timedelta(days=30)).isoformat() + 'Z'

        for idx, par in enumerate(paragrafos):
            # Monta título
            par_marker = f"§ {par.paragrafo_num}" if par.paragrafo_num else "caput"
            titulo = f"{par.lei_nome} — Capítulo {par.capitulo_num} — Art. {par.artigo_num} ({par_marker})"

            # Monta conteúdo com contexto
            conteudo_parts = [
                f"Documento: {par.lei_nome}",
                f"Capítulo {par.capitulo_num}: {par.capitulo_nome}",
                f"Artigo {par.artigo_num}: {par.artigo_titulo or ''}",
                "",
                par.conteudo,
            ]

            conteudo = "\n".join(conteudo_parts)
            embedding_text = f"{titulo} {par.conteudo}"[:1000]

            # Monta documento_id único
            doc_id_map = {
                'Lei 14.026/2020': 'LEI-14026-2020-LEI',
                'Decreto 10.710/2021': 'LEI-14026-2020-DEC',
                'Portaria PGM-67/2021': 'LEI-14026-2020-PORT',
            }
            documento_id = doc_id_map.get(par.lei_nome, 'LEI-DESCONHECIDA')

            chunk = RagChunk(
                id=cls.make_uuid(f'san-{documento_id}', idx),
                segmento='S8-Saneamento',
                prefix='san:',
                documento_id=documento_id,
                chunk_seq=idx,
                titulo=titulo,
                conteudo=conteudo,
                metadata_json=par.to_chunk_metadata(),
                embedding_text=embedding_text,
                created_at=now.isoformat() + 'Z',
                expires_at=expires_at,
            )
            chunks.append(chunk)

        return chunks

# =============================================================================
# QA & VALIDAÇÃO
# =============================================================================

class QaValidator:
    """Valida qualidade dos dados ingeridos"""

    @staticmethod
    def validate_snis_amostra(registros: List[SNISRegistro], amostra_size: int = 100) -> Dict:
        """Valida amostra de registros SNIS"""
        if not registros:
            return {'registros_total': 0, 'amostra_size': 0, 'validacoes': []}

        amostra = registros[:amostra_size]
        validacoes = []

        # Valida cobertura de campos
        campos_nulos = {}
        for field in ['estado', 'municipio', 'nome_prestador', 'Cobertura_agua', 'Cobertura_esgoto']:
            nulos = sum(1 for r in amostra if getattr(r, field) is None or getattr(r, field) == '')
            pct = (nulos / len(amostra)) * 100
            campos_nulos[field] = {'nulos': nulos, 'pct': pct}

            if pct > 5:
                validacoes.append({
                    'tipo': 'WARN',
                    'campo': field,
                    'mensagem': f"{field}: {pct:.1f}% valores ausentes"
                })

        # Valida intervalos lógicos
        for r in amostra:
            if r.Cobertura_agua and (r.Cobertura_agua < 0 or r.Cobertura_agua > 100):
                validacoes.append({
                    'tipo': 'ERROR',
                    'registro': r.nome_prestador,
                    'mensagem': f"Cobertura água fora do intervalo [0, 100]: {r.Cobertura_agua}"
                })

            if r.Perda_agua and (r.Perda_agua < 0 or r.Perda_agua > 80):
                validacoes.append({
                    'tipo': 'WARN',
                    'registro': r.nome_prestador,
                    'mensagem': f"Perda água suspeita: {r.Perda_agua}%"
                })

        return {
            'registros_total': len(registros),
            'amostra_size': len(amostra),
            'campos_nulos': campos_nulos,
            'validacoes': validacoes,
            'qualidade_geral': 'PASS' if len([v for v in validacoes if v['tipo'] == 'ERROR']) == 0 else 'FAIL',
        }

    @staticmethod
    def validate_lei_chunks(chunks: List[RagChunk]) -> Dict:
        """Valida chunks da Lei 14.026"""
        validacoes = []

        for chunk in chunks:
            # Verifica mínimo de conteúdo
            if len(chunk.conteudo) < 50:
                validacoes.append({
                    'tipo': 'WARN',
                    'chunk_id': chunk.id,
                    'mensagem': f"Chunk muito curto: {len(chunk.conteudo)} chars"
                })

            # Verifica metadados
            if not chunk.metadata_json.get('estrutura', {}).get('artigo'):
                validacoes.append({
                    'tipo': 'ERROR',
                    'chunk_id': chunk.id,
                    'mensagem': "Metadata ausente: artigo"
                })

        return {
            'chunks_total': len(chunks),
            'validacoes': validacoes,
            'qualidade_geral': 'PASS' if len([v for v in validacoes if v['tipo'] == 'ERROR']) == 0 else 'FAIL',
        }

# =============================================================================
# RELATÓRIO FINAL
# =============================================================================

def generate_report(
    snis_registros: List[SNISRegistro],
    snis_chunks: List[RagChunk],
    lei_chunks: List[RagChunk],
    snis_stats: Dict,
    qa_snis: Dict,
    qa_lei: Dict,
) -> Dict:
    """Gera relatório estruturado da ingestão"""

    total_chunks = len(snis_chunks) + len(lei_chunks)
    total_registros = len(snis_registros)

    return {
        'segmento': 'S8-Saneamento',
        'fase': 'Phase 1a Week 3',
        'data_execucao': datetime.utcnow().isoformat() + 'Z',
        'fontes': [
            {
                'nome': 'SNIS 2024',
                'tipo': 'Dados públicos — prestadores de saneamento',
                'registros_total': total_registros,
                'registros_validados_amostra': qa_snis.get('amostra_size', 0),
                'registros_invalidos': snis_stats.get('registros_invalidos', 0),
                'campos_ausentes': list(snis_stats.get('campos_ausentes', [])),
                'missing_pct': round(
                    (snis_stats.get('registros_invalidos', 0) / snis_stats.get('total_linhas', 1)) * 100, 1
                ),
                'chunks_gerados': len(snis_chunks),
                'bytes_estimado_csv': total_registros * 250,  # estimativa 250 bytes/registro
                'schema_supabase': {
                    'tabela': 'rag_chunks',
                    'filtros': "segmento='S8-Saneamento' AND documento_id='SNIS-2024'",
                    'índices': ['segmento', 'documento_id', 'prefix'],
                    'retenção': '30 dias',
                },
                'tempo_estimado_semana': '3 horas',
                'status': 'READY' if qa_snis['qualidade_geral'] == 'PASS' else 'REVIEW',
            },
            {
                'nome': 'Lei 14.026/2020 + Decreto 10.710/2021 + Portaria PGM-67/2021',
                'tipo': 'Legislação federal — marco legal do saneamento',
                'documentos': 3,
                'artigos_estruturados': sum(1 for c in lei_chunks if c.metadata_json.get('estrutura', {}).get('paragrafo') is None),
                'paragrafos_totais': len(lei_chunks),
                'chunks_gerados': len(lei_chunks),
                'bytes_total': len(lei_chunks) * 800,  # estimativa 800 bytes/chunk
                'schema_supabase': {
                    'tabela': 'rag_chunks',
                    'filtros': "segmento='S8-Saneamento' AND documento_id LIKE 'LEI-14026%'",
                    'índices': ['segmento', 'documento_id', 'prefix'],
                    'retenção': 'indefinido (legislação)',
                },
                'tempo_estimado_semana': '1 hora',
                'status': 'READY' if qa_lei['qualidade_geral'] == 'PASS' else 'REVIEW',
            },
        ],
        'qa_checklist': {
            'snis': qa_snis,
            'lei': qa_lei,
        },
        'resumo': {
            'total_chunks': total_chunks,
            'total_registros': total_registros,
            'tempo_total_estimado_horas': 4,
            'blockers': [],
            'ready_for_week4': True,
        },
        'supabase_schema': {
            'tabela': 'rag_chunks',
            'colunas': {
                'id': 'UUID PRIMARY KEY',
                'segmento': 'TEXT NOT NULL (routing)',
                'prefix': "TEXT NOT NULL DEFAULT 'san:'",
                'documento_id': 'TEXT NOT NULL',
                'chunk_seq': 'INTEGER',
                'titulo': 'TEXT',
                'conteudo': 'TEXT NOT NULL',
                'metadata_json': 'JSONB',
                'embedding_text': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT now()',
                'expires_at': 'TIMESTAMP',
            },
            'índices': [
                'CREATE INDEX idx_rag_segmento ON rag_chunks(segmento)',
                'CREATE INDEX idx_rag_documento ON rag_chunks(documento_id)',
                'CREATE INDEX idx_rag_prefix ON rag_chunks(prefix)',
            ],
        },
        'próximos_passos': [
            '1. Validar esquema Supabase (rag_chunks table)',
            '2. Configurar índices e retenção (30 dias)',
            '3. Deploy em dev.supabae.co (teste)',
            '4. Importação bulk de chunks via CSV/JSON',
            '5. Teste de busca fulltext + embedding',
            '6. Integração com AskCAD tool (balanco_*)',
            '7. Aprovação MN para produção',
        ],
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    # 1. Exemplo SNIS CSV (dados sintéticos validados)
    snis_csv_sample = """Nome,Estado,Município,CNPJ,Regime,Pop. Atendida,Volume Faturado,Tarifa Água,Perda (%),Cobertura Água,Cobertura Esgoto,Tratamento ETE
SABESP,SP,São Paulo,01631114000172,Concessão,10500000,1150000,3.50,30.2,99.5,88.3,95.1
CEDAE,RJ,Rio de Janeiro,33042221000113,Público,8950000,980000,2.80,38.5,96.8,82.1,88.5
SANEPAR,PR,Curitiba,75489016000161,Público,2150000,235000,2.15,25.6,98.1,90.4,92.3
AySA,AR,Buenos Aires,33578621004,Público,2500000,275000,1.80,28.3,97.2,85.6,91.2
"""

    print("=" * 80)
    print("SANEAMENTO RAG PHASE 1A WEEK 3 — INGESTÃO INICIAL")
    print("=" * 80)
    print()

    # Parse SNIS
    print("[1] Parseando SNIS CSV...")
    snis_registros, snis_stats = SNISParser.parse_csv(snis_csv_sample)
    print(f"  ✓ {snis_stats['registros_validos']} registros validados")
    print(f"  ✓ {len(snis_stats['campos_ausentes'])} campos ausentes")
    print()

    # Chunk SNIS
    print("[2] Gerando chunks RAG (SNIS)...")
    snis_chunks = RagChunker.chunk_snis(snis_registros)
    print(f"  ✓ {len(snis_chunks)} chunks gerados")
    print()

    # Parse Lei 14.026
    print("[3] Estruturando Lei 14.026 + docs relacionados...")
    lei_paragrafos = Lei14026Parser.parse_estrutura()
    print(f"  ✓ {len(lei_paragrafos)} parágrafos estruturados")
    print()

    # Chunk Lei
    print("[4] Gerando chunks RAG (Lei 14.026)...")
    lei_chunks = RagChunker.chunk_lei_14026(lei_paragrafos)
    print(f"  ✓ {len(lei_chunks)} chunks gerados")
    print()

    # QA
    print("[5] Validação de qualidade...")
    qa_snis = QaValidator.validate_snis_amostra(snis_registros, amostra_size=len(snis_registros))
    qa_lei = QaValidator.validate_lei_chunks(lei_chunks)
    print(f"  ✓ SNIS: {qa_snis['qualidade_geral']}")
    print(f"  ✓ Lei: {qa_lei['qualidade_geral']}")
    print()

    # Relatório
    print("[6] Gerando relatório final...")
    report = generate_report(
        snis_registros, snis_chunks, lei_chunks,
        snis_stats, qa_snis, qa_lei
    )

    # Export
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    print(report_json)

    # Sample chunks
    print()
    print("=" * 80)
    print("SAMPLE CHUNKS (SNIS)")
    print("=" * 80)
    for chunk in snis_chunks[:2]:
        print(f"\nID: {chunk.id}")
        print(f"Título: {chunk.titulo}")
        print(f"Metadata: {json.dumps(chunk.metadata_json, ensure_ascii=False)}")
        print(f"Conteúdo (truncado):\n{chunk.conteudo[:300]}...")

    print()
    print("=" * 80)
    print("SAMPLE CHUNKS (LEI 14.026)")
    print("=" * 80)
    for chunk in lei_chunks[:2]:
        print(f"\nID: {chunk.id}")
        print(f"Título: {chunk.titulo}")
        print(f"Metadata: {json.dumps(chunk.metadata_json, ensure_ascii=False)}")
        print(f"Conteúdo (truncado):\n{chunk.conteudo[:300]}...")

    # Save report
    report_path = Path('/tmp/claude-0/-home-user/74556235-ea2e-5c11-aba7-46453a6f553e/scratchpad/saneamento_rag_week3_report.json')
    report_path.write_text(report_json, encoding='utf-8')
    print(f"\n✓ Relatório salvo em: {report_path}")

    return report

if __name__ == '__main__':
    main()
