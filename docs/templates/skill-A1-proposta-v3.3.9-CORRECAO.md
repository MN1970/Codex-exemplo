<!--
NOTA DESTE REPOSITÓRIO (não faz parte da skill real): este arquivo é o
conteúdo COMPLETO E PRONTO PARA UPLOAD da correção v3.3.9 da skill real
`A1-proposta` (SharePoint, 04_IA/Manta-Maestro/02-atividades/A1-proposta/
SKILL.md). NÃO foi aplicado ao SharePoint — o modo automático desta
sessão bloqueou a escrita como ação de alto risco em produção. A única
mudança em relação à v3.3.8 real é: (1) bump de versão/frontmatter, (2)
o bracket [v3.3.9: ...] adicionado ao final do parágrafo de changelog,
(3) uma nota de correção anexada ao final do bullet "Template canônico"
em "Template e exemplares -- Tipo A / PRC". Nenhum outro conteúdo foi
alterado. Ver docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md, seção
"Autocorreção -- MNT-2026-COM-1301 (2026-09-11)", para o achado
completo e o passo a passo de aplicação.
-->

---
name: atividade-A1-proposta
codigo: A1
camada: L1.7
tipo: atividade
version: 3.3.9
updated: 2026-09-11
supersedes: 3.3.8 (2026-09-10)
---

# A1 Proposta tecnica-economica -- Metodo

Racional metodologico para elaboracao de propostas tecnicas e economicas em resposta a editais, RFP, EVTEA, licitacoes, e propostas comerciais diretas a investidores/clientes. Absorve o antigo agente-bd. [Historico v3.3.0-v3.3.5: ver changelog completo no CLAUDE.md do repositorio Codex-exemplo.] [v3.3.6: tabela tarifaria remove o grupo dedicado "Orcamentista"; nota 1 generalizada -- qualquer area (engenharia, planejamento, software, orcamento etc.) se enquadra nos niveis existentes (Diretoria/Coordenacao/Especialista/Engenharia/Analista) por senioridade, sem Funcao dedicada por area.] [v3.3.7: removida da secao "Variante -- Tipo A / Concessao de Infraestrutura de Grande Porte" a alegacao de que os 5 blocos foram "validados contra a proposta real MNT-2026-COM-1183_D" -- essa revisao nao existe no SharePoint (busca por MNT-2026-COM-1183 so retorna MNT-2026-COM-1183_C_3); a citacao entrou via fusao de pacote externo nunca conferido contra fonte primaria. Achado documentado no repositorio Codex-exemplo. Estrutura dos 5 blocos mantida sem alteracao; apenas a alegacao de validacao foi removida, sem substitui-la por nova citacao nao verificada.] [v3.3.8: adicionado template canonico Tipo A/PRC (`template-ptc-tipo-a-v1.html`, ver "Template e exemplares" abaixo) -- capa, sumario, resumo executivo e as 18 secoes + Anexo I com as clausulas padrao ja escritas por extenso.] [v3.3.9: correcao -- a v3.3.8 alegava que o template foi "conferido... contra a proposta real MNT-2026-COM-1301 (Concessionaria Rota da Liberdade, Lote 07)"; busca exaustiva no SharePoint (nome de arquivo, conteudo indexado, pasta do cliente 27_CLIENTE_VIA_LIBERDADE) nao encontrou nenhum documento com essa referencia -- recorrencia do mesmo padrao de fabricacao ja corrigido na v3.3.7 (MNT-2026-COM-1183_D), desta vez introduzida pela propria sessao que publicou o template. A alegacao de verificacao foi removida; o template em si permanece publicado e verificado por leitura pos-upload (fato distinto da alegacao de validacao removida). Achado e correcao documentados no repositorio Codex-exemplo.]

## Pipeline
```
qualify   -> qualificacao da oportunidade, GO/NO-GO
escopo    -> definicao do escopo tecnico
pricing   -> precificacao (custo + BDI + margem)
narrativa -> tese comercial, diferenciais Manta
riscos    -> matriz probabilidade x impacto
entrega   -> DOCX + PPTX + planilha comercial + carta de encaminhamento
```

## Tipos de proposta
- **Tipo A (PTC)** -- Manta vende consultoria/gestao ao cliente. 17 casos indexados. **Template canonico disponivel** (ver abaixo).
- **Tipo B (PRT)** -- Manta elabora a proposta tecnica em nome do cliente para licitacao/concessao ou concorrencia de obra. 8 casos indexados. **Template canonico disponivel** (ver abaixo).
- **PRC** -- Proposta apenas comercial (so preco/condicoes, sem escopo tecnico detalhado) -- usar a mesma numeracao e clausulas desta skill, suprimindo as secoes de escopo/metodologia.

## Convencao de numeracao e classificacao [v3.3.0]
- **ID:** `MNT-YYYY-COM-NNNN` (ex.: MNT-2026-COM-1201).
- **Sufixo de revisao:** `REV_00`, `REV_01`... para o padrao geral (Tipo A/PRC). Para propostas de concessao em resposta a processo regulatorio publico (audiencia publica, edital), usar sufixo de letra (`_A`, `_B`, `_C`...) acompanhando o calendario do processo, nao um ciclo de revisao interno -- registrar sempre um "Controle de Revisao" no topo do documento explicando o que mudou da revisao anterior.
- **Classificacao padrao:** Confidencial.

## Identidade institucional Manta (nucleo BD) [novo v3.2.0]

Ao atuar em A1, o agente fala **como** e **pela** Manta Associados. Nucleo duravel
(comportamento -- o acervo vivo fica em D8-institucional-manta, consultado via F1.b):

- **Empresa:** Manta Associados -- "Inteligencia de Engenharia". Visao integral
  (comercial, orcamento, engenharia e contratual) em investimentos, pre-construcao,
  construcao e operacao de ativos.
- **Posicionamento oficial:** "Podemos fazer todos os servicos que uma construtora e
  os investidores executam, mas nao construimos ou investimos."
- **Linhas de servico:** estruturacao de projetos e propostas tecnico-comerciais;
  estimativas de custo (SICRO/DER); business plans e modelagem financeira; avaliacao
  de construtibilidade; gestao de contratos (CM at Risk, DB, EPC); gestao de risco e
  seguros; gestao integral de obra; claims e reequilibrio.
- **Diferenciais a citar (ver D8-institucional-manta/diferenciais.md):** isencao
  estrutural (nao constroi/nao investe); plataforma proprietaria MantAI; 11 IAs
  Matrizes + agentes especializados; escala internacional (50 paises); pipeline de
  concessoes acompanhado.
- **Tom:** portugues tecnico, impessoal, sem adjetivos de efeito. Dados sustentam o
  argumento, nao a retorica.
- **Track record / cases:** carregar de D8-institucional-manta + `03-exemplares/bd/`
  (indice de propostas) via F1.b, filtrado por `nda_ceiling`. NAO citar case sem
  lastro (R2).

## Dados fixos da proponente [v3.3.0]
```
Razao Social: Manta Consultoria Ltda.
CNPJ: 56.063.961/0001-08
Endereco: Av. Marcos Penteado de Ulhoa Rodrigues, 939, andar 8, sala 850,
          Torre I - Edif. Jacaranda, 06.460-040, Tambore, Barueri - SP
Banco: Santander | Agencia: 3630 | CC: 13008405-3
Contato Comercial: Willer Monteiro | (31) 98757-2197 | comercial@mantaassociados.com
```

## Excecao R1 para A1 (proposta nomeada) [novo v3.2.0]

R1 (sanitizacao -- nome de concessionaria vira [CONCESS.]) aplica-se a todos os
agentes, MAS A1 e excecao controlada: uma proposta comercial e, por natureza,
**enderecada e assinada** a um cliente nomeado.

- **Permitido em A1:** nomear o cliente-destinatario e a Manta no cabecalho, carta de
  encaminhamento, capa e identificacao do documento. Nomes de lideres/socios Manta
  (ver D8-institucional-manta/equipe-chave.md) tambem nao sao sanitizados -- sao
  profissionais Manta, nao terceiros.
- **Mantem R1:** exemplares de terceiros usados como few-shot/RAG continuam
  sanitizados ([CONCESS.]); dados sob NDA respeitam `nda_ceiling`; nome de terceiros
  nao-partes (concorrentes, outros clientes) permanece sanitizado salvo autorizacao
  explicita.
- **Registro:** toda proposta nomeada registra em TRACE a autorizacao de nomeacao (R5).

## Tabela tarifaria padrao [v3.3.3, editada v3.3.6] (base 176h/mes)

Consolidacao "revB" (`Tarifas_Consolidadas_Manta_revB.xlsx`, gerada a pedido de
Willer Monteiro/Diretoria de IA + PMO, 09/09/2026): maior valor por nivel entre as
tabelas de origem, exceto Diretoria (definida manualmente nesta rodada).

| Funcao | Nivel | Tarifa (R$/h) | Tarifa (R$/mes, 176h) | Hora extra (1,5x, R$/h) |
|---|---|---|---|---|
| Diretoria | Socio Diretor / Consultor Internacional | R$ 900,00 | R$ 158.400,00 | R$ 1.350,00 |
| Diretoria | Diretor de Infraestrutura | R$ 700,00 | R$ 123.200,00 | R$ 1.050,00 |
| Coordenacao | Master | R$ 550,00 | R$ 96.800,00 | R$ 825,00 |
| Coordenacao | Senior | R$ 522,50 | R$ 91.960,00 | R$ 783,75 |
| Coordenacao | Pleno | R$ 496,38 | R$ 87.362,88 | R$ 744,57 |
| Especialista | Master | R$ 500,00 | R$ 88.000,00 | R$ 750,00 |
| Especialista | Senior | R$ 475,00 | R$ 83.600,00 | R$ 712,50 |
| Especialista | Pleno | R$ 470,00 | R$ 82.720,00 | R$ 705,00 |
| Especialista | Junior | R$ 470,00 | R$ 82.720,00 | R$ 705,00 |
| Engenharia | Master | R$ 561,00 | R$ 98.736,00 | R$ 841,50 |
| Engenharia | Senior | R$ 532,95 | R$ 93.799,20 | R$ 799,43 |
| Engenharia | Pleno | R$ 506,30 | R$ 89.108,80 | R$ 759,45 |
| Engenharia | Junior | R$ 480,99 | R$ 84.654,24 | R$ 721,49 |
| Analista (Engenharia / Software) | Senior | R$ 285,00 | R$ 50.160,00 | R$ 427,50 |
| Analista (Engenharia / Software) | Pleno | R$ 176,00 | R$ 30.976,00 | R$ 264,00 |
| Analista (Engenharia / Software) | Junior | R$ 135,38 | R$ 23.826,88 | R$ 203,07 |
| Estagio | Estagiario | R$ 80,00 | R$ 14.080,00 | R$ 120,00 |

Notas (fonte: ficha tecnica da revB, nota 1 revisada em v3.3.6):
1. **Enquadramento por maturidade, nao por area de atuacao [v3.3.6]:** profissionais
   de qualquer area (engenharia, planejamento, software/TI, orcamento, entre outras)
   sao remunerados enquadrando-se na Funcao e no Nivel da tabela acima (Diretoria,
   Coordenacao, Especialista, Engenharia ou Analista) que correspondam a sua
   maturidade/senioridade real -- nao ha Funcao dedicada por area de atuacao. Ex.: um
   orcamentista senior usa a tarifa de Engenharia Senior ou Especialista Senior,
   conforme a complexidade da atividade; um planejador pleno usa Engenharia Pleno ou
   Especialista Pleno. O grupo "Orcamentista", antes listado como Funcao propria, foi
   removido desta tabela por este motivo.
2. Base 176 horas normais/mes; valor-mes = tarifa x 176. Hora extra = 1,50x a hora
   normal, aplicavel a todas as funcoes (coluna acima).
3. Valores ja incluem encargos, overhead e margem. Sem custos adicionais exceto
   deslocamentos (ver clausulas abaixo).
4. "Projetista Senior" e "Tecnico" (perfis de versoes anteriores desta tabela) nao
   tem Funcao correspondente nesta matriz -- ate reconciliacao, usar o nivel
   "Especialista" mais proximo por senioridade.

## Estrutura de secoes -- Tipo A / PRC (18 secoes + Anexo) [v3.3.0]

| # | Secao | Conteudo |
|---|---|---|
| 1 | Introducao | Apresentacao da Manta, contexto do projeto, historico de relacionamento |
| 2 | Objeto | Descricao formal do que sera contratado |
| 3 | Escopo dos Servicos | Frentes de atuacao detalhadas (3.1, 3.2, 3.3...) |
| 4 | Documentacao a ser Disponibilizada | O que o cliente precisa fornecer |
| 5 | Entregaveis | Lista de produtos (relatorios, dashboards, pareceres) |
| 6 | Fora do Escopo | Exclusoes explicitas |
| 7 | Prazo | Duracao, fases, cronograma orientativo |
| 8 | Dos Casos Omissos | Tratamento de situacoes imprevistas |
| 9 | Beneficios e Valor | Proposta de valor (conhecimento, independencia, IA, confiabilidade) |
| 10 | Equipe | Modelo de alocacao, perfis, atuacao conjunta |
| 11 | Modalidade Contratual | HH, preco fixo, success fee, hibrida |
| 12 | Preco | Segrega Tarifa (remuneracao fixa por perfil/hora) x Success Fee (contingente, ver clausula "Segregacao Tarifa x Success Fee" abaixo); componentes (equipe, deslocamentos, reembolsaveis -- ver "Deslocamentos e despesas reembolsaveis" abaixo), reajuste, impostos [v3.3.1, v3.3.4] |
| 13 | Medicao e Pagamento | Fluxo mensal (boletim -> aprovacao -> NF -> pagamento); clausula de multa/juros de mora/correcao monetaria por atraso (ver "Atraso de pagamento" abaixo) [v3.3.1] |
| 14 | Nao Aliciamento e Confidencialidade | Clausula de 24 meses, penalidade 10x |
| 15 | Validade da Proposta | 30 dias corridos padrao |
| 16 | Contato Comercial e Dados da Empresa | Ver "Dados fixos da proponente" acima |
| 17 | Limitacao de Responsabilidade | Atuacao consultiva, limite = valor pago |
| 18 | Disclaimer | Confidencialidade, propriedade intelectual, validade |
| Anexo I | Apresentacao da Empresa | Credenciais, projetos, equipe |

Para Tipo B, seguir `template-prt-rodovias-v1.md` (9 blocos canonicos) em vez desta
tabela de 18 secoes.

## Variante -- Tipo A / Concessao de Infraestrutura de Grande Porte [v3.3.0]

Extensao do Tipo A para propostas de avaliacao tecnica, parametrico de CAPEX/OPEX
e gestao integrada em concessoes de infraestrutura de grande porte (rodovias,
ferrovias, portos, aeroportos, saneamento, energia, barragens) -- cliente
investidor/concessionaria avaliando participacao em leilao ou ja concessionaria de
um ativo. Blocos estruturais baseados em pratica de propostas de concessao de
infraestrutura de grande porte -- **pendente de validacao contra uma proposta real
especifica antes de uso em cliente** [correcao v3.3.7: a alegacao anterior de que
os blocos foram "validados contra a proposta real MNT-2026-COM-1183_D" foi
removida por nao corresponder a documento existente no SharePoint]. Nao substitui
a estrutura generica de 18 secoes -- e um perfil dela, com 5 blocos adicionais:

| Bloco | Conteudo | Onde entra |
|---|---|---|
| Dados Oficiais do Empreendimento | Quadro fisico do ativo (extensao, CAPEX, OPEX, prazo, TIR se disponivel) extraido de fonte primaria (edital, PER, audiencia publica, MEF) com rastreabilidade numero-a-numero a tabela/documento de origem | Nova secao 2, antes do Objeto |
| Cenarios de Contratacao | Cenario 1 (escopo-base, preco fixo) + Cenario(s) opcionais (modulo de engenharia de valor, success fee), com clausula "sem acordo, sem success fee" -- adesao ao modulo opcional nunca gera onus se recusada | Dentro da secao 2 (Objeto) |
| Metodo do Parametrico em Etapas | Etapas numeradas (leitura do MEF/edital -> estruturacao do escopo fisico -> aplicacao do banco de custos Manta -> curva ABC -> cenarios e comparacao), com pelo menos 1 exemplo numerico real (desvio de custo vs. tabela oficial, curva ABC por insumo) | Dentro da secao 3 (Escopo) |
| Infraestrutura e Ferramentas Incluidas | Tabela do que esta incluso no preco (plataformas de IA, tokens/mes, AutoCAD, Civil 3D, SharePoint, Office 365) | Nova secao entre 10 (Equipe) e 11 (Modalidade) |
| Ficha Tecnica (linha unica) [v3.3.5] | Uma linha no fechamento: `Cliente · Projeto · Documento · Codigo · Versao: [REV atual] (anterior: [REV-1] -- o que mudou, 1 frase) · Data · Classificacao · Responsavel · Contato · Fontes primarias · Repositorio` | So no fechamento do documento; substitui secoes 15-18 se a variante optar por clausulas finais condensadas |

Nesta variante, as secoes 6, 8, 15, 16, 17 e 18 PODEM ser condensadas em uma unica
secao final "Propriedade Intelectual e Clausulas Finais" em formato de tabela
compacta, seguida da Ficha Tecnica -- opcional, especifico deste perfil. Fora dela,
manter as 18 secoes numeradas individualmente.

## Clausulas padrao (texto reutilizavel) [v3.3.0]

**Secao IA (sempre incluir na secao 9 -- Beneficios):**
> A MANTA integra recursos de Inteligencia Artificial de forma estruturada e
> sistematica as suas atividades tecnicas e analiticas [...] Os recursos de IA
> serao aplicados nos processos de leitura e extracao estruturada de dados,
> identificacao de inconsistencias e divergencias entre registros, cruzamento de
> informacoes entre frentes de atuacao, consolidacao de evidencias e geracao
> assistida de relatorios tecnicos. [...] Todos os produtos gerados com apoio de
> IA passam por revisao e validacao de profissionais senores antes da emissao.

**Nao citar "Manta Mestro" na proposta ao cliente (secao 9) [v3.3.5]:** o texto
entregue ao cliente nunca menciona "Manta Mestro" nem a arquitetura interna do
sistema de IA (agentes por segmento, orquestracao, codigos "Manta NN"). A narrativa
foca na **experiencia e maturidade tecnica da equipe**, apoiada de forma generica
por "ferramentas de Inteligencia Artificial da Manta Associados" (ver Secao IA
acima), sem detalhar o mecanismo interno -- nomenclatura interna e uso exclusivo
operacional, nunca client-facing.

**Deslocamentos e despesas reembolsaveis (secao 12) [v3.3.4]:** regra padrao --
essas despesas sao **sempre por conta do cliente** (reembolsadas integralmente pelo
CLIENTE, nunca absorvidas pela MANTA), com duas modalidades de ressarcimento --
Nota de Debito (valor exato sem impostos) ou Nota Fiscal (recomposicao tributaria,
aliquota 17,50%). Sao expressamente reembolsaveis, mediante comprovacao fiscal e
criterio de razoabilidade:
- Taxis e aplicativos de transporte (Uber e similares);
- Deslocamentos rodoviarios/locais, incluindo trajetos a Jundiai e demais
  localidades do escopo do projeto;
- Passagens (aereas e rodoviarias);
- Traslados;
- Hospedagem (hoteis).

**Segregacao Tarifa x Success Fee (secao 12) [v3.3.1]:** a remuneracao da secao 12
sempre separa duas tabelas: (a) **Tarifa** -- remuneracao fixa por perfil/hora do
escopo-base (ver "Tabela tarifaria padrao" acima); (b) **Success Fee** --
remuneracao contingente, calculada como percentual sobre o criterio de sucesso
definido especificamente em cada proposta (economia de custo, conquista, ou
cumprimento de cronograma). Nunca somar as duas em uma unica linha de preco.

**Exigibilidade do Success Fee (secao 12) [v3.3.1]:** o success fee so se torna
exigivel a partir da **formalizacao documentada** do evento que caracteriza o
sucesso -- nunca de uma percepcao informal de resultado:

| Criterio de sucesso | Evento que torna o success fee exigivel |
|---|---|
| Economia de custo (CAPEX/OPEX) | Formalizacao da aprovacao do orcamento pelo cliente incorporando a economia identificada |
| Conquista (leilao, licitacao, aprovacao regulatoria) | Formalizacao da conquista (homologacao do resultado, assinatura do contrato, publicacao da aprovacao) |
| Cronograma / marco contratual | Formalizacao do marco de cronograma atingido e aprovado pelo cliente |

Em todos os casos: sem a formalizacao do evento-gatilho, nao ha success fee devido
-- a mera expectativa de sucesso nao gera exigibilidade nem vencimento de prazo de
pagamento. Esta clausula complementa (nao substitui) a clausula "sem acordo, sem
success fee" da variante de Concessao de Infraestrutura acima.

**Medicao padrao (secao 13):**

| Etapa | Responsavel | Prazo |
|---|---|---|
| Apresentacao Boletim | MANTA | Ate dia 5 do mes seguinte |
| Aprovacao | CLIENTE | Ate dia 10 |
| Emissao NF | MANTA | Dia 10, apos aprovacao |
| Pagamento | CLIENTE | Ate dia 25, transferencia bancaria |

**Atraso de pagamento (secao 13) [v3.3.1]:** aplicavel tanto a Tarifa quanto ao
Success Fee. Em caso de atraso no pagamento de qualquer fatura alem do prazo de
vencimento acordado, incidem sobre o valor em aberto, sem necessidade de aviso ou
notificacao previa: multa moratoria de 2% sobre o valor da fatura em atraso; juros
de mora de 1% ao mes, pro rata die, desde o vencimento ate o efetivo pagamento;
atualizacao monetaria pelo IPCA (ou indice equivalente pactuado) sobre o saldo
devedor no mesmo periodo. Percentuais de referencia -- ajustaveis por negociacao
especifica com o cliente; revisao juridica recomendada antes do proximo uso real.

**Nao aliciamento (secao 14):** vigencia contrato + 24 meses; penalidade 10x o
valor total da proposta.

## Template e exemplares -- Tipo A / PRC
- **Template canonico:** `02-atividades/A1-proposta/template-ptc-tipo-a-v1.html` -- capa, sumario, resumo executivo (5 cards: Objeto/Escopo/Prazos/Preco/Entregaveis) e as 18 secoes + Anexo I; clausulas fixas (Segregacao Tarifa x Success Fee, Exigibilidade, Deslocamentos, Atraso de pagamento, Nao Aliciamento, Secao IA, tabela tarifaria, dados fixos da proponente) ja escritas por extenso; demais conteudo como orientacao (caixa cinza-italico) a preencher por proposta. Sistema visual canonico aplicado (paleta `03-funcionais/F3-portal/theme`, tipografia serifada em titulos, marca d'agua diagonal, rodape de rastreabilidade). [correcao v3.3.9: a alegacao de que este template foi "conferido contra a proposta real MNT-2026-COM-1301" foi removida -- nao corresponde a documento existente no SharePoint.]
- **Regra de uso:** ao gerar proposta Tipo A/PRC, duplicar este template, preencher as caixas de orientacao com o conteudo do cliente e o rodape de rastreabilidade (cliente/projeto/data/autor/classificacao/trace_id reais, nunca fabricados) antes do envio.

## Template e exemplares -- celula S1.A1 (Tipo B rodovias)
- **Template canonico:** `02-atividades/A1-proposta/template-prt-rodovias-v1.md` -- 9 blocos canonicos, 2 variantes (B1 obra / B2 concessao-CAPEX), PASSO 0 (estrutura imposta pelo edital), checklist de completude.
- **Exemplares reais sanitizados (few-shot RAG):** `06-exemplares/S1.A1/` -- EX-001 (obra, estrutura livre), EX-002 (concessao/CAPEX), EX-003 (obra, estrutura imposta OIR/PIR/RIR/EIR).
- **Indice de corpus:** `03-exemplares/bd/manta_propostas_index.json` v2.0 (25 propostas, campos `celula_sad` e `status_catalogacao`).
- **Regra de uso:** ao gerar proposta Tipo B em S1/S2, carregar o template + 1-2 exemplares da variante correspondente como contexto. Entradas `status_catalogacao: candidata` NAO servem de exemplar (R2).

## Proposta de output canonica
- Tipo: proposta tecnica-comercial
- Formato: DOCX (tecnica) + PPTX (executiva) + XLSX (planilha comercial)
- Estrutura Tipo A: ver tabela de 18 secoes acima (ou a variante de concessao).
- Estrutura Tipo B: seguir template-prt-rodovias-v1 (blocos 1-9; nucleo = plano de ataque 37-45%).
- Paginas estimadas: 30-80 tecnica (Tipo A); 150-350 (Tipo B obra/concessao); 15-25 executiva
- Funcionais: F4 (extrai edital), F1 (analisa), F8 (padrao-manta), F3 (dashboard se estrategica), F2 (grava).

## Rubrica auto-juiz L2
- Recomenda: recomendacao GO/NO-GO explicita
- Compara: 2-3 abordagens de escopo com escolha justificada
- Anticipa: 2 lances a frente (contra-argumentos, negociacao)
- Quantifica: R$ preco firme, dias prazo, % margem
- Ponto cego: risco tecnico/comercial nao obvio
- Tipo B adicional: checklist de completude do template 100% verificado; quantitativos rastreaveis (R2)

## Composicoes tipicas com disciplinas
Depende do segmento -- S1 rodovia usa D01-D14, S4 metro usa D03/D07/D08/D09/D16, S5 imobiliario usa D08/D15/D16/D17.

## Sub-skills L1 chamadas
proposta-tecnica-rod (existente), evtea-extractor, evtea-quantifier, ler-edital, mk-manta, artefato, padrao-manta.

## Propostas de referencia [v3.3.0]
Para adaptar propostas existentes, buscar no corpus indexado em
`03-exemplares/bd/manta_propostas_index.json`. Exemplos historicos conhecidos:
Rodoanel SP, Fernao Dias, Rodoanel Complementar, Linha 13 Jade CPTM, ArLNG YPF,
RENEA (Custo Tecnico), Concessao Rota 2 de Julho (MNT-2026-COM-1183, variante de
concessao acima).

## Ver tambem
[[A3-orcamento]], [[A4-modelagem]], [[F4-extracao]], [[S1-rodovias]], [[D8-institucional-manta]]
