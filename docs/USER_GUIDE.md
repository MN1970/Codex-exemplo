# Manta Maestro — User Guide v1.0

**For:** Project managers, engineers, stakeholders  
**Version:** 1.0 (Production Release)  
**Updated:** 2026-07-27

---

## Getting Started

### 1. Creating Your Account

Visit **manta.example.com** and click "Sign up":

1. Enter your **email** (e.g., nome@mantaassociados.com)
2. Create a **password** (min 12 chars, 1 uppercase, 1 number, 1 symbol)
3. Enter your **organization name** (e.g., "Manta Associados")
4. Complete email verification
5. Set up **2FA** (Time-based One-Time Password / TOTP)
   - Use authenticator app (Google Authenticator, Authy)
   - Scan QR code provided
   - Save backup codes in secure location

### 2. Your Profile

Click your **avatar** (top-right) → **Profile**:

- **Personal Info:** Name, email, phone
- **Preferences:** Language (PT/EN), theme (light/dark)
- **API Keys:** Generate keys for programmatic access (advanced)
- **Subscriptions:** Manage billing (if applicable)
- **Security:** Change password, enable/disable MFA, view login history

---

## Selecting Your Agent

The **Maestro router** automatically selects the best agent for your query. However, you can also manually choose:

### Via Agent Browser

Click **Agents** (left sidebar) to see all 20 agents:

**Horizontal agents (cross-segment):**
- **Claims** — Sinistro, seguros, indenizações
- **Contratual** — Contratos, cláusulas, riscos legais
- **Imobiliário** — Propriedade, uso do solo
- **Orçamento** — Custos, precificação (SICRO)
- **Modelagem** — Simulações, análise estrutural
- **Cronograma** — Planning, Gantt, timelines
- **BD** — Business development, leads
- **Apresentações** — PowerPoint, comunicação
- **Advisory** — Consultoria estratégica

**Vertical agents (by segment):**
- **Infraestrutura — Rodovias (S1)** — Pavimentos, terraplenagem, CBUQ
- **Infraestrutura — Pontes (S2)** — Estruturas, fundações, OAE
- **Infraestrutura — Ferrovia (S3)** — Trilhos, via permanente, AMV
- **Infraestrutura — Metrô (S4)** — Estações, NATM, PSD
- **Portos (S6)** — Dragagem, molhes, terminais, ANTAQ
- **Aeroportos (S7)** — Pistas, TPS, ANAC, balizamento
- **Saneamento (S8)** — ETA/ETE, SNIS, AySA, adutoras
- **Energia (S9)** — Transmissão, subestações, ANEEL, leilões
- **Barragens (S10)** — CFRD, rejeitos, TSF, ICOLD

Click any agent card to view:
- **Description:** What it does
- **Capabilities:** Technical expertise
- **Recent responses:** Examples of past outputs
- **Statistics:** Usage count, average rating

---

## Submitting a Prompt

### Manual Agent Selection

1. Click an agent card
2. Scroll to **"Ask [Agent Name]"** input box
3. Type your question or task
4. (Optional) Upload related files
5. Click **"Send"** (or Ctrl+Enter)

**Example prompts:**

**For Rodovia (S1):**
> "Analise o custo unitário de CBUQ usinado a quente, espessura 5cm, em novembro de 2026. Use tabela SICRO mais recente."

**For Saneamento (S8):**
> "Quais são os requisitos de NBR 12211 para dimensionamento de adutora por gravidade com 15km?"

**For Orçamento (Manta 05):**
> "Estime o custo total de uma rodovia de 50km: 2km em corte profundo, 30km em aterro simples, 18km em aterro com bota-fora."

### Automatic Routing (Maestro)

1. Type your prompt in the **main search** (top)
2. Maestro analyzes your input and selects the best agent
3. Response appears with **confidence score** (e.g., 94%)
4. You can **override** if wrong agent selected (click "Try different agent")

---

## Understanding Responses

Each response includes:

### Main Content
The agent's analysis, recommendations, calculations, etc. Written in **Markdown** with:
- **Bold text** for emphasis
- *Italics* for technical terms
- `Code` for formulas, codes (SICRO, NBR references)
- Lists and tables

### Citations
Sources your agent used (if **Include citations** was enabled):

```
[Source] SICRO 2026 — Terraplenagem
[Chunk] Section 3.2 — Unit rates
[Score] 92% relevance
[Link] View source document
```

Click **[Link]** to see the actual source text.

### Metadata
- **Model used:** Which Claude version (Sonnet, Opus)
- **Tokens:** Input/output token count (for billing)
- **Latency:** How fast the response was generated
- **Routing confidence:** How sure Maestro was (80-99%)

---

## Working with Knowledge Hub

### Upload Documents

**Shared knowledge base** of your organization's documents (contracts, standards, past projects):

1. Click **Knowledge Hub** (left sidebar)
2. Click **"+ Upload"** (top-right)
3. Select files (PDF, DOCX, XLS) — max 50MB each
4. Add **tags** (optional): project name, segment, date
5. Click **"Upload"** → Processing starts (1-5 min per file)
6. Get notified when ready

### Search Documents

1. Click **Knowledge Hub** → **Search**
2. Enter natural language query:
   > "Requisitos de concreto em fundações de ponte"
3. Results show:
   - **Document name** (source)
   - **Matching section** (excerpt)
   - **Relevance score** (0-100%)
4. Click to view full document

### Using RAG (Retrieval-Augmented Generation)

When you enable **"Include citations"** in prompt:

1. Your query is converted to semantic embedding
2. Maestro searches your Knowledge Hub
3. Top 3-5 matching documents injected into agent context
4. Agent cites sources in response

**Result:** Responses grounded in YOUR documents (not generic knowledge)

---

## Building Workflows

Automate multi-step processes with the **Workflow Builder**:

### Example: Complete Rodovia Analysis

1. Click **Workflows** (left sidebar)
2. Click **"+ New Workflow"**
3. Give it a name: "Análise Completa — Rodovia 50km"
4. Add workflow **steps** (agents in sequence):

   **Step 1: Technical Analysis**
   - Agent: Infraestrutura — Rodovias (S1)
   - Prompt: "Analise o projeto técnico em: {project_file}"
   - Output variable: `technical_analysis`

   **Step 2: Budget Estimation**
   - Agent: Orçamento (Manta 05)
   - Prompt: "Estime orçamento baseado em: {technical_analysis}"
   - Output variable: `budget_estimate`

   **Step 3: Schedule Planning**
   - Agent: Cronograma (Manta 07)
   - Prompt: "Crie cronograma para: {budget_estimate}"
   - Output variable: `schedule`

5. Click **"Save"**

### Executing a Workflow

1. Open workflow from **Workflows** list
2. Click **"Execute"**
3. Upload required files (e.g., `{project_file}`)
4. Click **"Start"** → Watch progress
5. Results appear step-by-step
6. Download final report (PDF, Word)

---

## Submitting Feedback

Help improve agents by rating responses:

After each agent response, click **"Rate this response"**:

- **⭐⭐⭐⭐⭐** (5 stars) — Excellent, exactly what I needed
- **⭐⭐⭐⭐** (4 stars) — Good, mostly useful
- **⭐⭐⭐** (3 stars) — OK, some useful info
- **⭐⭐** (2 stars) — Poor, missing key points
- **⭐** (1 star) — Unhelpful, incorrect

**Add comment (optional):**
- What was most useful?
- What was missing?
- Any factual errors?

Your feedback is **anonymized** and used to improve routing accuracy (Maestro learns which agent handles which topics best).

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Submit prompt |
| `Ctrl+K` | Search agents |
| `Ctrl+/` | Show keyboard shortcuts |
| `Ctrl+Shift+D` | Toggle dark mode |
| `Ctrl+B` | Open Knowledge Hub search |
| `Escape` | Close modals |

---

## Accessibility Features

**Manta Maestro** supports **WCAG 2.1 AA** accessibility standards:

### Keyboard Navigation
- Tab through all elements
- Enter/Space to activate buttons
- Arrow keys in lists

### Screen Readers
- All images have alt text
- Form inputs labeled properly
- Semantic HTML structure

### Color & Contrast
- Text contrast ratio 4.5:1 (normal), 3:1 (large)
- Color not sole indicator (icons, labels used)
- Works in high-contrast mode

### Dyslexia-Friendly Font
- Settings → Preferences → Font → "Dyslexia-friendly"

---

## Troubleshooting

### "Wrong agent selected"

If Maestro picks the wrong agent:

1. Click **"Try different agent"** button
2. Select correct agent from list
3. Your prompt is re-submitted to correct agent
4. **Help improve Maestro:** Rate the mistake (feedback sent to engineering)

### "Response too slow" (> 10 seconds)

- Check your internet connection
- If persistent, check **Status** (top-right) for system alerts
- Try again in 5 minutes
- Contact support if continues

### "Upload failed"

1. Check file format (PDF, DOCX, XLS supported)
2. Verify file size < 50MB
3. Try different file
4. If still fails, contact support

### "Citation links broken"

If you click a citation and get 404:

1. Document may have been deleted
2. Check Knowledge Hub to verify document exists
3. Contact support to restore

### Lost Password

1. Click **"Forgot password?"** on login page
2. Enter your email
3. Check email for reset link (expires in 1 hour)
4. Create new password
5. Log in with new password

---

## Best Practices

### Writing Effective Prompts

**Good:**
> "Calcule o custo de CBUQ usinado a quente, 5cm espessura, via SICRO 2026. Inclua custos de transporte até a obra (raio 50km)."

**Avoid:**
> "quanto custa asfalto?"

**Tips:**
- Be **specific** about what you need
- Provide **context** (project type, location, standards)
- Ask for **specific format** (table, calculation steps, citations)

### Using Knowledge Hub Effectively

- **Organize by project:** Tag documents with project ID
- **Regular updates:** Upload new standards/contracts
- **Naming:** Use clear file names (e.g., "NBR-7187-Bridges-2020.pdf")
- **Metadata:** Add tags for better searchability

### Workflow Best Practices

- **Linear workflows:** Step output feeds into next step
- **Error handling:** If Step 1 fails, workflow pauses (manual review)
- **Versioning:** Each workflow has version history (rollback if needed)
- **Sharing:** Share workflows with team (requires Manta 02 — Contratual for governance)

---

## Billing & Usage

### Usage Dashboard

Click **Usage** (top-right menu):

- **Tokens used this month:** Input + output tokens
- **Agent execution count:** How many prompts submitted
- **Storage used:** Knowledge Hub documents
- **Estimated cost:** Based on token consumption

### Token Counting

- Typical agent response: 1,500-2,500 tokens (input + output)
- One-page PDF upload: ~3,000 tokens (when added to Knowledge Hub)
- 1,000 tokens ≈ 750 words

### Plans

| Plan | Monthly Cost | Inclusions | Overage |
|------|-------------|-----------|---------|
| Starter | R$ 500 | 100K tokens, 10 workflows | R$ 5 per 1K tokens |
| Professional | R$ 2,000 | 1M tokens, unlimited workflows | R$ 2 per 1K tokens |
| Enterprise | Custom | Unlimited tokens, priority support | Negotiated |

---

## Support & Help

### Getting Support

1. **Chat:** Click **?** (bottom-right) → **Live Chat** (Mon-Fri 9am-5pm BRT)
2. **Email:** support@mantaassociados.com (response within 24h)
3. **FAQ:** Click **?** → **FAQ** for 50+ common questions
4. **Status Page:** status.manta.example.com (service incidents)

### Reporting Issues

1. Click **?** → **Report Issue**
2. Describe what happened
3. Attach screenshot (optional)
4. We'll investigate and follow up via email

### Feature Requests

1. Click **?** → **Suggest Feature**
2. Describe what you'd like
3. Upvote existing requests
4. Product team reviews monthly

---

## Advanced Features

### API Access

For programmatic access to Manta Maestro:

1. Profile → **API Keys**
2. Click **"Generate Key"**
3. Copy key (shown once!)
4. Use in curl/Python/etc. requests

**Example:**
```bash
curl -X POST https://api.manta.example.com/agents/agent_s1_rodovia/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Calcule custo de CBUQ...",
    "include_citations": true
  }'
```

See **API_REFERENCE.md** for complete endpoint documentation.

### Fine-tuning Custom Models

**Enterprise plan** includes fine-tuning:

1. ML → **Create Fine-tuning Job**
2. Upload training data (JSONL format)
3. Select model (Sonnet, Opus)
4. Hyperparameters: learning rate, epochs, rank
5. Job queues → Training starts (1-4 hours)
6. Results: Accuracy, loss curves, export model

---

**Last Updated:** 2026-07-27  
**Next Update:** 2026-08-27 (post go-live feedback)
