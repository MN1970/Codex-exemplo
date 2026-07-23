# Web Scraping Global — Código de Clientes (JP, KR, CN)

**Objetivo:** Extrair padrões de código de tecnologia global usando Obscura em **paralelo** (múltiplos agentes)

---

## 1. Sites por Região

### 🌐 Hugging Face (Global)
| Site | Tipo | Dados |
|------|------|-------|
| huggingface.co/organizations | Orgs | Companies usando HF |
| huggingface.co/models | Models | Trending models |
| huggingface.co/spaces | Apps | Apps-source examples |
| huggingface.co/papers | Research | Paper implementations |

**Código esperado:** PyTorch, TensorFlow, JAX, Transformers

---

### 🐙 GitHub (Global)
| Site | Query |
|------|-------|
| github.com/trending | Trending repos |
| github.com/search?q=transformers | NLP models |
| github.com/search?q=pytorch | Deep learning |
| github.com/topics/machine-learning | ML topic |

**Padrões:** imports, class definitions, training loops

---

### 🇯🇵 Japão (Tech Sites)

| Site | URL | Tipo | Linguagem |
|------|-----|------|-----------|
| **Qiita** | qiita.com | Tech articles | 日本語 |
| **Zenn** | zenn.dev | Dev articles | 日本語 |
| **GitHub JP** | github.com/topics/japanese | Repos | Mixed |
| **Atmarkit** | atmarkit.co.jp | News | 日本語 |
| **Tech Nikkeibp** | tech.nikkeibp.co.jp | News | 日本語 |

**Empresas alvo:** Toyota, Sony, Canon, NEC, Fujitsu, Panasonic, Hitachi, NHK, SoftBank

**Frameworks populares:** PyTorch (academia), TensorFlow (produção), JAX (pesquisa)

**Exemplo de busca:**
```bash
obscura fetch "https://qiita.com/search?q=transformers&sort=stock" --dump markdown
```

---

### 🇰🇷 Coréia (Tech Sites)

| Site | URL | Tipo | Linguagem |
|------|-----|------|-----------|
| **GitHub KR** | github.com/awesome-kor | Lists | Mixed |
| **Naver Dev** | d2.naver.com | Blog | 한국어 |
| **Daily Secu** | dailysecu.com | News | 한국어 |
| **Naver News** | news.naver.com/section | News | 한국어 |

**Empresas alvo:** Samsung, LG, Naver, Kakao, SK, KT, Hyundai, CJ

**Frameworks populares:** PyTorch (mobile), TensorFlow (servers), JAX (research)

**Especialidades:** NLP coreano (Jamo, syllable-based), mobile CV

**Exemplo:**
```bash
obscura fetch "https://github.com/awesome-kor/awesome-korean-nlp" --dump markdown
```

---

### 🇨🇳 China (Tech Sites) — **NOVO**

| Site | URL | Tipo | Linguagem |
|------|-----|------|-----------|
| **Gitee** | gitee.com | GitHub CN | 中文 |
| **CSDN** | csdn.net | Articles | 中文 |
| **Zhihu** | zhihu.com/topic | Discussions | 中文 |
| **GitHub CN Topics** | github.com/topics/chinese | Repos | Mixed |
| **Baidu Research** | research.baidu.com | Papers | 中文 |

**Empresas alvo:** Alipay, Baidu, Tencent, ByteDance, Huawei, Alibaba, JD.com, Meituan, Didi

**Frameworks populares:**
- **MindSpore** (Huawei)
- **PaddlePaddle** (Baidu)
- **PyTorch** (standard)
- **TensorFlow** (enterprise)

**Especialidades:** 
- NLP chinês (caracteres, pinyin, tokenização)
- Computer Vision (face detection, OCR)
- E-commerce AI (recomendação, search)

**Exemplos de busca:**
```bash
# Gitee (GitHub chinês)
obscura fetch "https://gitee.com/explore/recommend?sort=fork" --dump markdown

# CSDN (artigos tech)
obscura fetch "https://www.csdn.net/?ref=logo" --dump markdown

# Zhihu (Stack Overflow chinês)
obscura fetch "https://www.zhihu.com/topic/19776749" --dump markdown

# Baidu Research Papers
obscura fetch "https://research.baidu.com/" --dump markdown
```

---

## 2. Execução em Paralelo (Múltiplos Agentes)

### Workflow: hunt-global-parallel.js

```javascript
// Executa 5 agentes em paralelo
const results = await parallel([
  agent("scrape huggingface"),    // Agent 1
  agent("scrape github"),          // Agent 2
  agent("scrape japan"),           // Agent 3
  agent("scrape korea"),           // Agent 4
  agent("scrape china")            // Agent 5 — NOVO
])

// Depois: análise paralela
const analysis = await parallel([
  agent("analyze frameworks"),     // Comparar frameworks por região
  agent("analyze code patterns")   // Extrair padrões de código
])
```

**Vantagem:** 5 scraping + 2 análises rodam em paralelo  
**Tempo total:** ~30s (vs 150s sequencial)

---

## 3. Padrões de Código Esperados

### PyTorch (Universal)
```python
import torch
import torch.nn as nn
from torch.optim import Adam

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 5)
    
    def forward(self, x):
        return self.linear(x)
```

### TensorFlow (Produção)
```python
import tensorflow as tf
from tensorflow.keras import layers

model = tf.keras.Sequential([
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(10, activation='softmax')
])
```

### MindSpore (Huawei/China)
```python
import mindspore as ms
from mindspore import nn

class Model(nn.Cell):
    def __init__(self):
        super().__init__()
        self.dense = nn.Dense(128, 10)
    
    def construct(self, x):
        return self.dense(x)
```

### PaddlePaddle (Baidu/China)
```python
import paddle
import paddle.nn as nn

class Model(nn.Layer):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(128, 10)
    
    def forward(self, x):
        return self.linear(x)
```

---

## 4. Análise por Região

| Região | Frameworks | Linguagem | Especialidade |
|--------|-----------|-----------|---------------|
| **Global** | PyTorch, TF, JAX | English | General ML |
| **Japão** | PyTorch, TF, JAX | 日本語 | Robotics, Manufacturing |
| **Coréia** | PyTorch, TF | 한국어 | Mobile, NLP-KO |
| **China** | MindSpore, PaddlePaddle, PyTorch | 中文 | E-commerce, CV, NLP-ZH |

---

## 5. Integrando com Manta

### Manta 06 (Modelagem) — Geração de Código
```python
# skill: gerar-codigo-baseado-regiao.py
def gerar_modelo(regiao: str, task: str, framework: str = None):
    """Gerar código baseado em padrões globais."""
    
    # 1. Buscar padrão no RAG (rag_chunks com código por região)
    padrao = await rag.search(f"{regiao}:{task}:{framework}")
    
    # 2. Adaptar para projeto do usuário
    codigo = adaptar_padrao(padrao, usuario_specs)
    
    # 3. Validar contra best practices da região
    validar_codigo(codigo, regiao)
    
    return codigo

# Uso:
# codigo = await gerar_modelo(
#     regiao="china",
#     task="classificacao",
#     framework="paddlepaddle"
# )
```

### Manta 15 (Advisory) — Comparação Global
```python
# skill: advisory-global.py
async def comparar_com_concorrentes(projeto):
    """Comparar projeto com práticas em JP, KR, CN."""
    
    analises = {
        "japan": await analisar_praticas("japan", projeto),
        "korea": await analisar_praticas("korea", projeto),
        "china": await analisar_praticas("china", projeto),
    }
    
    parecer = gerar_parecer(analises)
    return parecer
```

---

## 6. Implementação

### Step 1: Executar Workflow Paralelo
```bash
# Dispara 5 agentes + 2 análises em paralelo
node workflows/hunt-global-parallel.js
```

### Step 2: Indexar em Supabase
```python
# RAG collection: "codigo_global"
await supabase.table("rag_chunks").insert({
    "source": "github-pytorch-example",
    "codigo": "import torch; ...",
    "regiao": "global",
    "framework": "pytorch",
    "tipo": "training-loop"
})
```

### Step 3: Usar em Skills
```python
# Em mk-manta ou outra skill
padrao = await rag.search("pytorch training loop")
codigo_customizado = adaptar(padrao, projeto_usuario)
```

---

## 7. Recursos

- **Workflow:** `workflows/hunt-global-parallel.js`
- **Script:** `examples/hunt-codigos-clients-worldwide.py`
- **MCP:** Obscura (`OBSCURA-INTEGRATION.md`)
- **Docs:** GitHub Awesome Lists
  - https://github.com/awesome-kor/awesome-korean-nlp
  - https://github.com/topics/chinese
  - https://github.com/topics/japanese

---

**Criado:** 2026-07-23  
**Atualizado:** 2026-07-23  
**Próxima:** Executar workflow paralelo em ambiente com internet
