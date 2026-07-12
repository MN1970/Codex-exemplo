# prompts/intake-ambiguo.md — manta-maestro

Cinco exemplos concretos de queries ambíguas do usuário e como o
Maestro deve resolvê-las via Q1 do intake, ordem de fallback §6.4, ou
consulta cruzada.

Formato:
- **Query**: o que o usuário digitou
- **Q1 disparado**: qual regra determinística casou (ou LLM-router)
- **Resultado**: qual agente ganhou a delegação

---

## Exemplo 1 — palavra sobreposta S12 (túneis) vs S2 (OAE)

**Query**: "Preciso projetar um túnel rodoviário de 800 m sob a Serra
do Cafezal, para a rodovia estadual SP-125."

**Q1 disparado**: casam DOIS segmentos —
- S1 Rodovias: "rodovia", "SP-125"
- S12 Túneis: "túnel", "rodoviário"

Em empate, o índice de menor S geralmente ganharia (S1), mas o Maestro
aplica a heurística de escopo: "quem é o entregável dominante?" — a
Serra do Cafezal exige NATM/TBM, o principal engenheiro é o tunelista;
a rodovia é o contexto.

**Resultado**: delegou para **S12 (agente-tuneis)** como primário; S1
como ⇢ (consulta cruzada) para geometria rodoviária no portal.

---

## Exemplo 2 — código Codex vs código operacional Maestro

**Query**: "Como está o roteiro do S5? preciso rever o SKILL."

**Q1 disparado**: literal "S5" — mas AMBÍGUO entre:
- Codex: `03-S5` = Túneis
- Operacional: `S5` = Imobiliário

O Maestro consulta a §3.1 do próprio SKILL.md e vê a tabela de
reconciliação. Sem contexto adicional, pergunta ao usuário
("estás perguntando do S5 do Codex (túneis) ou do S5 operacional
(imobiliário)?").

**Resultado**: delegou para **Q1 humano** (§6.4 fallback nível 3).

---

## Exemplo 3 — palavra AySA aciona prioridade absoluta

**Query**: "Preciso rever a EEAB proposta pelo escritório de Buenos Aires
antes de mandar para a AySA."

**Q1 disparado**: "AySA" + "EEAB" — S9 tem metadata PRIORIDADE AySA.

Mesmo que "escritório" pudesse sugerir S6 (edificações), a menção
"AySA" trava o roteamento em S9 sem ambiguidade — é convenção Manta.

**Resultado**: delegou para **S9 (agente-saneamento)**.

---

## Exemplo 4 — "concessão" isolada não decide segmento

**Query**: "Estou modelando VPL/TIR de uma concessão de 30 anos."

**Q1 disparado**: NENHUM segmento casa (concessão sozinho é
transversal — pode ser S1, S7, S8, S10). Casa Atividade A4 (VPL, TIR).

Fallback §6.4:
1. F1.c Learned Router — MLP retorna S10 com confidence 0.62 (< 0.85, descartado).
2. F1.b RAG hybrid — top-1 é `ake:concessao-transmissao-2024` (S10).
3. Se ainda ambíguo, Q1 humano: "qual segmento — porto, rodovia,
   saneamento, transmissão?".

**Resultado**: delegou para **A4 (agente-advisory)** como orquestrador
temporário; ele faz o Q1 do segmento antes de rodar VPL/TIR.

---

## Exemplo 5 — palavra genérica "pilar" ambígua entre S2 e S6

**Query**: "Preciso do quantitativo de aço + concreto dos pilares."

**Q1 disparado**: "pilar" + "quantitativo" + "aço/concreto" — ambíguo:
- S2 OAE (pilares de ponte) → casa "aço, concreto"
- S6 Edificações (pilares de edifício) → casa "aço, concreto"

Nenhum termo de contexto (não há "viga longarina", "ponte", "torre",
"laje protendida"). Fallback F1.c retorna S6 com confidence 0.71.

**Resultado**: fallback rebaixa e vai a **Q1 humano**: "pilares de
ponte/viaduto (OAE) ou pilares de edifício/galpão (edificação)?"
