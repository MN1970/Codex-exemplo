# Ficha Técnica condensada + regra de não citar "Manta Mestro" — 2026

**Status:** ✅ **PUBLICADO em produção** — `04_IA/Manta-Maestro/02-atividades/
A1-proposta/SKILL.md` atualizado de **3.3.4 para 3.3.5** via `SharePoint_Manta`
MCP, publicação confirmada por releitura (18.964 bytes, tamanho idêntico ao
arquivo local).

## O que mudou

### 1. Ficha Técnica condensada em uma linha só

Na variante "Tipo A / Concessão de Infraestrutura de Grande Porte", o bloco
"Controle de Revisão + Ficha Técnica" descrevia duas ocorrências no mesmo
documento:

- **No topo** (antes da Seção 1): o que mudou da revisão anterior.
- **No fechamento**: ficha técnica compacta (cliente, projeto, documento,
  código, versão, data, classificação, responsável, contato, fontes
  primárias, repositório).

A pedido do usuário, isso foi condensado em **uma única linha**, mantida
apenas no fechamento do documento (a ocorrência do topo, antes da Seção 1,
foi removida). O campo "Versão" da linha única já embute o que mudou da
revisão anterior, em até uma frase:

```
Cliente · Projeto · Documento · Código · Versão: [REV atual]
(anterior: [REV-1] -- o que mudou, 1 frase) · Data · Classificação ·
Responsável · Contato · Fontes primárias · Repositório
```

### 2. Proposta ao cliente não cita "Manta Mestro"

Nova cláusula na "Seção IA" (Seção 9 — Benefícios) determinando que o texto
entregue ao cliente:

- **Nunca menciona** "Manta Mestro" nem a arquitetura interna do sistema de
  IA (agentes por segmento, orquestração, códigos internos "Manta NN").
- **Foca na experiência e maturidade técnica da equipe**, apoiada de forma
  genérica por "ferramentas de Inteligência Artificial da Manta Associados"
  — sem detalhar o mecanismo interno.
- Nomenclatura interna (Manta Mestro, Manta 00–25 etc.) fica reservada a uso
  exclusivamente interno/operacional, nunca client-facing.

Exemplo do tipo de substituição pretendida:

| Antes (não usar em proposta) | Depois (client-facing) |
|---|---|
| "Esta proposta foi elaborada com o apoio do Manta Mestro, nosso ecossistema de agentes de IA especializados por segmento de infraestrutura..." | "Esta proposta reflete a experiência e a maturidade técnica da nossa equipe, apoiada por ferramentas de inteligência artificial da Manta Associados." |

## Processo

A pedido do usuário. Dado o texto fonte da solicitação estar bastante
truncado/ambíguo, a interpretação foi confirmada em linguagem simples via
pergunta direta antes de qualquer edição na skill real de produção — só se
procedeu à escrita após confirmação explícita dos dois pontos acima.

## Nota técnica sobre a publicação

O upload para o SharePoint via `SharePoint_Manta` MCP só aceita conteúdo em
base64 inline (o parâmetro `local_path` não funciona neste ambiente — o
servidor MCP roda em um container diferente do shell desta sessão, sem
sistema de arquivos compartilhado). Para uma string base64 desta extensão
(~25.300 caracteres), a transcrição direta se mostrou não confiável (duas
tentativas produziram corrupção silenciosa). A publicação final só ocorreu
após reconstruir o base64 em blocos verificados (~4.000 caracteres cada,
conferidos byte a byte contra o arquivo de origem) e confirmar via hash
SHA-256 que a reconstrução batia exatamente com o arquivo original antes do
upload.
