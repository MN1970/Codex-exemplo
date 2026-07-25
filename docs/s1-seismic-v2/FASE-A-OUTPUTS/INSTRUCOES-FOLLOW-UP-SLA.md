# Instruções - Follow-up Schedule com SLAs

## Objetivo
Gerenciar follow-ups com 5 especialistas críticos com SLAs diferenciados, escalation automática e fallback plans documentados.

## Estrutura do Arquivo JSON

### Seção Principal: `schedule[]`
Cada especialista tem um objeto contendo:

1. **Identificação**
   - `id`: Código único (ex: `IPOC-001`)
   - `organization`: Nome da organização
   - `specialist`: Descrição do especialista

2. **Contatos**
   - `contact.primary`: Contato principal (nome, email, telefone, departamento)
   - `contact.backup`: Contato backup (para escalation)

3. **SLA**
   - `deadline`: Data em formato ISO (ex: `2026-07-31`)
   - `days_remaining`: Dias até deadline (atualizar diariamente)
   - `severity`: `CRITICAL` ou `HIGH`
   - `response_type`: Descrição do tipo de resposta esperada

4. **Status**
   - Códigos: `AWAITING_RESPONSE`, `IN_PROGRESS`, `COMPLETE`, `MISSED`, `ESCALATED_L1/L2/L3`

5. **Escalation** (3 níveis)
   - `level_1`: Reminder (3-4 dias antes do deadline)
   - `level_2`: Escalação para nível superior (1-2 dias antes)
   - `level_3`: Invoke fallback (no dia do deadline)

6. **Re-contact Triggers**
   - Condições que acionam novos contatos
   - Exemplos: "no response", "partial delivery", "milestone not met"

7. **Action Items**
   - Checklist de datas e ações específicas

8. **Backup Plan**
   - Contatos alternativos e plano de contingência

---

## Cronograma de Escalação Detalhado

### 1. CPRM (Crítico - Deadline 31 JUL)
**Severity: CRITICAL**

| Data | Ação | Responsável | Contato |
|------|------|-------------|---------|
| 2026-07-27 | Phone call + resend via registered mail | Você | Eng. Roberto Ferreira |
| 2026-07-28 | Checkpoint: confirmar 50% progresso | Você | Eng. Roberto |
| 2026-07-29 | Escalação ao Director Regional | Manager | Dra. Marisa Oliveira |
| 2026-07-31 12:00 | Invoke fallback (GeoEngenharia) | Você | Fallback: GeoEngenharia |

**Fallback Plan:**
- Empresa: GeoEngenharia Consultoria Ltda
- Contato: contato@geoengenharia.com.br
- Custo: ~R$ 12.000
- Tempo: 3-5 dias
- Acionado se: sem resposta até 2026-07-31 12:00

---

### 2. IPOC (High - Deadline 31 JUL)
**Severity: HIGH**

| Data | Ação | Responsável | Contato |
|------|------|-------------|---------|
| 2026-07-28 | Reminder email + Teams message | Você | Dr. João Martins |
| 2026-07-29 | Follow-up call + document | Você | Dr. João Martins |
| 2026-07-30 | Escalação para dept head | Manager | Dra. Fernanda Silva |
| 2026-07-31 | Final deadline - mark status | Você | - |

**Backup Plan:**
- Dados públicos INEP/ONS como fallback
- Suplementar com CPRM se necessário

---

### 3. UFOP (High - Deadline 7 AGO)
**Severity: HIGH**

| Data | Ação | Responsável | Contato |
|------|------|-------------|---------|
| 2026-07-25 | Verificar calendário acadêmico UFOP | Você | - |
| 2026-08-03 | Reminder email + Teams | Você | Prof. Dr. Carlos Mendes |
| 2026-08-04 | Follow-up call | Você | Prof. Dr. Carlos |
| 2026-08-05 | Escalação a PROPEP | Manager | Prof. Dr. Antonio Lima |
| 2026-08-07 | Final deadline | Você | - |

**Backup Plan:**
- UFRJ: Prof. Flavio (flavio@ufrj.br) - 7-10 dias
- PUC-RJ: Prof. Daniela (d.costa@puc-rio.br) - 7-10 dias

---

### 4. Defesa Civil (High - Deadline 10 AGO)
**Severity: HIGH**

| Data | Ação | Responsável | Contato |
|------|------|-------------|---------|
| 2026-07-25 | Verificar protocolo SEI recebido | Você | - |
| 2026-08-04 | Phone call + resend via SEI | Você | Tec. Paulo Gomes |
| 2026-08-05 | Follow-up para confirmar timeline | Você | Tec. Paulo |
| 2026-08-08 | Escalação ao Secretário | Manager | Dra. Luciana Costa |
| 2026-08-10 | Final deadline | Você | - |

**Backup Plan:**
- Proceder com best practices da indústria
- Defesa Civil clearance obtida retroativamente (comum em BR)
- Notificar cliente de atraso governamental

---

### 5. USP (High - Deadline 7 AGO)
**Severity: HIGH**

| Data | Ação | Responsável | Contato |
|------|------|-------------|---------|
| 2026-07-25 | Check calendário acadêmico | Você | - |
| 2026-08-03 | Reminder email + institutional channels | Você | Prof. Dr. Ricardo Santos |
| 2026-08-04 | Follow-up call + assessment | Você | Prof. Dr. Ricardo |
| 2026-08-05 | Escalação a Pró-Reitoria | Manager | Prof. Dra. Camila Moura |
| 2026-08-07 | Final deadline | Você | - |

**Backup Plan:**
- UNICAMP: Prof. Heitor Assiss (h.assis@unicamp.br) - 8-10 dias
- UNESP Rio Claro: Prof. Wagner (w.costa@unesp.br) - 8-10 dias

---

## Como Usar Este Schedule

### Diariamente
1. Atualizar `days_remaining` para cada contato
2. Verificar se algum trigger de re-contact foi acionado
3. Executar action items do dia conforme `action_items[date]`

### Na ocorrência de resposta
1. Mudar `status` para `IN_PROGRESS`
2. Registrar em `communication_log_template` (copiar template)
3. Confirmar timeline e milestone dates com contato
4. Agendar checkpoint calls (2026-07-28, 2026-08-04)

### Na ocorrência de atraso
1. Ativar escalation do nível correspondente
2. Atualizar `status` para `ESCALATED_L1/L2/L3`
3. Registrar tentativa em communication log
4. Se deadline atingido, invocar backup plan

### Na recepção de deliverable
1. Mudar `status` para `COMPLETE` (ou `PARTIAL` se <100%)
2. Registrar data e percentual recebido
3. Notificar stakeholders
4. Arquivar no projeto

---

## Codes de Status e Significado

```
AWAITING_RESPONSE     → Primeiro contato enviado, aguardando resposta
IN_PROGRESS           → Contato confirmou, trabalho em andamento
MILESTONE_50          → 50% do deliverable recebido
MILESTONE_75          → 75% do deliverable recebido
COMPLETE              → 100% recebido antes do deadline
MISSED                → Deadline perdido
PARTIAL               → Deliverable parcial aceito
ESCALATED_L1          → Escalação nível 1 acionada
ESCALATED_L2          → Escalação nível 2 acionada
ESCALATED_L3          → Escalação nível 3 / fallback acionado
```

---

## Templates de Email (Português)

### Escalation Level 1 - Reminder
```
Assunto: Acompanhamento: [Organization] - SLA vence em 3 dias - Protocolo [ID]

Prezado [Contact Name],

Este é um acompanhamento da solicitação enviada em [date_original].

Confirmamos que aguardamos retorno até [SLA_deadline] (em 3 dias).

Por favor, confirme recebimento e timeline de entrega.

Atenciosamente,
[Seu Nome]
Manta Associados
```

### Escalation Level 2 - Urgent
```
Assunto: ESCALAÇÃO URGENTE: [Organization] - SLA crítico - [ID]

Prezada [Backup Contact Name],

Escalamos a solicitação para o seu conhecimento, pois não recebemos resposta do contato original até a presente data.

Deadline: [SLA_deadline] (em 1 dia)
Assunto: [Subject]
Protocolo: [ID]

Solicitamos confirmação imediata de entrega ou justificativa de atraso.

Disposto a facilitar recursos necessários.

Atenciosamente,
[Seu Nome]
Manta Associados
```

---

## Checklist de Implementação

- [ ] **Hoje (2026-07-25)**
  - [ ] Verificar calendário acadêmico UFOP e USP
  - [ ] Confirmar protocolo SEI Defesa Civil foi recebido
  - [ ] Confirmar emails de contato estão corretos
  - [ ] Backups plans documentados no Sharepoint

- [ ] **2026-07-27** (CPRM - 4 dias antes)
  - [ ] Phone call Eng. Roberto + resend via registered mail
  - [ ] Document outcome em communication log

- [ ] **2026-07-28** (CPRM & IPOC - 3 dias antes)
  - [ ] CPRM: checkpoint call confirmar 50% progresso
  - [ ] IPOC: reminder email + Teams message

- [ ] **2026-07-29** (IPOC - 2 dias antes)
  - [ ] IPOC: follow-up call
  - [ ] CPRM: escalação se ainda sem resposta

- [ ] **2026-07-30** (IPOC & Defesa Civil)
  - [ ] IPOC: escalação para dept head
  - [ ] Defesa Civil: checkpoint

- [ ] **2026-07-31** (CPRM & IPOC - DEADLINE)
  - [ ] Registrar status final (COMPLETE/MISSED)
  - [ ] Se missed: invocar fallback
  - [ ] Notificar stakeholders

- [ ] **2026-08-03** (UFOP & USP & Defesa Civil - 4 dias antes)
  - [ ] UFOP: reminder email + Teams
  - [ ] USP: reminder email + institutional channels
  - [ ] Defesa Civil: phone call

- [ ] **2026-08-04** (UFOP & USP)
  - [ ] UFOP: follow-up call
  - [ ] USP: follow-up call
  - [ ] Defesa Civil: checkpoint

- [ ] **2026-08-05** (UFOP & USP & Defesa Civil - 2 dias antes)
  - [ ] UFOP: escalação a PROPEP se sem resposta
  - [ ] USP: escalação a Pró-Reitoria se sem resposta
  - [ ] Defesa Civil: escalação ao Secretário se sem resposta

- [ ] **2026-08-07** (UFOP & USP - DEADLINE)
  - [ ] Registrar status final
  - [ ] Se missed: invocar fallback
  - [ ] Notificar stakeholders

- [ ] **2026-08-10** (Defesa Civil - DEADLINE)
  - [ ] Registrar status final
  - [ ] Document governo delay se aplicável
  - [ ] Notificar cliente

---

## Monitoramento de Risco

### Indicadores de Risco ALTO
- Nenhuma resposta até 3 dias antes do deadline
- Partial response (<50%) sem timeline de conclusão
- Contato indisponível (férias, sabático, viagem)

### Ações preventivas
1. Verificar calendários acadêmicos AGORA (UFOP, USP, Defesa Civil)
2. Pre-confirmar availability dos contatos principais na próxima semana
3. Ter fallback plans 100% acionáveis (orçamentos validados, contatos confirmados)

---

## Integrações sugeridas

1. **Google Calendar**: Sincronizar action items deste JSON com calendário pessoal
2. **SharePoint**: Upload do JSON + communication logs para histórico de projeto
3. **Slack**: Lembretes automáticos 1 dia antes de cada escalation
4. **Excel/Power BI**: Dashboard com status de cada SLA (% de progresso, dias restantes, risco)

---

## Contato para Suporte
**Owner**: mneves@mantaassociados.com  
**Última atualização**: 2026-07-25

---

## Apêndice: Communication Log Template

Copiar e preencher para cada contato:

```json
{
  "date": "2026-07-25 14:30",
  "organization": "CPRM",
  "contact_name": "Eng. Roberto Ferreira",
  "contact_method": "email",
  "message_type": "initial_contact",
  "subject": "Urgente: Parecer Geotécnico - Fundações da Barragem",
  "outcome": "no_response",
  "notes": "Email enviado. Aguardando confirmação de recebimento.",
  "next_action": "Follow-up call em 2026-07-27"
}
```

Manter registro em arquivo separado: `communication-log-2026-07.json`
