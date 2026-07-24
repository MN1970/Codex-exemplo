# Plataformas e Repositórios Similares ao HuggingFace Hub - Guia Completo

**Data de compilação:** Julho 2026
**Total de plataformas:** 40+

---

## SUMÁRIO EXECUTIVO

O HuggingFace Hub domina como a plataforma de modelo mais popular com 500K+ modelos. Contudo, existe um ecossistema robusto de alternativas especializadas, fragmentado em cinco categorias principais:

1. **Plataformas Concorrentes Diretas** — Model hubs full-stack com datasets e spaces
2. **Alternativas Open-Source** — Self-hosted e descentralizadas
3. **Plataformas de Inferência** — APIs e serverless para servir modelos
4. **Repositórios Especializados** — Focados em domínios específicos (CV, NLP, etc)
5. **Ferramentas de Rastreamento MLOps** — Model registry e versionamento

---

## 1. PLATAFORMAS CONCORRENTES DIRETAS

### 1.1 ModelScope (Alibaba)
- **URL:** https://modelscope.cn | https://modelscope.models.alibaba.com
- **Tipo:** Model hub + datasets + pipeline inference
- **Público-alvo:** Desenvolvedores globais (focado China/Ásia)
- **Conteúdo:** 
  - 70K+ modelos (2025)
  - 2K+ organizações contribuintes
  - 16 milhões de desenvolvedores em 36 países
- **Características principais:**
  - Model-as-a-Service (MaaS) integrado
  - Suporte multilíngue nativo
  - Linha de produção integrada (DAMO)
  - Integração com Alibaba Cloud
- **Licença:** Open-source (Python SDK; plataforma proprietária)
- **Força:** Distribuição padrão para modelos Qwen (LLMs principais)
- **Fraqueza:** Menor comunidade fora Ásia; documentação em chinês

---

### 1.2 GitHub Models
- **URL:** https://github.com/models
- **Tipo:** Model marketplace integrado ao GitHub
- **Público-alvo:** Equipes GitHub; devs já em repositórios
- **Conteúdo:**
  - Modelos proprietários e open-source
  - Acesso via GitHub workflow existente
  - Permissões alinhadas ao repo
- **Características principais:**
  - Native GitHub integration (no switching)
  - API compatibility com plataformas de chat
  - Copilot + Model integration
- **Licença:** Proprietário (Microsoft)
- **Força:** Conveniência para devs GitHub; permissões centralizadas
- **Fraqueza:** Catálogo menor que HF; paywall de acesso a LLMs premium

---

### 1.3 OpenModelDB / Open Model Database
- **URL:** https://openmodeldb.info
- **Tipo:** Database comunitária de modelos upscaling
- **Público-alvo:** Artistas, fotógrafos, videastas
- **Conteúdo:**
  - Modelos de upscaling (super-resolution, interpolação)
  - Metadados completos e exemplos visuais
- **Características principais:**
  - Comparação visual entre modelos
  - Benchmark de performance
  - Arquitetura e peso de modelos detalhados
- **Licença:** Open-source (comunidade)
- **Força:** Especialização em upscaling; comunidade ativa visual
- **Fraqueza:** Nicho específico; baixo volume de modelos

---

## 2. ALTERNATIVAS OPEN-SOURCE (SELF-HOSTED)

### 2.1 Ollama
- **URL:** https://ollama.ai | GitHub: ollama/ollama
- **Tipo:** Local inference runtime + model library
- **Público-alvo:** Individual developers, privacy-conscious orgs
- **Conteúdo:**
  - Biblioteca de modelos pré-otimizados
  - Docker-first architecture
  - CLI simples + REST API
- **Características principais:**
  - 164K+ GitHub stars
  - 15-20% mais rápido que LocalAI
  - Integração com 100+ tools (LM Studio, Open WebUI, n8n, etc)
  - Suporte GPU automático (NVIDIA, AMD, Intel, Metal)
  - Zero config inference
- **Licença:** MIT (open-source)
- **Força:** Simplicidade; performance; comunidade vibrante
- **Fraqueza:** Local-only (não é hub/sharing platform)

---

### 2.2 LocalAI
- **URL:** https://localai.io | GitHub: mudler/LocalAI
- **Tipo:** Local/self-hosted AI server
- **Público-alvo:** DevOps, enterprise self-hosted needs
- **Conteúdo:**
  - Multi-model loading
  - Audio, image, embeddings, completions
  - Docker/Kubernetes native
- **Características principais:**
  - OpenAI API compatibility
  - Multimodal (text, vision, speech)
  - Stateless & container-orchestrated
  - Backend abstraction (Ollama, llama.cpp, GPTQ)
- **Licença:** MIT (open-source)
- **Força:** Enterprise-ready; orchestration support
- **Fraqueza:** Overhead vs Ollama; menos documentação

---

### 2.3 LM Studio
- **URL:** https://lmstudio.ai
- **Tipo:** Desktop app para modelo experimentation
- **Público-alvo:** Non-technical users, researchers exploring
- **Conteúdo:**
  - Built-in model browser
  - Pre-optimized model library
  - REST API server
- **Características principais:**
  - GUI-first, zero command-line
  - Side-by-side model comparison
  - Local chat interface
  - GPU acceleration automática
- **Licença:** Proprietário (freeware)
- **Força:** UX best-in-class para desktop; zero setup
- **Fraqueza:** Desktop-only; closed-source; sem features enterprise

---

### 2.4 Open WebUI
- **URL:** https://openwebui.com | GitHub: open-webui/open-webui
- **Tipo:** Web UI para local/remote LLM inference
- **Público-alvo:** Teams rodando Ollama/LocalAI/OpenAI APIs
- **Conteúdo:**
  - Chat interface minimalista
  - Multi-model support
  - Document upload & RAG
- **Características principais:**
  - Compatível com Ollama/OpenAI/GGML
  - Docker deployment
  - User management multi-tenant
  - Web-based (no client install)
- **Licença:** MIT (open-source)
- **Força:** Simplicity; multi-tenant support
- **Fraqueza:** Interface only; não gerencia modelos

---

## 3. PLATAFORMAS DE INFERÊNCIA (SERVERLESS/API)

### 3.1 Replicate
- **URL:** https://replicate.com
- **Tipo:** Inference API + model hosting
- **Público-alvo:** Developers, product teams, enterprises
- **Conteúdo:**
  - 50K+ open-source models
  - Community-contributed + official
  - Support for custom model deployment
- **Características principais:**
  - Pay-per-second pricing
  - Automatic scaling
  - WebHooks para async jobs
  - REST API + Python/JavaScript SDKs
  - Adquirida por Cloudflare (Nov 2025, fechada 2026)
- **Licença:** Proprietário (com modelos open-source)
- **Força:** Modelo preço simples; catálogo enorme; UX limpa
- **Fraqueza:** Dependência Cloudflare; menos modelo control (vs Baseten)
- **Status 2026:** Integrada Workers AI Cloudflare

---

### 3.2 Together AI
- **URL:** https://www.together.ai
- **Tipo:** LLM inference + fine-tuning platform
- **Público-alvo:** LLM-focused teams, API consumers
- **Conteúdo:**
  - 100+ open-source LLMs
  - Fine-tuning service
  - Vision models
- **Características principais:**
  - OpenAI-compatible API
  - Lowest token cost (2026)
  - ~$1B ARR (2026)
  - Speculative decoding, batching otimizado
  - MCP integration
- **Licença:** Proprietário (models open-source)
- **Força:** Melhor preço LLMs; OpenAI compatibility; community trust
- **Fraqueza:** LLM-focused (menos multimodal que Replicate)

---

### 3.3 Fireworks AI
- **URL:** https://fireworks.ai
- **Tipo:** Fast LLM inference platform
- **Público-alvo:** LLM developers, production workloads
- **Conteúdo:**
  - 50+ LLMs
  - Proprietary + open-source
  - Fine-tuning capability
- **Características principais:**
  - Speculative decoding para speed
  - ~$800M ARR (2026)
  - OpenAI-compatible API
  - Function calling native
- **Licença:** Proprietário (models open-source)
- **Força:** Speed-optimized; production-grade SLAs
- **Fraqueza:** LLM-only; menos community

---

### 3.4 Modal
- **URL:** https://modal.com
- **Tipo:** Serverless GPU compute platform
- **Público-algo:** Python developers, ML teams
- **Conteúdo:**
  - Deployment of any Python inference
  - Custom model support
  - Training jobs
- **Características principais:**
  - Python-first (modal.run)
  - Full compute control (vs Replicate pre-built)
  - Auto-scaling GPUs
  - ~$300M ARR (2026)
  - Webhook support
- **Licença:** Proprietário
- **Força:** Controle completo; flexibilidade; Python nativo
- **Fraqueza:** Curva aprendizado; overhead vs Replicate

---

### 3.5 Baseten
- **URL:** https://www.baseten.co
- **Tipo:** Model deployment + training platform
- **Público-alvo:** ML teams com custom models
- **Conteúdo:**
  - Custom model deployment
  - Training capability (novo 2026)
  - Model APIs (novo 2026)
- **Características principais:**
  - Low-code UI (Truss framework)
  - Autoscaling
  - Basic observability
  - Multi-node fine-tuning
  - ~$600M ARR (2026)
- **Licença:** Proprietário
- **Força:** Developer experience; feature richness; vendor flexibility
- **Fraqueza:** Maior overhead vs Replicate para simple models

---

### 3.6 DeepInfra
- **URL:** https://deepinfra.com
- **Tipo:** Open-source model inference API
- **Público-alvo:** Open-source model users
- **Conteúdo:**
  - 100+ open-source models
  - Community contributions
- **Características principais:**
  - OpenAI-compatible API
  - Good pricing (second-tier)
  - Text + embeddings
- **Licença:** Proprietário (models open-source)
- **Força:** Community-aligned; transparent pricing
- **Fraqueza:** Documentação menos polida

---

### 3.7 OpenRouter
- **URL:** https://openrouter.ai
- **Tipo:** LLM router/aggregator
- **Público-alvo:** Cost-conscious LLM users
- **Conteúdo:**
  - 100+ LLMs via unified API
  - Proprietary + open-source
- **Características principais:**
  - Single API, multiple provider backends
  - Fallback routing
  - Per-model rate limits
  - Transformers + structured output support
- **Licença:** Proprietário
- **Força:** Maximum flexibility; price arbitrage
- **Fraqueza:** Less predictable latency (multi-provider)

---

### 3.8 Anyscale
- **URL:** https://www.anyscale.com
- **Tipo:** Distributed compute platform (Ray-based)
- **Público-alvo:** Teams with Ray workloads, large-scale ML
- **Conteúdo:**
  - Ray Serve for model serving
  - Distributed training support
  - Batch inference
- **Características principais:**
  - Multi-node tensor parallelism
  - Ray integration (70B+ model support)
  - Kubernetes orchestration
  - Used by OpenAI, Uber, Spotify
- **Licença:** Proprietário (Ray open-source)
- **Força:** Production-grade; large-model support
- **Fraqueza:** Overhead para simple models; Ray lock-in

---

## 4. REPOSITÓRIOS ESPECIALIZADOS POR DOMÍNIO

### 4.1 TensorFlow Hub
- **URL:** https://tfhub.dev
- **Tipo:** Model zoo + pre-trained assets
- **Público-alvo:** TensorFlow ecosystem users
- **Conteúdo:**
  - 2500+ modelos
  - Vision, text, audio
  - SavedModel format nativo
- **Características principais:**
  - Google-backed
  - Plug-and-play integration
  - Text embeddings, dense passage retrieval
  - Multi-format support (SavedModel, TF.js)
- **Licença:** Open-source (models varied)
- **Força:** Production-quality models; Google backing
- **Fraqueza:** Framework-specific; menos modelos que HF

---

### 4.2 PyTorch Hub
- **URL:** https://pytorch.org/hub
- **Tipo:** Model zoo para PyTorch
- **Público-alvo:** PyTorch developers
- **Conteúdo:**
  - 200+ modelos
  - Official + community
  - Vision, NLP, audio
- **Características principais:**
  - Meta-maintained
  - torch.hub.load() simple
  - GitHub repo wrapper
- **Licença:** Open-source (models varied)
- **Força:** Framework nativo; simplicidade
- **Fraqueza:** Menos models que TF Hub; comunidade menos engaged

---

### 4.3 OpenMMLab (Model Zoo)
- **URL:** https://platform.openmmlab.com/modelzoo/
- **Tipo:** Computer vision specialized model zoo
- **Público-alvo:** Computer vision researchers, practitioners
- **Conteúdo:**
  - Object detection (MMDetection)
  - Pose estimation (MMPose)
  - Semantic segmentation (MMSegmentation)
  - Image classification (MMClassification)
  - Text OCR (MMOCR)
  - Self-supervised learning (MMSelfSup)
- **Características principais:**
  - HKUST-backed open-source initiative
  - Unified PyTorch interface
  - Benchmarks publicados
  - Config-driven architecture
- **Licença:** Open-source (Apache 2.0)
- **Força:** Especialização CV; académica credibilidade
- **Fraqueza:** CV-only; curva aprendizado configs

---

### 4.4 Civitai
- **URL:** https://civitai.com
- **Tipo:** Marketplace para generative art models
- **Público-alvo:** Artists, image generation enthusiasts
- **Conteúdo:**
  - 100K+ Stable Diffusion checkpoints
  - LoRAs (Low-Rank Adapters)
  - Embeddings textuais
  - Aesthetic gradients
  - Flux.1 models
- **Características principais:**
  - Browser-integrated image generator
  - Download para uso local
  - Community monetization (Civitai Creator Program)
  - Version control de modelos
  - Gallery + showcase
- **Licença:** Proprietário (models varied open-source)
- **Força:** Nicho dominante; comunidade criativa; monetização
- **Fraqueza:** Generative art-only; moderation challenges

---

### 4.5 Papers with Code Model Database
- **URL:** https://paperswithcode.com
- **Tipo:** Research models + datasets + benchmarks
- **Público-alvo:** Researchers, practitioners
- **Conteúdo:**
  - 1.7M+ papers (via ArXiv partnership)
  - Linked datasets
  - Benchmark leaderboards
  - Code implementations
- **Características principais:**
  - ArXiv integration (Code & Data tabs)
  - Task-centric organization
  - Reproducibility focus
  - Dataset usage tracking
- **Licença:** Proprietário (content open-access)
- **Força:** Research-first; auditável reproducibility
- **Fraqueza:** Não é deployment hub; curadoria manual

---

### 4.6 Kaggle Datasets + Models
- **URL:** https://kaggle.com
- **Tipo:** Competitions + datasets + models
- **Público-alvo:** Data scientists, competition participants
- **Conteúdo:**
  - 50K+ public datasets
  - 2000+ linked TensorFlow Hub models
  - Competitions com prizes
- **Características principais:**
  - Notebooks colaborativos
  - Tier system (Novice → Grandmaster)
  - Featured competitions ($)
  - Dataset versioning
- **Licença:** Proprietário (dados/modelos mixed)
- **Força:** Community driven; learning path
- **Fraqueza:** Competition-focused; nem todos models open-access

---

### 4.7 ONNX Model Zoo
- **URL:** https://onnx.ai/models/
- **Tipo:** Cross-framework model repository
- **Público-alvo:** Framework-agnostic practitioners
- **Conteúdo:**
  - 500+ pre-trained models
  - Computer vision, NLP, speech
  - MobileNet, BERT, ResNet, etc
- **Características principais:**
  - Interoperability (ONNX format)
  - Framework-independent deployment
  - Legacy-focused (novo content → HF)
- **Licença:** Open-source (models varied)
- **Força:** Interoperability; legacy support
- **Fraqueza:** Archived 2025 (LFS downloads ended); movendo para HF

---

## 5. FERRAMENTAS DE RASTREAMENTO E VERSIONAMENTO (MLOps)

### 5.1 MLflow Model Registry
- **URL:** https://mlflow.org
- **Tipo:** Experiment tracking + model registry
- **Público-alvo:** ML teams, experiment management
- **Conteúdo:**
  - Modelo versioning
  - Artifact tracking
  - Experiment comparison
- **Características principais:**
  - Open-source (Apache 2.0)
  - Framework-agnostic
  - Built-in UI
  - Databricks enterprise tier
- **Licença:** Open-source (Community) / Proprietário (Enterprise)
- **Força:** Open-source; universidade adoção
- **Fraqueza:** UI menos polida que W&B; auto-logging menos mature

---

### 5.2 Weights & Biases (W&B)
- **URL:** https://wandb.ai
- **Tipo:** Experiment tracking + model registry + reports
- **Público-alvo:** Research teams, production ML
- **Conteúdo:**
  - Model checkpoints versionados
  - Experiment history
  - Sweep optimization
  - Reports colaborativos
- **Características principais:**
  - 30+ framework integrations
  - Real-time collaboration
  - Superior UX/visualizations
  - Weave (LLM tracing, novo)
  - Pricing: ~$50/user/month (2026)
- **Licença:** Proprietário (com tier free)
- **Força:** Best UX; team collaboration; framework support
- **Fraqueza:** Pricey; vendor lock-in; closed-source

---

### 5.3 ClearML
- **URL:** https://clear.ml
- **Tipo:** MLOps + model registry + experiment tracking
- **Público-alvo:** Enterprise ML teams
- **Conteúdo:**
  - Model registry com lineage tracking
  - Experiment comparison
  - Task orchestration
  - Pipeline automation
- **Características principais:**
  - Open-source core (+ enterprise)
  - Auto-logging (TensorFlow, PyTorch)
  - Artifact management
  - Kubernetes integration
- **Licença:** Open-source (Community) / Proprietário (Enterprise)
- **Força:** Full MLOps platform; open-source option
- **Fraqueza:** Curva aprendizado; documentação gaps

---

### 5.4 ModelDB (by Verta.ai)
- **URL:** https://github.com/VertaAI/modeldb
- **Tipo:** Open-source model versioning
- **Público-alvo:** Teams versionando modelos localmente
- **Conteúdo:**
  - Modelo storage + metadata
  - Experiment tracking
  - Dataset versioning
- **Características principais:**
  - Python/Scala clients
  - Web frontend
  - gRPC backend
  - Maintained by Verta.ai
- **Licença:** Open-source (Apache 2.0)
- **Força:** Open-source; lightweight
- **Fraqueza:** Menos features que MLflow; comunidade pequena

---

### 5.5 Kubeflow Model Registry
- **URL:** https://github.com/kubeflow/model-registry
- **Tipo:** Kubernetes-native model registry
- **Público-alvo:** Kubernetes-centric ML teams
- **Conteúdo:**
  - Central model index
  - Version management
  - ML artifact metadata
- **Características principais:**
  - Kubernetes first-class
  - DAG-centric
  - Integration com Kubeflow pipelines
- **Licença:** Open-source (Apache 2.0)
- **Força:** Kubernetes integration; cloud-native
- **Fraqueza:** Steep learning curve; Kubernetes requirement

---

### 5.6 Neptune.ai
- **URL:** https://neptune.ai
- **Tipo:** Experiment tracking + model registry
- **Público-alvo:** Data science teams
- **Conteúdo:**
  - Experiment comparison
  - Model versioning
  - Artifact management
- **Características principais:**
  - Mid-tier features (W&B e MLflow)
  - 30+ integrations
  - Webhook support
  - Custom dashboards
- **Licença:** Proprietário (com tier free)
- **Força:** Good balance features/price
- **Fraqueza:** Menos market share; documentação menor

---

## 6. COMPARAÇÃO RESUMIDA POR CATEGORIA

### Model Hubs (HuggingFace Direct Competitors)
| Plataforma | Modelos | Datasets | Spaces | Público-alvo | Força chave |
|------------|---------|----------|--------|-------------|-------------|
| **HuggingFace** | 500K+ | 200K+ | 50K+ | Global | Comunidade; amplitude |
| ModelScope | 70K+ | 30K+ | N/A | Ásia, devs | MaaS integrado; Qwen |
| GitHub Models | 100+ | N/A | N/A | Devs GitHub | Conveniência; integração |
| OpenModelDB | 5K+ | N/A | N/A | Artists | Upscaling especializado |

### Inferência Serverless
| Plataforma | Best for | Preço | API Style |
|------------|----------|-------|-----------|
| **Replicate** | Catálogo maior; simplicidade | $$$ | REST custom |
| Together AI | LLMs baratos; throughput | $$ | OpenAI compatible |
| Fireworks AI | Speed; production | $$ | OpenAI compatible |
| Modal | Controle total; custom | $$$ | Python-first |
| Baseten | Teams; training | $$$ | Low-code UI |

### Self-Hosted Local
| Plataforma | Força | Fraqueza | GPU Support |
|------------|-------|----------|-------------|
| **Ollama** | Simplicidade; speed | Local-only | NVIDIA, AMD, Metal |
| LocalAI | Enterprise-ready; Kubernetes | Overhead | Multiple |
| LM Studio | Best desktop UX | Desktop-only | NVIDIA, AMD, Metal |
| Open WebUI | Web-based; multi-tenant | Interface-only | Via backends |

### Computer Vision Specializado
| Plataforma | Foco | Tamanho | Académico |
|------------|------|--------|----------|
| TensorFlow Hub | General CV | 2500+ | Sim (Google) |
| OpenMMLab | Detection, segmentation, pose | 1000+ | Sim (HKUST) |
| PyTorch Hub | General PyTorch | 200+ | Sim (Meta) |
| Civitai | Generative art | 100K+ | Não |

---

## 7. MATRIZ DE DECISÃO

### Escolha por Use Case

**Preciso compartilhar modelos publicamente?**
- HuggingFace (padrão)
- ModelScope (Ásia)
- Civitai (arte generativa)

**Preciso servir inferência em produção?**
- Replicate (simplicidade)
- Together AI (LLMs baixo custo)
- Fireworks AI (speed)
- Modal (controle total)
- Baseten (training + inference)

**Preciso rodar localmente/offline?**
- Ollama (simplicidade)
- LocalAI (enterprise)
- LM Studio (GUI)

**Preciso rastrear experimentos/versionamento?**
- Weights & Biases (best UX)
- MLflow (open-source)
- ClearML (full MLOps)

**Preciso especialização (CV)?**
- OpenMMLab (detection, pose)
- TensorFlow Hub (geral)

**Preciso generative art?**
- Civitai (padrão)

---

## 8. TENDÊNCIAS 2026

### Market Consolidation
- **Replicate adquirida por Cloudflare** (Nov 2025, merged 2026)
- **Together AI, Fireworks AI crescimento explosivo** (~$1B, $800M ARR)
- **Open-source dominance** (Ollama 164K stars; community prefers local)

### Feature Parity
- **OpenAI API compatibility** padrão (Together, Fireworks, DeepInfra, OpenRouter)
- **Vision models mainstream** (todos fornecedores têm suporte multimodal)
- **Fine-tuning democratizado** (Replicate via inference, Baseten Training, Together)

### Specialization
- **Civitai + generative art boom** (100K+ models, comunidade monetizada)
- **Regional hubs crescem** (ModelScope en Ásia; potencial para LATAM)
- **Enterprise MLOps** diferenciação via Kubernetes, observability (Anyscale, ClearML)

---

## 9. RECOMENDAÇÕES FINAIS

### Para Indivíduos / Hobby
1. **HuggingFace** - padrão ouro
2. **Ollama** - local, zero custo após setup
3. **Civitai** - generative art

### Para Startups / SMBs
1. **HuggingFace** - comunidade + modelos
2. **Replicate** ou **Together AI** - inferência serverless (escolha preço vs controle)
3. **Weights & Biases** - experiment tracking se budget permite, senão **MLflow**

### Para Empresas / Enterprise
1. **HuggingFace Enterprise** - catálogo + support
2. **Baseten** - deployment + training
3. **ClearML** ou **Weights & Biases** - MLOps
4. **Anyscale** - distributed training/serving (se Ray users)
5. **Modelo self-hosted** (Ollama + Kubernetes) para dados sensíveis

### Para Researchers
1. **HuggingFace** - comunidade padrão
2. **Papers with Code** - reproducibility + benchmarks
3. **Kaggle** - datasets + competitions (learning)
4. **ModelScope** (se trabalha Qwen/Alibaba models)

---

## 10. URLS DE REFERÊNCIA RÁPIDA

| Plataforma | URL |
|------------|-----|
| HuggingFace | https://huggingface.co |
| ModelScope | https://modelscope.cn |
| GitHub Models | https://github.com/models |
| Replicate | https://replicate.com |
| Together AI | https://www.together.ai |
| Fireworks AI | https://fireworks.ai |
| Modal | https://modal.com |
| Baseten | https://www.baseten.co |
| OpenRouter | https://openrouter.ai |
| Ollama | https://ollama.ai |
| LocalAI | https://localai.io |
| LM Studio | https://lmstudio.ai |
| TensorFlow Hub | https://tfhub.dev |
| PyTorch Hub | https://pytorch.org/hub |
| OpenMMLab | https://openmmlab.com |
| Civitai | https://civitai.com |
| Papers with Code | https://paperswithcode.com |
| Kaggle | https://kaggle.com |
| MLflow | https://mlflow.org |
| Weights & Biases | https://wandb.ai |
| ClearML | https://clear.ml |
| Neptune.ai | https://neptune.ai |

---

## APÊNDICE: CATEGORIAS EMERGENTES

### Multimodal Platforms (2025+)
- **LLaVA ecosystem** — Vision + language instruction tuning
- **CLIP variants** — Text-image alignment
- **Diffusion + LLM combos** — Codex, Flamingo derivatives

### Specialized Verticals (novo 2026)
- **Medical imaging** — no HuggingFace
- **Autonomous vehicles** — fragmented (proprietary)
- **Synthetic data generation** — growing niche

### Decentralized Options (research phase)
- **Huggingface IPFS integration** (beta)
- **Blockchain model registries** — low adoption (2026)
- **DAO-based model repositories** — emerging

---

**Nota:** Este documento foi compilado em Julho 2026. Tecnologia de IA evolui rapidamente; verificar URLs e feature parity antes de decisões críticas.

---
