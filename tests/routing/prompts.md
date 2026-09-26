# Routing smoke tests — Manta Maestro v4.2

Prompts amostrais para validar que o Maestro (Manta 00) despacha cada
consulta ao agente vertical correto. Cada bloco declara o prompt
esperado e o **agente-alvo**; um teste passa se o Maestro roteia ao
agente listado sem passar por horizontais indevidos.

Rodar via:
```
python scripts/test_routing.py tests/routing/prompts.md
```
(script a ser criado no repo operacional do Maestro; por ora este
arquivo serve como fonte manual para QA humano.)

---

## S6 — Portos

- [ ] `Preciso de um preliminar de dragagem para o terminal de contêineres do Porto do Itaqui.` → **agente-portos**
- [ ] `Como dimensiono a defensa de um berço para navio Panamax?` → **agente-portos**
- [ ] `A ANTAQ pede um cronograma de arrendamento para o TUP; ajuda?` → **agente-portos**
- [ ] `Qual PIANC bulletin cobre projeto de quebra-mar em enrocamento?` → **agente-portos**
- [ ] `Estamos com calado insuficiente no canal — preciso de plano de dragagem.` → **agente-portos**

## S7 — Aeroportos

- [ ] `Quero dimensionar a pista de pouso do aeroporto regional (código 3C).` → **agente-aeroportos**
- [ ] `Qual RBAC cobre projeto de pátio de aeronaves?` → **agente-aeroportos**
- [ ] `Preciso do PCN da pista para operação de A320neo.` → **agente-aeroportos**
- [ ] `Como projeto o balizamento CAT II para operação noturna?` → **agente-aeroportos**
- [ ] `ICAO Annex 14 permite offset lateral de RWY na minha configuração?` → **agente-aeroportos**

## S8 — Saneamento (prioridade AySA)

- [ ] `Preciso projetar uma ETA de ciclo completo para 200 mil hab.` → **agente-saneamento**
- [ ] `Como calculo golpe de aríete na adutora de 800mm?` → **agente-saneamento**
- [ ] `AySA me pediu um estudo de reabilitação da Planta Norte.` → **agente-saneamento**
- [ ] `Qual método de dimensionamento de rede de esgoto pela NBR 9649?` → **agente-saneamento**
- [ ] `Estou preparando o PMSB do município; por onde começar?` → **agente-saneamento**
- [ ] `A Lei 14.026 exige quais métricas do SNIS para universalização?` → **agente-saneamento**

## S9 — Energia (prioridade transmissão)

- [ ] `Estamos avaliando um leilão de transmissão da ANEEL em 2027, pode me ajudar?` → **agente-energia**
- [ ] `Preciso da RAP referencial para uma LT de 500kV, 250km.` → **agente-energia**
- [ ] `Como faço o estudo de ampacidade para condutor ACSR 636 MCM?` → **agente-energia**
- [ ] `Qual arranjo de subestação recomenda para 230kV?` → **agente-energia**
- [ ] `ONS pede um estudo de fluxo — pode revisar minha modelagem?` → **agente-energia**
- [ ] `EPE liberou o R3 do projeto; preciso conferir contra o edital.` → **agente-energia**

## S10 — Barragens

- [ ] `Preciso projetar uma barragem CFRD de 80m de altura.` → **agente-barragens**
- [ ] `Como faço dam breach analysis pós-Brumadinho?` → **agente-barragens**
- [ ] `Qual bulletin ICOLD cobre rejeitos filtrados (dry stack)?` → **agente-barragens**
- [ ] `PNSB exige quais entregáveis para revisão periódica?` → **agente-barragens**
- [ ] `Tenho uma barragem TSF a montante que precisa descaracterizar.` → **agente-barragens**
- [ ] `O SIGBM da ANM me alertou sobre categoria de risco — o que faço?` → **agente-barragens**

## MOT — Faseamento de Tráfego (extensão S1/S2)

- [ ] `"preciso da sequência executiva de fases para o trevo em obra do km 282"` → **agente-infraestrutura S1** + handoff **mot-orquestrador**
- [ ] `"como fica o desvio de tráfego da duplicação atravessando a interseção existente?"` → **agente-infraestrutura S1** + handoff **mot-orquestrador**
- [ ] `"faseamento da rotatória durante a obra do viaduto"` → **agente-infraestrutura S2** + handoff **mot-orquestrador**
- [ ] `"quais as etapas de manutenção de tráfego para o trevo em desnível durante a execução da OAE?"` → **agente-infraestrutura S2** + handoff **mot-orquestrador**
- [ ] `"monta o plano de fases (TMP) para o desvio de tráfego no trevo enquanto a obra avança"` → **agente-infraestrutura S1** + handoff **mot-orquestrador**
- [ ] `"sequência de faseamento do tráfego na interseção com a marginal durante a duplicação"` → **agente-infraestrutura S1** + handoff **mot-orquestrador**

### Casos ambíguos MOT

- [ ] `"qual sinalização usar no desvio provisório da rotatória?"` → **sinalizacao-provisorios-rodovias** (pedido isolado de dispositivo/placa de UMA fase já decidida, não pede sequência/fases — não deve acionar MOT)
- [ ] `"preciso das fases do desvio de tráfego do trevo, e depois também das placas de cada fase"` → **agente-infraestrutura S1/S2** + handoff **mot-orquestrador** (define as fases) → em seguida **sinalizacao-provisorios-rodovias** (desenha os dispositivos de cada fase já decidida); caso composto, roteamento inicial para MOT por mencionar "fases"

## Verificações de não-regressão (S1-S4 mantidos)

- [ ] `Preciso do orçamento SICRO para pavimento CBUQ 5cm.` → **agente-infraestrutura S1** (Rodovias) + handoff **manta-05**
- [ ] `Como projeto uma viga PRP para viaduto sobre a rodovia?` → **agente-infraestrutura S2** (OAE)
- [ ] `Qual AMV recomenda para pátio ferroviário?` → **agente-infraestrutura S3** (Ferrovia)
- [ ] `Vou escavar uma estação de metrô pelo método NATM.` → **agente-infraestrutura S4** (Metrô)

## Casos ambíguos / desafiadores

Estes prompts têm palavras-chave de mais de um segmento; o Maestro
deve escolher o **mais específico** (não necessariamente o primeiro
match). Anotar o dispatch efetivo em revisão manual.

- [ ] `Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE.`
    - Esperado: dispatch para **agente-barragens** (ou **agente-energia**?) com handoff explícito para o outro. Definir política MN.
- [ ] `A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro.`
    - Esperado: **agente-saneamento** primário + handoff **agente-energia**.
- [ ] `Porto arrendado no Amazonas com pátio + pista para carga aérea auxiliar.`
    - Esperado: **agente-portos** primário + handoff **agente-aeroportos**.
- [ ] `Adutora atravessa uma barragem de rejeitos existente.`
    - Esperado: **agente-saneamento** com consulta técnica ao **agente-barragens**.
