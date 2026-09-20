---
name: dedup-guard
description: Detecta duplicacao e redundancia de informacao DENTRO de um mesmo artefato Manta (HTML tecnico ou dashboard React com abas/telas) — a mesma tabela, bloco de texto ou valor repetido em mais de uma aba/secao sem uma fonte unica de verdade, e o caso mais grave de um mesmo rotulo (ex. "Total", "Prazo") aparecendo com VALORES DIFERENTES em telas diferentes. Ative SEMPRE que o usuario pedir "rodar dedup-guard", "checar duplicacao", "tem informacao repetida?", "revisar redundancia do artefato", "essa tabela ta em dobro", ou ao fechar/exportar qualquer artefato Manta com multiplas abas/telas (dashboard React, HTML com varias secoes, portal). Tambem ative proativamente antes de entregar um artefato que voce mesmo construiu com mais de uma aba/tela, mesmo que o usuario nao peca explicitamente — duplicacao nao percebida e a causa mais comum de dado divergente entre telas.
---

# dedup-guard — Deteccao de duplicacao e redundancia dentro do artefato

## Por que este skill existe

Em artefatos com varias abas/telas (dashboards React, propostas HTML com
secoes, portais), e comum uma tabela ou um valor ser copiado de uma tela
para outra em vez de vir de uma unica fonte. Isso e inofensivo ate alguem
atualizar so uma das copias — a partir dai o artefato passa a mostrar dois
valores diferentes para a "mesma" informacao, e ninguem percebe porque as
duas telas nunca sao vistas lado a lado. Este skill existe para pegar isso
ANTES de entregar, nao depois que o cliente perceber a divergencia.

## Como se relaciona com os outros guardioes Manta

- **consist-guard**: valida UM documento especifico contra valores
  canonicos fixados no seu CONFIG (ex.: o quantum de uma tese de
  reequilibrio). E hardcoded de proposito — serve para garantir que aquele
  documento nao se desviou da verdade vigente daquele caso.
- **context-guardian**: preserva o contexto de uma sessao longa, evitando
  que informacao se perca por compactacao do historico.
- **dedup-guard** (este skill): nao sabe nada sobre o conteudo de negocio
  de nenhum artefato especifico. Olha para QUALQUER HTML/React da Manta e
  procura duplicacao estrutural — o mesmo bloco, tabela ou rotulo:valor
  aparecendo mais de uma vez dentro do artefato. Complementa o consist-guard:
  ele garante que os NUMEROS estao certos; este garante que os numeros nao
  foram copiados e colados em varios lugares sem uma fonte unica.

## Quando usar

- Antes de fechar/exportar um artefato Manta com mais de uma aba/tela.
- Quando o usuario relatar "essa informacao aparece duas vezes", "os totais
  nao batem entre as telas", ou pedir para revisar redundancia.
- Como checagem de rotina ao final de qualquer sessao que gerou um
  artefato HTML/React multi-secao — nao espere o usuario pedir.

## Como executar

1. Identifique o arquivo HTML alvo (o artefato exportado, ou o HTML gerado
   a partir do React antes do build, se disponivel).
2. Rode no terminal:

       python dedup_guard.py CAMINHO_DO_ARQUIVO.html

   Sem argumento, o script usa o `.html` mais recente no diretorio atual.
3. Leia o relatorio (linhas FLAG e ERRO) e o veredito
   (APROVADO / REVISAR / REPROVADO).
4. Corrija por ordem de gravidade: todo ERRO (valores divergentes ou id
   duplicado) e um defeito real, sempre corrigir antes de entregar. Todo
   FLAG e uma redundancia — avalie se vale a pena centralizar a informacao
   numa unica fonte (ex.: uma variavel/state que alimenta as duas telas)
   antes de decidir manter como esta.

## O que checa

1. **Blocos duplicados** — a mesma `<table>` ou `<section>` (texto igual,
   ignorando tags) aparecendo em mais de um lugar do artefato → FLAG.
2. **Blocos quase-identicos** — duas tabelas/secoes de tamanho parecido
   com alta similaridade de texto (>= 90%, configuravel), tipico de
   copiar uma secao para criar uma aba nova e mudar só um numero → FLAG.
3. **Rotulo com valores divergentes** — o mesmo rotulo (ex. "Total:",
   "Prazo contratual:") aparecendo com valores DIFERENTES em pontos
   diferentes do artefato → ERRO (isto e uma inconsistencia real, nao so
   redundancia — os dois numeros nao podem estar certos ao mesmo tempo).
4. **Rotulo repetido com o mesmo valor 3+ vezes** — sintoma de que aquele
   valor deveria vir de uma unica fonte/state em vez de estar escrito em
   varios lugares → FLAG.
5. **IDs de elemento duplicados no HTML** — sintoma comum de copiar uma
   secao inteira para criar uma aba nova sem atualizar os `id`s (quebra
   `getElementById`, navegacao por ancora, e scripts que dependem de id
   unico) → ERRO.

## Importante

- Este script **nao tem valores de negocio fixos** — so thresholds de
  deteccao (tamanho minimo de bloco, limiar de similaridade, numero de
  repeticoes). Funciona em qualquer artefato Manta sem precisar de
  configuracao previa, ao contrario do consist-guard.
- Falso positivo esperado: rotulos genericos de layout (ex. "Ver mais:")
  podem aparecer varias vezes por design (menus, rodapes repetidos por
  aba). Use o bom senso — o alvo real deste skill sao tabelas de dados,
  totais, prazos e outros valores que deveriam ter uma unica fonte de
  verdade dentro do artefato.
- Publicado como plugin proprio no catalogo Manta (mesmo padrao dos
  demais ~60 plugins, cada um com seu proprio backingPluginId) — nao e
  uma secao dentro de consist-guard nem de context-guardian.
