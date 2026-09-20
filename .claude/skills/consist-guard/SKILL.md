---
name: consist-guard
description: Valida a consistencia interna de um documento HTML de tese, laudo ou parecer Manta antes de fechar ou enviar. Verifica integridade estrutural (tags balanceadas e fecho correto do HTML), consistencia numerica (quantum, subtotais, imposto), logica e ordem de datas, numeracao sequencial de capitulos, pendencias marcadas (a cargar, a confirmar, numero en blanco) e rastreabilidade (presenca de fontes citadas, ex. SharePoint). Use sempre que o usuario pedir "rodar consist-guard", "revisar consistencia", "validar a tese", "checar o documento", ou ao fechar e enviar um documento tecnico Manta.
---

# consist-guard — Revisao de consistencia de documentos Manta

## Quando usar
Sempre que for fechar, atualizar ou enviar um documento HTML tecnico da Manta
(tese de reequilibrio, laudo, parecer), ou quando o usuario pedir para validar
a consistencia, logica ou rastreabilidade do documento.

## Antes do primeiro uso — preencher o CONFIG
Este script **nao vem com nenhum valor de negocio pre-preenchido**. O bloco
CONFIG no topo de `consist_guard.py` chega vazio (`None` / `[]`) de proposito
— e generico, nao amarrado a nenhum caso ou cliente especifico. Antes de
rodar contra um documento real, preencha com os valores canonicos DESSE
documento:
- `EXPECT`: quantum (total, subtotal, categorias), datas-chave na ordem
  esperada, numero de capitulos.
- `FORBIDDEN`: strings obsoletas que nao devem mais aparecer.
- `DIVERGENCIAS_CITADAS`: valores/citacoes ja identificados como divergencia
  a resolver antes de fechar.
- `FONTES_RASTREAVEIS`: fontes-chave que o documento deve citar (normas,
  pareceres, atas, SharePoint etc.).

Qualquer campo deixado vazio faz o script pular aquele check (reporta
"nao configurado") em vez de falhar — assim ele roda sem erro mesmo antes
de voce configurar tudo, so nao valida o que nao foi preenchido.

## Como executar
1. Identifique o arquivo HTML alvo (ex.: a ultima versao da tese, tese-vNNN.html).
2. Rode no terminal:

       python consist_guard.py CAMINHO_DO_ARQUIVO.html

   Sem argumento, o script procura a ultima versao tese-v em ./_deploy
   (ou no diretorio corrente).
3. Leia o relatorio (linhas ERRO e FLAG) e o veredito
   (APROVADO / REVISAR / REPROVADO).

## O que checa
- Estrutura: tags div, section e table balanceadas; fecho correto do HTML.
- Valores obsoletos: strings que nao devem mais aparecer (configuraveis).
- Quantum: A + B + C + D, subtotal, total com imposto (no bloco CONFIG).
- Datas: presenca e ordem cronologica das datas-chave.
- Numeracao: capitulos sequenciais (sem lacunas).
- Pendencias: "a cargar", "a confirmar", numero de EC en blanco, divergencias.
- Rastreabilidade: fontes-chave referenciadas.

## Importante
- Os valores canonicos ficam no bloco CONFIG no topo de consist_guard.py.
  Atualize o CONFIG a cada novo documento/caso (novo quantum, novas datas,
  novo numero de capitulos, novas fontes exigidas), para que a validacao
  reflita a verdade vigente DESSE documento especifico.
- Complementa as skills revisao (rele fontes), dedup-guard (duplicacao de
  informacao dentro do artefato) e aluci-guard (anti-alucinacao). Esta foca
  na consistencia interna do documento contra os valores que voce configurou.
