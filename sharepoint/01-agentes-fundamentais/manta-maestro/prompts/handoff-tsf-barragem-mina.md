# prompts/handoff-tsf-barragem-mina.md — manta-maestro

Exemplo detalhado do handoff cross-agent nas fronteiras **S11 Barragens
↔ S13 Mineração** para casos envolvendo Tailings Storage Facility (TSF)
de rejeitos. Combina os cenários #3 e #6 do playbook.

---

## Contexto da fronteira

- **S11 (agente-barragens)** é dono das barragens de rejeitos (TSF).
  Cobre concepção, alteamento, monitoramento, PAE/PAEBM, Lei 12.334/
  14.066, descaracterização.
- **S13 (agente-mineracao)** cobre a mina propriamente dita: cava,
  desmonte, planta de beneficiamento, PDE, LOM. **NÃO cobre TSF** —
  encaminha para S11.
- **A fronteira é sensível**: uma mina produz rejeito → o rejeito vai
  para TSF → S13 planeja a lavra, S11 dimensiona/descaracteriza o TSF.
  Em conflito, S11 lidera (rejeitos = disposto).

---

## Input do usuário

> "Estamos avaliando expansão da mina de ferro em Nova Lima com
> aumento de 8 → 15 Mtpa. A TSF a montante existente atinge o teto de
> outorga em 2027. Preciso de um plano integrado: (a) ampliação de
> lavra para 15 Mtpa, (b) alternativa filtragem + dry stack, (c) plano
> de descaracterização da TSF atual conforme Lei 14.066, (d) impacto
> no cronograma da concessionária."

---

## Fluxo esperado do Maestro

### Fase INTAKE + READ

- Q1 casa `mineração` (S13) + `TSF` + `dry stack` + `Lei 14.066` (S11).
- O Maestro identifica **duplo segmento primário** e pergunta ao
  usuário: "quem lidera a resposta — S11 (rejeitos) ou S13 (mina)?"
- Convenção Manta (§3.1 SKILL.md + Cenário 6 do playbook): **rejeito
  disposto = S11 lidera; mina propriamente dita = S13 consulta S11**.
- Aqui há duas coisas simultâneas: expansão de mina (S13) E
  descaracterização de TSF (S11). O Maestro opta por dividir em
  entregável, um por líder.

### Fase PLAN — DAG proposto

```
INTAKE / READ (fontes: plano de lavra atual, projeto TSF, licença ANM)

┌─── S13 (agente-mineracao) LIDERA (a) expansão de lavra:
│    ├── D03 Geotecnia (talude de cava a 15 Mtpa)
│    ├── D05 Terraplenagem (desmonte + transporte)
│    ├── A5 Cronograma de rampa
│    └── ⇢ S11 para validar continuidade da produção de rejeito
│         (limite de outorga em 2027)
│
├─── S11 (agente-barragens) LIDERA (c) descaracterização TSF:
│    ├── D03 Geotecnia (estabilidade pós-desativação)
│    ├── D07 Hidrologia (revisão do vertedouro)
│    ├── A6 Contratual (compliance ANM Res 95)
│    ├── KEs acadêmicos (Mendes 2022, Fernandes 2020)
│    └── ⇢ S13 para plano de disposição alternativa
│
├─── S11 LIDERA também (b) alternativa dry stack:
│    ├── D03 Geotecnia (fundação da pilha filtrada)
│    ├── A3 Orçamento (planta de filtragem + heavy-lift)
│    └── ⇢ S13 para vazão de rejeito da nova produção 15 Mtpa
│
└─── A4 Modelagem (agente-advisory) faz (d) impacto financeiro
     agregado (VPL/TIR + CapEx dry stack vs alteamento vs BF)
     depois que S11 e S13 terminarem.
```

### Fase CONFIRM (handshake condensado — default)

Maestro apresenta ao usuário:
- 3 entregáveis: (i) memorial mineração 15 Mtpa por S13, (ii) memorial
  TSF + dry stack por S11, (iii) modelo financeiro consolidado por A4.
- Estimativa: 4 dias corridos, 3 sub-agentes em paralelo + 1 serial
  (A4 depende dos volumes de S11 e S13).
- R1-R5 verificadas: R1 sanitizada ("[MINERADORA]" no output), R2
  lacunas viram perguntas (LOM histórico, curva de produção anual),
  R5 base BRL @ hoje.

### Fase EXECUTE (parallel default)

`parallel(S11.dry_stack, S11.descaract, S13.expansao)` — 3 ramos
independentes rodam ao mesmo tempo. Cada um emite handoffs cruzados
via tool `⇢` sem transferir contexto. A4 aguarda.

Ao fim: A4 consome os 3 outputs e produz o financeiro.

### Fase DELIVER

Resposta final do Maestro (não repete conteúdo bruto):
1. Sumário: "3 memoriais + 1 modelo. TSF viável para descaracterização
   em 2028 desde que dry stack esteja pronto em 2027 Q1."
2. Entregáveis (paths SharePoint).
3. TRACE raiz para auditoria.
4. Notas do auto-juiz L2 + LLM-judge F6.b (score 4.3/5).
5. Próximos passos: aprovar CapEx dry stack antes de submeter plano
   à ANM.
6. Assinatura: `— Maestro · Manta Associados`

---

## Fronteiras testadas

- **S11 lidera rejeito, não S13** — mesmo quando o pedido menciona
  "mina" primeiro.
- **Q0 explícito no intake de S13** para casos com dry stack: "TSF?
  Não → dry stack → notificar S11 para revisão".
- **A4 não roda antes** — modelagem financeira depende dos volumes que
  S11 e S13 ainda estão calculando (dependência de dado, serial
  obrigatório).
- **KEs acadêmicos citados**: Mendes 2022 (crítica ao alteamento a
  montante pós-Brumadinho), Fernandes 2020 (viabilidade econômica dry
  stack Brasil), Silva 2023 (métricas ANM Res 95).
