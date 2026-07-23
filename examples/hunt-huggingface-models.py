#!/usr/bin/env python3
"""
Hunting Phase — Buscar modelos/agentes em Hugging Face.

Objetivo: Encontrar modelos IA no Hugging Face que possam integrar com Manta:
- Modelos de NLP para análise de documentos
- Computer Vision para CAD/BIM
- Modelos específicos de engenharia
- Transformers para extração de dados

Uso:
    python examples/hunt-huggingface-models.py
"""

import subprocess
import json
import re
from typing import List, Dict
from dataclasses import dataclass, asdict


@dataclass
class HFModel:
    """Modelo encontrado em Hugging Face."""
    nome: str
    repositorio: str
    tipo: str  # nlp, vision, code, multi-modal
    task: str  # text-classification, document-qa, image-segmentation, etc
    downloads: int = 0
    likes: int = 0
    descricao: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


def search_huggingface_with_obscura(query: str) -> str:
    """Buscar modelos em Hugging Face usando Obscura."""
    url = f"https://huggingface.co/models?search={query}"

    cmd = [
        "/root/.local/bin/obscura",
        "fetch",
        url,
        "--dump",
        "markdown"
    ]

    print(f"🤗 Buscando em Hugging Face: {query}", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"⚠️  Erro na busca: {result.stderr[:200]}")
        return None

    return result.stdout


def suggest_models_for_manta() -> List[Dict]:
    """Sugerir modelos HF relevantes para Manta."""
    suggestions = [
        {
            "nome": "layoutlm-base (Microsoft)",
            "url": "https://huggingface.co/microsoft/layoutlm-base-uncased",
            "tipo": "vision",
            "task": "document-understanding",
            "uso_manta": "Extrair campos de documentos (editais, contratos)",
            "compatibilidade": "🟢 Alta",
            "skill": "ler-edital"
        },
        {
            "nome": "bert-base-portuguese-cased (BERTimbau)",
            "url": "https://huggingface.co/neuralmind/bert-base-portuguese-cased",
            "tipo": "nlp",
            "task": "text-classification",
            "uso_manta": "Classificar documentos em português (SICRO, licitações)",
            "compatibilidade": "🟢 Alta",
            "skill": "mk-manta"
        },
        {
            "nome": "donut (Naver/Google)",
            "url": "https://huggingface.co/naver-clova-ocr/donut-base-finetuned-docvqa",
            "tipo": "vision",
            "task": "document-qa",
            "uso_manta": "Extrair informações de PDFs/imagens (plantas, orçamentos)",
            "compatibilidade": "🟡 Média",
            "skill": "project-scanner"
        },
        {
            "nome": "table-transformer (Microsoft)",
            "url": "https://huggingface.co/microsoft/table-transformer-detection",
            "tipo": "vision",
            "task": "table-detection",
            "uso_manta": "Extrair tabelas de documentos (licitações, orçamentos)",
            "compatibilidade": "🟢 Alta",
            "skill": "ler-edital"
        },
        {
            "nome": "CodeBERT (Facebook/Microsoft)",
            "url": "https://huggingface.co/microsoft/codebert-base",
            "tipo": "code",
            "task": "code-search-retrieval",
            "uso_manta": "Buscar code/queries similares (SQL, VBA em projetos)",
            "compatibilidade": "🟡 Média",
            "skill": "project-scanner"
        },
        {
            "nome": "CLIP (OpenAI)",
            "url": "https://huggingface.co/openai/clip-vit-large-patch14",
            "tipo": "vision",
            "task": "image-text-matching",
            "uso_manta": "Indexar imagens de plantas/renders (busca visual)",
            "compatibilidade": "🟢 Alta",
            "skill": "visual-search"
        },
        {
            "nome": "Flan-T5 (Google)",
            "url": "https://huggingface.co/google/flan-t5-base",
            "tipo": "nlp",
            "task": "text-generation",
            "uso_manta": "Geração de parecer técnico (resumo de documentos)",
            "compatibilidade": "🟢 Alta",
            "skill": "manta-advisory"
        },
        {
            "nome": "YOLOv8 (Ultralytics)",
            "url": "https://huggingface.co/ultralytics/yolov8m",
            "tipo": "vision",
            "task": "object-detection",
            "uso_manta": "Detecção de objetos em fotos de obras (segurança, progresso)",
            "compatibilidade": "🟡 Média",
            "skill": "obra-monitoring"
        },
        {
            "nome": "mBART (Meta)",
            "url": "https://huggingface.co/facebook/mbart-large-50",
            "tipo": "nlp",
            "task": "machine-translation",
            "uso_manta": "Traduzir normas/especificações (EN → PT, PT → EN)",
            "compatibilidade": "🟢 Alta",
            "skill": "tradução-normas"
        },
        {
            "nome": "BEiT (Meta)",
            "url": "https://huggingface.co/microsoft/beit-large-patch16-224",
            "tipo": "vision",
            "task": "image-classification",
            "uso_manta": "Classificar imagens de documentos (edital, contrato, laudo)",
            "compatibilidade": "🟢 Alta",
            "skill": "document-classification"
        }
    ]

    return suggestions


def generate_huggingface_report(models: List[Dict]) -> str:
    """Gerar relatório de modelos HF para Manta."""
    report = [
        "\n" + "=" * 90,
        "🤗 HUGGING FACE MODELS — Integração com Manta Maestro",
        "=" * 90,
        f"\n📊 Modelos recomendados: {len(models)}\n"
    ]

    # Agrupar por tipo
    nlp_models = [m for m in models if m.get("tipo") == "nlp"]
    vision_models = [m for m in models if m.get("tipo") == "vision"]
    code_models = [m for m in models if m.get("tipo") == "code"]

    if nlp_models:
        report.append("📝 MODELOS NLP:")
        for model in nlp_models:
            report.append(f"   • {model['nome']:35} → {model['skill']}")
            report.append(f"     Task: {model['task']}")
            report.append(f"     Compatibilidade: {model['compatibilidade']}\n")

    if vision_models:
        report.append("👁️  MODELOS VISION:")
        for model in vision_models:
            report.append(f"   • {model['nome']:35} → {model['skill']}")
            report.append(f"     Task: {model['task']}")
            report.append(f"     Compatibilidade: {model['compatibilidade']}\n")

    if code_models:
        report.append("💻 MODELOS CODE:")
        for model in code_models:
            report.append(f"   • {model['nome']:35} → {model['skill']}")
            report.append(f"     Task: {model['task']}")
            report.append(f"     Compatibilidade: {model['compatibilidade']}\n")

    report.append("\n" + "=" * 90)
    report.append("🎯 TOP 3 PRIORITÁRIOS:")
    report.append("""
1. LayoutLM (Microsoft) — Document understanding
   → Extrair campos de editais automaticamente
   → Integrar com skill `ler-edital`

2. BERT-Portuguese (BERTimbau) — Classificação em PT
   → Categorizar documentos (edital, contrato, laudo)
   → Integrar com `mk-manta` para business case

3. Table-Transformer (Microsoft) — Table detection
   → Extrair tabelas de licitações
   → Integrar com `ler-edital` + `orcamento`
""")
    report.append("=" * 90)

    return "\n".join(report)


def integration_examples() -> str:
    """Exemplos de integração HF models com Manta."""
    examples = [
        """
EXEMPLO 1: LayoutLM para extrair editais
─────────────────────────────────────────
# skill: ler-edital-v3.py
from transformers import LayoutLMForTokenClassification, AutoProcessor

processor = AutoProcessor.from_pretrained("microsoft/layoutlm-base-uncased")
model = LayoutLMForTokenClassification.from_pretrained(...)

# 1. Obscura: fetch edital PDF
edital_pdf = await obscura.fetch(url, dump="original")

# 2. Converter para imagem (PDF → PNG)
images = pdf2image.convert_from_bytes(edital_pdf)

# 3. LayoutLM: extrair campos
for img in images:
    inputs = processor(img, return_tensors="pt")
    outputs = model(**inputs)
    # → extrai: número, data, objeto, valores, contatos, etc
""",
        """
EXEMPLO 2: BERT-Portuguese para classificação
───────────────────────────────────────────────
# skill: mk-manta.py + classificador
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="neuralmind/bert-base-portuguese-cased"
)

# Classificar documento capturado
texto_doc = ocr_document(arquivo)
categoria = classifier(texto_doc[:512])[0]
# → "edital", "contrato", "laudo", "relatório", etc

# Indexar em Supabase com categoria
await supabase.table("rag_chunks").insert({
    "texto": texto_doc,
    "categoria": categoria,
    "fonte": arquivo
})
""",
        """
EXEMPLO 3: Integração com MCP Obscura
──────────────────────────────────────
# Na skill que usa ler-edital:
1. Obscura (MCP): fetch PDF renderizado
2. LayoutLM (HF): extrair campos
3. BERT (HF): classificar tipo
4. Supabase: indexar resultado
5. Manta Advisory (15): gerar parecer

Pipeline automático:
  Obscura → LayoutLM → BERT → Supabase → Advisory
"""
    ]

    return "\n".join(examples)


def main():
    print("\n🤗 HUNTING PHASE — Hugging Face Models\n")

    # Obter sugestões
    models = suggest_models_for_manta()

    # Gerar relatório
    report = generate_huggingface_report(models)
    print(report)

    # Exemplos
    print("\n" + "=" * 90)
    print("💡 EXEMPLOS DE INTEGRAÇÃO:")
    print("=" * 90)
    print(integration_examples())

    # Salvar
    with open("/tmp/huggingface-models.json", "w") as f:
        json.dump(models, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Relatório salvo: /tmp/huggingface-models.json\n")

    print("\n📚 Próximos passos:")
    print("""
1. Escolher top 3 modelos (LayoutLM, BERT-PT, Table-Transformer)
2. Criar skills que integrem modelos HF
3. Testar com documentos reais (editais, contratos)
4. Avaliar performance (accuracy, latency)
5. Registrar no CLAUDE.md como "HF Models Connectors"
6. Documentar em "skills/huggingface-models.md"
""")


if __name__ == "__main__":
    main()
