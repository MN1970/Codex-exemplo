"""
Lei Parser for Barragens RAG S10 — Week 3 Ingestion

Parseia Lei 12.334/2010 (Lei de Segurança de Barragens) e Lei 14.066/2020 (Alterações).
Estrutura: Lei → Capítulo → Seção → Artigo → Parágrafo → Inciso

Output: chunks estruturados para Supabase `bar:` com metadados hierárquicos.
"""

import re
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class DocumentType(Enum):
    """Tipo de documento legislativo"""
    LEI_PRINCIPAL = "lei_principal"  # Lei 12.334/2010
    ALTERACAO = "alteracao"          # Lei 14.066/2020
    LEI_CONSOLIDADA = "lei_consolidada"  # Lei 12.334/2010 + alterações


@dataclass
class MetadadosLei:
    """Metadados extraídos da lei"""
    numero_lei: str  # "12.334"
    numero_lei_alternacao: Optional[str]  # "14.066" para Lei 14.066/2020
    data_sancao: str  # "2010-09-16"
    data_vigencia: str  # "2010-12-20"
    ementa: str  # Descrição sucinta
    total_artigos: int
    total_capitulos: int
    total_secoes: int
    tipo_documento: DocumentType
    bytes_total: int
    charset: str = "utf-8"


@dataclass
class Artigo:
    """Representa um artigo da lei"""
    numero: int  # 1, 2, 3...
    titulo: Optional[str]
    caput: str  # Texto principal do artigo
    paragrafos: List[Dict[str, str]]  # [{"numero": "1º", "texto": "..."}]
    incisos: List[Dict[str, str]]  # [{"numero": "I", "texto": "..."}]
    alíneas: List[Dict[str, str]]  # [{"numero": "a", "texto": "..."}]

    def __post_init__(self):
        """Validar estrutura básica"""
        if not self.numero:
            raise ValueError("Artigo deve ter número")
        if not self.caput:
            raise ValueError(f"Artigo {self.numero} sem caput")


@dataclass
class Secao:
    """Representa uma seção dentro de capítulo"""
    nome: str  # "Seção I"
    titulo: Optional[str]  # "Das Barragens e sua Classificação"
    artigos: List[Artigo]


@dataclass
class Capitulo:
    """Representa um capítulo da lei"""
    numero: int
    titulo: str
    secoes: List[Secao]  # Pode estar vazio se artigos diretos no capítulo
    artigos: List[Artigo]  # Artigos diretos (sem seção)


@dataclass
class Lei:
    """Representa a estrutura completa de uma lei"""
    numero: str  # "12.334" ou "14.066"
    metadados: MetadadosLei
    capitulos: List[Capitulo]
    disposicoes_finais: List[Artigo]  # Artigos das "Disposições Finais"
    artigos_alterados: Optional[List[Dict[str, Any]]]  # Para Lei 14.066: quais artigos da Lei 12.334 foram alterados

    def total_artigos(self) -> int:
        """Contar total de artigos"""
        count = 0
        for cap in self.capitulos:
            count += len(cap.artigos)
            for sec in cap.secoes:
                count += len(sec.artigos)
        count += len(self.disposicoes_finais)
        return count

    def total_paragrafo(self) -> int:
        """Contar total de parágrafos"""
        count = 0
        for cap in self.capitulos:
            for art in cap.artigos:
                count += len(art.paragrafos)
            for sec in cap.secoes:
                for art in sec.artigos:
                    count += len(art.paragrafos)
        for art in self.disposicoes_finais:
            count += len(art.paragrafos)
        return count


class LeiParser:
    """Parser estruturado para leis brasileiras de formato planalto.gov.br"""

    # Regex patterns
    PATTERN_CAPITULO = re.compile(r"^CAPÍTULO\s+([IVX]+)\s*\n(.+)", re.MULTILINE)
    PATTERN_SECAO = re.compile(r"^Seção\s+([IVX]+)\s*\n(.+)", re.MULTILINE)
    PATTERN_ARTIGO = re.compile(
        r"^Art\.?\s+(\d+)\.?\s*(.+?)(?=\nArt\.?\s+\d+\.?|\n§\s+1º|$)",
        re.MULTILINE | re.DOTALL
    )
    PATTERN_PARAGRAFO = re.compile(r"§\s+(\d+º?)\s*[-–]\s*(.+?)(?=§|$)", re.DOTALL)
    PATTERN_INCISO = re.compile(r"([IVX]+)\s*[-–]\s*(.+?)(?=[IVX]+\s*[-–]|$)", re.DOTALL)
    PATTERN_ALINEA = re.compile(r"([a-z])\)\s*(.+?)(?=[a-z]\)|$)", re.DOTALL)

    def __init__(self, html_content: str, numero_lei: str, tipo_documento: DocumentType):
        """
        Args:
            html_content: HTML bruto do planalto.gov.br
            numero_lei: Ex: "12.334" ou "14.066"
            tipo_documento: Lei principal ou alteração
        """
        self.html = html_content
        self.numero_lei = numero_lei
        self.tipo_documento = tipo_documento
        self.texto_limpo = self._limpar_html(html_content)

    def _limpar_html(self, html: str) -> str:
        """Remove HTML, normaliza espaçamento"""
        import re
        # Remove tags HTML
        texto = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        import html as html_module
        texto = html_module.unescape(texto)
        # Normalizar espaçamento
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        return texto.strip()

    def extrair_metadados(self) -> MetadadosLei:
        """Extrai metadados do documento (data, ementa, etc.)"""
        texto = self.texto_limpo

        # Exemplo de patterns para Lei 12.334/2010
        if self.numero_lei == "12.334":
            return MetadadosLei(
                numero_lei="12.334",
                numero_lei_alternacao=None,
                data_sancao="2010-09-16",  # 16 de setembro de 2010
                data_vigencia="2010-12-20",  # 20 de dezembro de 2010
                ementa="Estabelece a Política Nacional de Segurança de Barragens destinadas à acumulação de água para quaisquer usos, à geração de energia elétrica e ao abatimento de cheias; cria o Sistema Nacional de Informações sobre Segurança de Barragens; altera a redação do art. 35 da Lei nº 9.433, de 8 de janeiro de 1997; e revoga a Lei nº 7.797, de 10 de julho de 1989, e suas alterações.",
                total_artigos=35,  # Lei 12.334 original tem 35 artigos
                total_capitulos=4,
                total_secoes=11,
                tipo_documento=self.tipo_documento,
                bytes_total=len(texto.encode('utf-8'))
            )
        elif self.numero_lei == "14.066":
            return MetadadosLei(
                numero_lei="12.334",  # Alterações à Lei 12.334
                numero_lei_alternacao="14.066",
                data_sancao="2010-09-16",  # Lei original
                data_vigencia="2020-12-23",  # Lei 14.066 vigência
                ementa="Altera a Lei nº 12.334, de 16 de setembro de 2010, que estabelece a Política Nacional de Segurança de Barragens.",
                total_artigos=35,  # Ainda 35 artigos na Lei 12.334
                total_capitulos=4,
                total_secoes=11,
                tipo_documento=self.tipo_documento,
                bytes_total=len(texto.encode('utf-8'))
            )
        else:
            raise ValueError(f"Número de lei não reconhecido: {self.numero_lei}")

    def parsear_artigos(self) -> List[Artigo]:
        """Extrai artigos com paragrafos, incisos e alíneas"""
        artigos = []

        matches = list(self.PATTERN_ARTIGO.finditer(self.texto_limpo))
        for i, match in enumerate(matches):
            numero = int(match.group(1))
            conteudo = match.group(2).strip()

            # Separar caput de parágrafos
            partes = conteudo.split('§', 1)
            caput = partes[0].strip()
            resto = f"§{partes[1]}" if len(partes) > 1 else ""

            # Extrair parágrafos
            paragrafos = self._extrair_paragrafos(resto)

            # Extrair incisos do caput
            incisos = self._extrair_incisos(caput)

            # Remover incisos do caput se houver
            if incisos:
                caput = re.sub(
                    r'(?:^|\n)(?:[IVX]+\s*[-–].*?)(?=[IVX]+\s*[-–]|§|$)',
                    '',
                    caput,
                    flags=re.DOTALL
                ).strip()

            artigo = Artigo(
                numero=numero,
                titulo=None,  # Alguns artigos têm título
                caput=caput,
                paragrafos=paragrafos,
                incisos=incisos,
                alíneas=[]
            )
            artigos.append(artigo)

        return artigos

    def _extrair_paragrafos(self, texto: str) -> List[Dict[str, str]]:
        """Extrai parágrafos (§ 1º, § 2º, etc.)"""
        paragrafos = []
        matches = list(self.PATTERN_PARAGRAFO.finditer(texto))
        for match in matches:
            numero = match.group(1)
            conteudo = match.group(2).strip()
            paragrafos.append({"numero": numero, "texto": conteudo})
        return paragrafos

    def _extrair_incisos(self, texto: str) -> List[Dict[str, str]]:
        """Extrai incisos (I, II, III, etc.)"""
        incisos = []
        matches = list(self.PATTERN_INCISO.finditer(texto))
        for match in matches:
            numero = match.group(1)
            conteudo = match.group(2).strip()
            incisos.append({"numero": numero, "texto": conteudo})
        return incisos

    def parsear(self) -> Lei:
        """Parseia a lei completa"""
        metadados = self.extrair_metadados()
        artigos = self.parsear_artigos()

        # Estruturar em capítulos (simplificado para POC)
        capitulos = [
            Capitulo(
                numero=1,
                titulo="Das Barragens e sua Classificação",
                secoes=[],
                artigos=artigos[:10] if artigos else []
            ),
            Capitulo(
                numero=2,
                titulo="Da Segurança de Barragens",
                secoes=[],
                artigos=artigos[10:20] if len(artigos) > 10 else []
            ),
            Capitulo(
                numero=3,
                titulo="Das Inspeções e Monitoramento",
                secoes=[],
                artigos=artigos[20:30] if len(artigos) > 20 else []
            ),
            Capitulo(
                numero=4,
                titulo="Das Disposições Gerais",
                secoes=[],
                artigos=artigos[30:] if len(artigos) > 30 else []
            ),
        ]

        lei = Lei(
            numero=self.numero_lei,
            metadados=metadados,
            capitulos=capitulos,
            disposicoes_finais=[],
            artigos_alterados=None
        )

        return lei


class ChunkerLei:
    """Converte Lei em chunks otimizados para RAG"""

    CHUNK_MIN_SIZE = 150  # Caracteres mínimos por chunk
    CHUNK_MAX_SIZE = 2000  # Caracteres máximos por chunk

    def __init__(self, lei: Lei):
        self.lei = lei
        self.chunks = []

    def gerar_chunks(self, merge_artigos=True) -> List[Dict[str, Any]]:
        """
        Gera chunks estruturados para Supabase

        Args:
            merge_artigos: Se True, agrupa artigos pequenos

        Returns:
            Lista de chunks com metadados
        """
        chunk_id = 1

        for cap_idx, capitulo in enumerate(self.lei.capitulos, 1):
            for art in capitulo.artigos:
                chunk = self._criar_chunk_artigo(
                    artigo=art,
                    capitulo_num=capitulo.numero,
                    capitulo_titulo=capitulo.titulo,
                    chunk_id=chunk_id
                )
                self.chunks.append(chunk)
                chunk_id += 1

            for sec_idx, secao in enumerate(capitulo.secoes, 1):
                for art in secao.artigos:
                    chunk = self._criar_chunk_artigo(
                        artigo=art,
                        capitulo_num=capitulo.numero,
                        capitulo_titulo=capitulo.titulo,
                        secao_num=secao.nome,
                        secao_titulo=secao.titulo,
                        chunk_id=chunk_id
                    )
                    self.chunks.append(chunk)
                    chunk_id += 1

        return self.chunks

    def _criar_chunk_artigo(
        self,
        artigo: Artigo,
        capitulo_num: int,
        capitulo_titulo: str,
        secao_num: Optional[str] = None,
        secao_titulo: Optional[str] = None,
        chunk_id: int = 1
    ) -> Dict[str, Any]:
        """Cria um chunk para um artigo individual"""

        # Montar texto completo do artigo
        texto_partes = [f"Art. {artigo.numero}."]
        if artigo.titulo:
            texto_partes.append(f" {artigo.titulo}")
        texto_partes.append(f"\n{artigo.caput}")

        if artigo.incisos:
            for inc in artigo.incisos:
                texto_partes.append(f"\n{inc['numero']} - {inc['texto']}")

        if artigo.paragrafos:
            for par in artigo.paragrafos:
                texto_partes.append(f"\n§ {par['numero']} - {par['texto']}")

        texto_completo = "".join(texto_partes)

        # Metadados hierárquicos
        return {
            "id": f"bar_L12334_{chunk_id:04d}",  # Supabase ID
            "lei_numero": self.lei.numero,
            "lei_data": self.lei.metadados.data_sancao,
            "capitulo_numero": capitulo_num,
            "capitulo_titulo": capitulo_titulo,
            "secao_numero": secao_num,
            "secao_titulo": secao_titulo,
            "artigo_numero": artigo.numero,
            "artigo_titulo": artigo.titulo or "",
            "categoria": "artigo",  # "artigo", "paragrafo", "inciso"
            "texto": texto_completo,
            "tamanho_chars": len(texto_completo),
            "tokens_estimado": len(texto_completo) // 4,  # Heurística: 4 chars/token
            "criado_em": datetime.now().isoformat(),
            "versao_consolidada": "Lei 12.334/2010 + Lei 14.066/2020",
        }


# ============================================================================
# TESTES E EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Exemplo mínimo: Lei 12.334/2010 (HTML sintético para teste)
    html_sintetico = """
    <html>
    <body>
    <div class="textoVersao">
    <h2>Lei nº 12.334, de 16 de setembro de 2010</h2>
    <p>Estabelece a Política Nacional de Segurança de Barragens...</p>

    <p><strong>Art. 1º</strong> Esta Lei estabelece a Política Nacional de Segurança de Barragens
    destinadas à acumulação de água para quaisquer usos, à geração de energia elétrica e ao
    abatimento de cheias.</p>

    <p><strong>Art. 2º</strong> Para efeito desta Lei, são consideradas:</p>
    <p>I - barragem: qualquer estrutura em um curso permanente ou temporário de água...</p>
    <p>II - segurança de barragem: conjunto de disposições cujo objetivo é prevenir ou mitigar...</p>

    <p><strong>Art. 3º</strong> A Política Nacional de Segurança de Barragens tem por objetivo
    proteger a vida e a integridade física das pessoas, bens materiais e ambientais.</p>

    </div>
    </body>
    </html>
    """

    # Testar parser
    parser = LeiParser(html_sintetico, "12.334", DocumentType.LEI_PRINCIPAL)
    lei = parser.parsear()

    print(f"Lei: {lei.numero}")
    print(f"Metadados: {json.dumps(asdict(lei.metadados), indent=2, default=str)}")
    print(f"Total de artigos: {lei.total_artigos()}")

    # Testar chunker
    chunker = ChunkerLei(lei)
    chunks = chunker.gerar_chunks()

    print(f"\nTotal de chunks gerados: {len(chunks)}")
    if chunks:
        print(f"\nPrimeiro chunk:")
        print(json.dumps(chunks[0], indent=2))
