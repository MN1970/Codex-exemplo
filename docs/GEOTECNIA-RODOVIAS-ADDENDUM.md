# Addendum pronto para deploy — Extensão de Geotecnia Rodoviária
## (perfil de cortes/aterros, baliza de uso de material, banco JSON consolidado, QA/QC de sondagens)

**Status:** ✅ **gate humano (MN) aprovado em 2026-09-12** (confirmado em
sessão de chat). Aplicação técnica ainda **pendente**: a skill
`rodovias-geotecnia` não foi localizada neste repositório
(`Codex-exemplo`) nem seu caminho canônico foi confirmado no SharePoint
nesta sessão. Antes de publicar, localizar o `SKILL.md` de produção de
`rodovias-geotecnia` (provável local: `04_IA/Manta-Maestro/02-sub-skills/`
no SharePoint, por analogia ao padrão usado por
`skill-proposta-comercial-SKILL.md`) e colar o bloco da Seção A abaixo na
posição indicada — passo bloqueado nesta sessão porque o conector
`SharePoint_Manta` está desconectado (mesma situação já registrada para o
addendum de `proposta-comercial`).

**Atualização 2026-09-12:** os números de norma NBR/DNIT citados neste
addendum foram verificados por pesquisa web (4 pesquisas independentes
no total) após a primeira versão — ver nota no início da seção 11 e a
marcação de confiança por linha em `BALIZA_PADRAO_DNIT` (seção 11.3).
Números/títulos de norma têm confiança alta. Uma pesquisa dedicada
confirmou `aterro_corpo` (CBR≥2%, expansão≤4%) e a expansão de
`aterro_coroamento` (≤2%) contra o DNIT 108/2009-ES — mas revelou que o
CBR mínimo do coroamento **não é um valor fixo** (era um placeholder de
"6%" sem base normativa); corrigido para `especificacao_projeto`
obrigatório, como já valia para `reforco_subleito`. Seguem pendentes
(sem leitura direta do PDF oficial): expansão exata do reforço do
subleito e a tabela de CBR por faixa de tráfego da base — ver checklist
de aplicação no fim deste documento.

Motivação: pedido de MN (2026-09-12) para complementar a capacidade de
geotecnia rodoviária em 4 frentes — (1) modelagem do perfil dos cortes e do
fundo dos aterros a partir das localizações/volumes do balanço de massa,
(2) CBR + plasticidade por material com baliza geotécnica de uso em
aterros conforme as especificações de terraplenagem/pavimentação de cada
projeto, (3) banco de dados JSON consolidado das sondagens (cotas, nível
d'água, ensaios, classificação), e (4) QA/QC das sondagens (qualidade,
densidade de furos, período/validade).

---

## Onde inserir

No arquivo `SKILL.md` de `rodovias-geotecnia`, inserir o bloco da
**Seção A** como novas seções **10 a 13**, logo depois da atual "## 9.
Schemas de Dados" (ou renumerando 9→14 se preferir manter Schemas por
último — nesse caso Schemas vira a seção 14). Nenhuma seção 1–9 existente
precisa ser alterada; é puramente aditivo. Os scripts referenciados
(`perfil_corte_aterro.py`, extensão de `ensaios_geotecnicos.py`,
`qa_qc_sondagem.py`) vão em `scripts/`, ao lado dos já existentes.

---

## SEÇÃO A — Conteúdo a colar

```markdown
## 10. Modelagem de Perfil de Cortes e Fundo de Aterros

Módulo que cruza a sondagem localizada no eixo (seção 6) com as
progressivas e volumes de corte/aterro produzidos pela skill
`balanco-rodoviario-orquestrador` (modo A — terraplenagem), para gerar
geometria de talude por material e avaliação de fundação de aterro.

### 10.1 Interface com o balanço de massa

```python
# Script: scripts/perfil_corte_aterro.py
# Entrada esperada de balanco-rodoviario-orquestrador (modo A), por estaca:
# {"progressiva_m": float, "tipo": "corte"|"aterro", "volume_m3": float,
#  "cota_terreno_m": float, "cota_greide_m": float, "altura_m": float}

def cruzar_balanco_com_sondagens(estacas_balanco, sondagens_localizadas, buffer_m=80):
    """Associa cada estaca de corte/aterro à sondagem mais próxima (mesma
    função de projeção usada em localizar_sondagens_no_eixo, seção 6)."""
    from .perfil_geotecnico import localizar_sondagens_no_eixo
    resultado = []
    for estaca in estacas_balanco:
        candidatas = [s for s in sondagens_localizadas
                      if abs(s["progressiva_m"] - estaca["progressiva_m"]) <= buffer_m]
        sond = min(candidatas, key=lambda s: abs(s["progressiva_m"] - estaca["progressiva_m"])) \
               if candidatas else None
        resultado.append({**estaca, "sondagem_ref": sond})
    return resultado
```

### 10.2 Geometria de talude de corte por material

```python
# Inclinações de referência (V:H) por categoria DNIT / NSPT médio da camada
# exposta no talude — ajustar por projeto quando houver ensaio de
# estabilidade (Bishop/Morgenstern/Spencer) específico.
TALUDE_REFERENCIA = [
    # (categoria_dnit, nspt_min, nspt_max, inclinacao_v_h, altura_max_sem_berma_m)
    ("3a_categoria", None, None, (1, 0.3), 15),   # rocha sã
    ("2a_categoria", None, None, (1, 0.75), 12),  # rocha alterada/matacões
    ("1a_categoria", 15, None, (1, 1.0), 10),     # solo rijo/compacto
    ("1a_categoria", 8, 15, (1, 1.5), 8),         # solo médio
    ("1a_categoria", None, 8, (1, 2.5), 6),       # solo mole/fofo — avaliar estabilidade
]

def definir_inclinacao_talude(categoria_dnit, nspt_medio, altura_corte_m):
    """Retorna (V:H, exige_berma, exige_estudo_estabilidade).
    Berma obrigatória a cada 10 m de altura quando > altura_max_sem_berma_m.
    Solo mole (NSPT<8) sempre marca exige_estudo_estabilidade=True —
    inclinação de referência aqui é só um limite superior conservador."""
    for cat, n_min, n_max, incl, h_max in TALUDE_REFERENCIA:
        if cat != categoria_dnit:
            continue
        if n_min is not None and (nspt_medio is None or nspt_medio < n_min):
            continue
        if n_max is not None and (nspt_medio is None or nspt_medio >= n_max):
            continue
        exige_estudo = nspt_medio is not None and nspt_medio < 8
        exige_berma = altura_corte_m > h_max
        return incl, exige_berma, exige_estudo
    return (1, 2.0), True, True  # sem dado — conservador, força revisão manual

def gerar_perfil_corte(estaca, sondagem_ref):
    """Gera geometria do talude (lista de pontos do offset 0 até a crista)
    a partir da altura de corte e da inclinação definida por material."""
    nspt_medio = None
    categoria = "indefinido"
    if sondagem_ref:
        camadas_superficiais = [c for c in sondagem_ref["camadas"]
                                 if c["profundidade_m"] <= estaca["altura_m"]]
        nspts = [c["nspt"] for c in camadas_superficiais if c["nspt"] is not None]
        nspt_medio = sum(nspts) / len(nspts) if nspts else None
        # categoria_dnit vem aninhada em camada["classificacao"], não na
        # raiz da camada (ver schema da seção 12) — ler direto na raiz
        # sempre cai em "indefinido" silenciosamente e força a inclinação
        # conservadora de fallback mesmo com dado real disponível.
        categoria = camadas_superficiais[0].get("classificacao", {}).get("categoria_dnit", "indefinido") \
                    if camadas_superficiais else "indefinido"

    (v, h), exige_berma, exige_estudo = definir_inclinacao_talude(
        categoria, nspt_medio, estaca["altura_m"])

    n_bermas = int(estaca["altura_m"] // 10) if exige_berma else 0
    return {
        "progressiva_m": estaca["progressiva_m"],
        "altura_corte_m": estaca["altura_m"],
        "categoria_dnit": categoria,
        "nspt_medio_zona_talude": nspt_medio,
        "inclinacao_v_h": f"{v}:{h}",
        "n_bermas": n_bermas,
        "exige_estudo_estabilidade": exige_estudo,
        "observacao": "NSPT médio < 8 na zona do talude — inclinação é só "
                      "referência conservadora, exigir estudo Bishop/Morgenstern/"
                      "Spencer antes de liberar o projeto executivo."
                      if exige_estudo else None,
    }
```

### 10.3 Fundação de aterros (fundo de aterro)

```python
def avaliar_fundacao_aterro(estaca, sondagem_ref, peso_especifico_aterro_kn_m3=19.0):
    """Avalia a camada de fundação sob o aterro (profundidade 0 a ~2×altura
    do aterro) e recomenda tratamento quando o solo de fundação é mole.
    Critério simplificado (triagem): NSPT<4 nos 3 primeiros metros sob o
    aterro → risco de ruptura/recalque excessivo, exige tratamento;
    4<=NSPT<8 → aceitável com monitoramento (instrumentação/recalque)."""
    if not sondagem_ref:
        return {"progressiva_m": estaca["progressiva_m"],
                "veredito": "sem sondagem associada — não avaliável",
                "acao": "solicitar sondagem complementar antes de liberar projeto"}

    prof_influencia = min(2 * estaca["altura_m"], sondagem_ref.get("prof_total", 0))
    camadas_fundacao = [c for c in sondagem_ref["camadas"]
                         if c["profundidade_m"] <= prof_influencia]
    nspts = [c["nspt"] for c in camadas_fundacao if c["nspt"] is not None]
    nspt_min = min(nspts) if nspts else None

    if nspt_min is None:
        # sondagem sem prof_total (ou sem camada dentro da zona de
        # influência) NÃO é "adequado" por omissão — sem dado é sem dado.
        veredito = "sem dado suficiente na zona de influência — sondagem incompleta"
        tratamentos = ["completar/estender a sondagem até cobrir a zona de "
                       "influência (~2x a altura do aterro) antes de avaliar"]
    elif nspt_min < 4:
        veredito = "solo de fundação mole/fofo — risco de ruptura/recalque"
        tratamentos = ["remoção e substituição do solo mole (se espessura <2 m)",
                        "colchão drenante + geotêxtil de separação",
                        "bermas de equilíbrio (contrapeso lateral)",
                        "PVDs (drenos verticais) + sobrecarga temporária, se espessura grande",
                        "aterro em etapas com monitoramento de recalque/poropressão"]
    elif nspt_min < 8:
        veredito = "solo de fundação médio — aceitável com monitoramento"
        tratamentos = ["instrumentação (marcos superficiais + piezômetros)",
                        "controle de velocidade de alteamento"]
    else:
        veredito = "solo de fundação adequado — sem tratamento especial indicado"
        tratamentos = []

    return {
        "progressiva_m": estaca["progressiva_m"],
        "altura_aterro_m": estaca["altura_m"],
        "nspt_min_zona_influencia": nspt_min,
        "veredito": veredito,
        "tratamentos_recomendados": tratamentos,
        "observacao": "Triagem por NSPT — para aterros >6 m ou fundação com "
                      "NSPT<4 e espessura >3 m, exigir cálculo de estabilidade "
                      "(Bishop/Spencer) e recalque (Terzaghi 1D ou numérico) "
                      "antes da liberação do projeto executivo.",
    }
```

## 11. Classificação Completa de Materiais e Baliza Geotécnica de Uso em Aterros

Estende `scripts/ensaios_geotecnicos.py` (seção 7) com limites de
Atterberg, SUCS/AASHTO completos e a tabela de adequação de material por
camada, cruzada com a especificação de terraplenagem/pavimentação do
projeto (DNIT 108/2009-ES — aterros, DNIT 138/2010-ES — reforço do
subleito, DNIT 139/2010-ES — sub-base, DNIT 141/2022-ES — base, ou a
especificação particular do edital/contrato quando informada).

> **Normas verificadas nesta revisão (2026-09-12), por pesquisa web com
> triangulação de múltiplas fontes — não por leitura direta do PDF
> oficial (acesso bloqueado pelo proxy de rede desta sessão):**
> DNIT 106/2009-ES (cortes), DNIT 107/2009-ES (empréstimos),
> DNIT 108/2009-ES (aterros, corrigida 2025), DNIT 137/2010-ES
> (regularização do subleito), DNIT 138/2010-ES (reforço do subleito),
> DNIT 139/2010-ES (sub-base estabilizada granulometricamente),
> DNIT 141/2022-ES (base estabilizada granulometricamente — **não**
> 141/2010, que foi revisada), DNIT 172/2016-ME (CBR, substitui
> DNER-ME 049/94 e 050/64), DNIT 164/2013-ME (Proctor, substitui
> DNER-ME 047/64, 048/64, 129/89/94), DNIT 459/2025-ME (granulometria,
> substitui DNER-ME 080/94 e 051/94), DNER-ME 122/94 (limite de
> liquidez) e DNER-ME 082/94 (limite de plasticidade) — estes dois
> últimos com título/ano confirmados mas sem confirmação de que não
> foram substituídos por norma DNIT mais recente. **Os valores
> numéricos de CBR/expansão/IP abaixo têm confiança média** (fontes
> secundárias convergentes, não o texto integral da norma) — conferir
> contra o PDF oficial do DNIT/IPR antes de uso em documento normativo
> formal ou em disputa contratual. Não existe norma ABNT equivalente ao
> sistema SUCS/USCS (ver nota na função `classificar_sucs_completo`
> abaixo) nem uma especificação DNIT/DNER numerada isolada para
> classificação AASHTO — ambas são de uso corrente no Brasil por
> adoção direta (ASTM D2487 / AASHTO M 145 e Manual de Pavimentação
> DNIT — IPR-719), não por norma nacional própria.

```python
# ─── LIMITES DE ATTERBERG ─────────────────────────────────────────────────
def calcular_limites_atterberg(ll_pct, lp_pct):
    """IP = LL - LP. IP=None (NP, não plástico) quando LP não determinável."""
    if ll_pct is None or lp_pct is None:
        return {"LL": ll_pct, "LP": lp_pct, "IP": None, "classificacao": "NP (não plástico)"}
    ip = round(ll_pct - lp_pct, 1)
    if ip <= 0:
        return {"LL": ll_pct, "LP": lp_pct, "IP": 0, "classificacao": "NP (não plástico)"}
    faixa = ("baixa" if ip < 15 else "média" if ip < 30 else "alta")
    return {"LL": ll_pct, "LP": lp_pct, "IP": ip, "classificacao": f"plasticidade {faixa}"}

# ─── SUCS COMPLETO (USCS — ASTM D2487) ────────────────────────────────────
# Não existe norma ABNT equivalente ao SUCS/USCS — a prática brasileira usa
# a ASTM D2487 diretamente. NBR 6502 é só terminologia de solos/rochas (não
# um sistema de classificação); NBR 7250 trata de identificação/descrição
# tátil-visual de amostras, mas sua vigência não foi confirmada nesta
# revisão — não citar como fonte normativa da classificação SUCS em si.
def classificar_sucs_completo(finos_pct, pedregulho_pct, cu=None, cc=None, ll=None, ip=None):
    """Classificação SUCS de 2 letras. Requer processar_granulometria()
    (seção 7) para finos_pct/pedregulho_pct/Cu/Cc, e calcular_limites_atterberg()
    para ll/ip quando finos_pct > 12 (necessário para o sufixo C/M)."""
    granular = finos_pct <= 50
    if granular:
        prefixo = "G" if pedregulho_pct > 50 else "S"
        if finos_pct < 5:
            bem_graduado = (cu is not None and cu >= (4 if prefixo == "G" else 6)
                             and cc is not None and 1 <= cc <= 3)
            return f"{prefixo}{'W' if bem_graduado else 'P'}"
        if finos_pct > 12:
            if ll is None or ip is None:
                return f"{prefixo}M/C (indefinido — LL/IP do fino não informado)"
            sufixo = "C" if (ip is not None and ip > 0.73 * (ll - 20)) else "M"
            return f"{prefixo}{sufixo}"
        return f"{prefixo}W-{prefixo}M / {prefixo}P-{prefixo}M (fronteira 5–12% finos)"
    # solo fino
    if ll is None or ip is None:
        return "ML/CL/MH/CH (indefinido — LL/IP não informado)"
    alta_compressibilidade = ll >= 50
    acima_linha_A = ip > 0.73 * (ll - 20)
    if acima_linha_A:
        return "CH" if alta_compressibilidade else "CL"
    return "MH" if alta_compressibilidade else "ML"

# ─── AASHTO COMPLETO (M 145) COM GROUP INDEX ──────────────────────────────
def classificar_aashto(passante_200_pct, ll=None, ip=None):
    """Retorna grupo AASHTO (A-1 a A-7-6) + Group Index (GI), usado nas
    especificações de terraplenagem/pavimentação do DNIT para aceitar/
    rejeitar material de reforço do subleito, sub-base e base."""
    ip = ip or 0
    ll = ll or 0
    if passante_200_pct <= 35:
        if ip <= 6:
            grupo = "A-1/A-3" if passante_200_pct <= 25 else "A-2-4/A-2-6"
        else:
            grupo = "A-2-7" if ll >= 41 else "A-2-6"
    else:
        if ll <= 40:
            grupo = "A-4" if ip <= 10 else "A-6"
        else:
            grupo = "A-5" if ip <= 10 else ("A-7-5" if ip <= (ll - 30) else "A-7-6")

    a = max(0, min(passante_200_pct - 35, 40))
    b = max(0, min(passante_200_pct - 15, 40))
    c = max(0, min(ll - 40, 20))
    d = max(0, min(ip - 10, 20))
    gi = round(0.2 * a + 0.005 * a * c + 0.01 * b * d, 1)
    return {"grupo_aashto": grupo, "group_index": max(0, gi)}

# ─── BALIZA GEOTÉCNICA DE USO EM ATERROS E PAVIMENTAÇÃO ───────────────────
# Sobrepor por `especificacao_projeto` sempre que o edital/contrato definir
# valores próprios — nunca editar este dicionário-base por projeto.
#
# Confiança por linha (ver nota de normas verificadas acima):
#   - sub_base e base: valores confirmados (DNIT 139/2010-ES, DNIT 141/2022-ES),
#     exceto cbr_min de "base", que a norma varia por faixa de tráfego N
#     (60% é um piso conservador; pode exigir até ~80% para N>5x10^6 —
#     conferir a tabela completa do DNIT 141/2022-ES por N antes de aplicar).
#   - reforco_subleito: DNIT 138/2010-ES não fixa um CBR mínimo absoluto —
#     exige CBR do material > CBR do subleito local do projeto. cbr_min=None
#     aqui de propósito: SEMPRE passar especificacao_projeto com o CBR do
#     subleito real para esta camada, nunca usar um número fixo genérico.
#     expansao_max=1.0 tem confiança média (uma fonte cita 2%, possível
#     mistura com DNIT 137/2010-ES — regularização do subleito).
#   - aterro_corpo: CBR mín. 2% e expansão máx. 4% CONFIRMADOS por pesquisa
#     dedicada (2026-09-12, confiança média-alta — convergência de múltiplas
#     fontes secundárias sobre o texto da norma, PDF oficial ainda não lido
#     diretamente por bloqueio de rede desta sessão), compactação Método A
#     (DNER-ME 129/94) a 100% da massa específica aparente seca máxima,
#     camadas de até 0,30 m.
#   - aterro_coroamento: expansão máx. 2% CONFIRMADA (mesma pesquisa,
#     compactação Método B, camadas de até 0,20 m). cbr_min=None aqui DE
#     PROPÓSITO: a pesquisa não encontrou um CBR mínimo fixo para esta
#     camada no texto da norma — a exigência recorrente nas fontes é
#     "capacidade de suporte melhor que a do corpo do aterro" e "ISC
#     igual ou superior ao previsto em projeto", ou seja, relativo/definido
#     em projeto, igual ao caso de reforco_subleito. SEMPRE passar
#     especificacao_projeto com o CBR real exigido para esta camada.
BALIZA_PADRAO_DNIT = {
    "aterro_corpo":        {"cbr_min": 2,    "expansao_max": 4.0, "ip_max": None, "gi_max": None,
                             "confianca": "confirmado — DNIT 108/2009-ES (pesquisa web, PDF oficial não lido diretamente)"},
    "aterro_coroamento":   {"cbr_min": None, "expansao_max": 2.0, "ip_max": None, "gi_max": None,
                             "confianca": "expansão confirmada (DNIT 108/2009-ES); CBR é relativo/definido em projeto — usar especificacao_projeto"},
    "reforco_subleito":    {"cbr_min": None, "expansao_max": 1.0, "ip_max": None, "gi_max": None,
                             "confianca": "CBR é relativo ao subleito do projeto — usar especificacao_projeto"},
    "sub_base":            {"cbr_min": 20,   "expansao_max": 1.0, "ip_max": None, "gi_max": 0,
                             "confianca": "confirmado — DNIT 139/2010-ES"},
    "base":                {"cbr_min": 60,   "expansao_max": 0.5, "ip_max": 6,    "gi_max": None,
                             "confianca": "confirmado (piso) — DNIT 141/2022-ES; pode exigir até 80% conforme N"},
}

def avaliar_baliza_uso(material, camada_alvo, especificacao_projeto=None):
    """material: dict com cbr_pct, expansao_pct, ip, group_index (o que faltar
    é tratado como 'não verificado', nunca como aprovado por omissão).
    especificacao_projeto: dict opcional no mesmo formato de
    BALIZA_PADRAO_DNIT[camada_alvo] para sobrepor os limites do edital/contrato
    específico (registrar sempre a fonte na saída para rastreabilidade)."""
    limites = (especificacao_projeto or BALIZA_PADRAO_DNIT.get(camada_alvo))
    if limites is None:
        return {"veredito": "camada_alvo desconhecida", "camada_alvo": camada_alvo}

    pendencias, motivos_reprovacao = [], []
    cbr = material.get("cbr_pct")
    if limites.get("cbr_min") is None:
        # ex.: reforço do subleito e coroamento do aterro — sem mínimo
        # absoluto na norma padrão; exige especificacao_projeto com o CBR
        # relativo real (do subleito, ou superior ao do corpo do aterro).
        pendencias.append("cbr_min não definido no padrão para esta camada — "
                           "informar especificacao_projeto com o CBR relativo do projeto")
    elif cbr is None:
        pendencias.append("CBR não informado")
    elif cbr < limites["cbr_min"]:
        motivos_reprovacao.append(f"CBR {cbr}% < mínimo {limites['cbr_min']}%")

    exp = material.get("expansao_pct")
    if exp is None:
        pendencias.append("expansão não informada")
    elif exp > limites["expansao_max"]:
        motivos_reprovacao.append(f"expansão {exp}% > máximo {limites['expansao_max']}%")

    if limites.get("ip_max") is not None:
        ip = material.get("ip")
        if ip is None:
            pendencias.append("IP não informado")
        elif ip > limites["ip_max"]:
            motivos_reprovacao.append(f"IP {ip} > máximo {limites['ip_max']}")

    if limites.get("gi_max") is not None:
        gi = material.get("group_index")
        if gi is None:
            pendencias.append("Group Index não informado")
        elif gi > limites["gi_max"]:
            motivos_reprovacao.append(f"GI {gi} > máximo {limites['gi_max']}")

    if motivos_reprovacao:
        veredito = "inadequado"
    elif pendencias:
        veredito = "indeterminado — ensaios incompletos"
    else:
        veredito = "adequado"

    return {
        "camada_alvo": camada_alvo,
        "veredito": veredito,
        "motivos_reprovacao": motivos_reprovacao,
        "pendencias": pendencias,
        "fonte_especificacao": "projeto (override)" if especificacao_projeto else "DNIT (padrão)",
        "confianca_do_padrao": limites.get("confianca", "n/a — especificacao_projeto"),
    }
```

## 12. Banco de Dados JSON Consolidado (extensão do `schema_sondagem.json`)

Campos novos por camada, adicionados ao `params.json` de sondagem (seção 9
do skill — objeto original preservado, isto é aditivo):

```json
{
  "camadas": [
    {
      "profundidade_m": 3.0,
      "nspt": 6,
      "descricao_solo": "Argila siltosa marrom",
      "ensaios": {
        "granulometria": {"D10": null, "D30": null, "D60": 0.018, "Cu": null, "Cc": null,
                           "finos_pct": 78, "pedregulho_pct": 0},
        "limites_atterberg": {"LL": 42, "LP": 19, "IP": 23},
        "cbr_pct": 5.2,
        "expansao_pct": 1.8,
        "proctor": {"w_otimo_pct": 18.4, "gd_max_kg_m3": 1620}
      },
      "classificacao": {"SUCS": "CL", "AASHTO": "A-6", "group_index": 9,
                         "categoria_dnit": "1a_categoria"},
      "baliza_uso": {
        "aterro_corpo": "adequado",
        "aterro_coroamento": "inadequado",
        "reforco_subleito": "inadequado",
        "sub_base": "inadequado",
        "base": "inadequado"
      },
      "rastreabilidade": {
        "laudo_origem": "SP-04_Sondatec_2026-03.pdf",
        "data_ensaio": "2026-03-11",
        "empresa": "Sondatec",
        "responsavel_tecnico": "ART 123456789",
        "revisao": "REV_00"
      }
    }
  ]
}
```

Schema JSON completo (com os campos novos formalizados): ver
`references/schema_sondagem.json` — adicionar as chaves `ensaios`,
`classificacao`, `baliza_uso` e `rastreabilidade` ao objeto de camada já
documentado, sem remover nenhuma chave existente.

## 13. QA/QC de Sondagens — Controle de Qualidade Manta Maestro

Checklist normativo (NBR 6484:2020 — método de ensaio SPT; NBR 8036:1983 —
programação/malha/profundidade de sondagens para fundações; NBR 9604:2024 —
abertura de poço/trincheira com amostra deformada/indeformada, quando
aplicável) executado automaticamente sobre o conjunto de sondagens de um
projeto, antes de liberar o perfil geotécnico composto (seção 6) para uso
em projeto executivo. Números confirmados por pesquisa web nesta revisão
(2026-09-12) — sem leitura direta do texto integral da norma.

```python
# Script: scripts/qa_qc_sondagem.py

REGRAS_QA_QC_PADRAO = {
    # espacamento_max_m: NBR 6484 é método de ensaio (não fixa malha) e
    # NBR 8036 trata de fundações de edifícios, não de investigação
    # rodoviária — 300 m é referência de prática de mercado para
    # rodovias em fase de projeto básico, não um valor normativo. Ajustar
    # sempre pelo termo de referência do contrato ou norma interna Manta;
    # reduzir para 100-150 m em cortes altos, OAE e trechos críticos.
    "espacamento_max_m": 300,
    "profundidade_min_relativa_greide": 6.0,  # m abaixo da cota de greide, mínimo
    "validade_laudo_anos": 2,
    "exige_na_medido": True,
    "exige_amostragem_continua_1m": True,
    "delta_nspt_suspeito": 15,        # salto de NSPT entre furos vizinhos sem
                                       # justificativa geológica registrada
}

def qa_qc_sondagem(sondagens, eixo_pontos, data_referencia, regras=None):
    """Roda o conjunto de checagens sobre as sondagens já localizadas no
    eixo (saída de localizar_sondagens_no_eixo, seção 6) e retorna lista de
    não conformidades por sondagem + malha, com severidade.
    Severidades: "bloqueante" (não liberar projeto executivo sem sanar),
    "alerta" (registrar e seguir com ressalva), "info"."""
    import datetime
    regras = {**REGRAS_QA_QC_PADRAO, **(regras or {})}
    achados = []

    # 1. Malha — espaçamento entre furos consecutivos ao longo do eixo
    ordenadas = sorted(sondagens, key=lambda s: s["progressiva_m"])
    for anterior, atual in zip(ordenadas, ordenadas[1:]):
        dist = atual["progressiva_m"] - anterior["progressiva_m"]
        if dist > regras["espacamento_max_m"]:
            achados.append({"tipo": "malha_aberta", "severidade": "alerta",
                             "sondagens": [anterior["id"], atual["id"]],
                             "distancia_m": round(dist, 1),
                             "limite_m": regras["espacamento_max_m"]})

    for sond in sondagens:
        # 2. Profundidade mínima abaixo do greide — SEMPRE avaliada, com ou
        # sem cota_greide_m informada (checagem anterior só rodava quando
        # cota_greide_m existia, deixando sondagens sem essa cota passarem
        # sem checagem nenhuma). Quando a cota do greide é conhecida, mede
        # a profundidade relativa a ela (a boca do furo pode estar acima ou
        # abaixo do greide futuro); sem ela, usa a profundidade bruta do
        # furo como aproximação.
        cota_greide = sond.get("cota_greide_m")
        prof_min_exigida = regras["profundidade_min_relativa_greide"]
        if cota_greide is not None:
            prof_abaixo_greide = sond["prof_total"] - (sond["cota_boca"] - cota_greide)
        else:
            prof_abaixo_greide = sond["prof_total"]
        if prof_abaixo_greide < prof_min_exigida and not sond.get("impenetravel_atingido"):
            achados.append({"tipo": "profundidade_insuficiente", "severidade": "bloqueante",
                             "sondagem": sond["id"], "prof_abaixo_greide_m": round(prof_abaixo_greide, 2),
                             "exigido_m": prof_min_exigida})

        # 3. Validade do laudo
        data_laudo = sond.get("rastreabilidade", {}).get("data_ensaio")
        if data_laudo:
            idade_anos = (data_referencia - datetime.date.fromisoformat(data_laudo)).days / 365.25
            if idade_anos > regras["validade_laudo_anos"]:
                achados.append({"tipo": "laudo_vencido", "severidade": "alerta",
                                 "sondagem": sond["id"], "idade_anos": round(idade_anos, 1),
                                 "limite_anos": regras["validade_laudo_anos"]})

        # 4. Nível d'água registrado
        if regras["exige_na_medido"] and sond.get("nivel_dagua_prof") is None:
            achados.append({"tipo": "na_nao_medido", "severidade": "alerta",
                             "sondagem": sond["id"]})

        # 5. Rastreabilidade mínima (responsável técnico / ART)
        if not sond.get("rastreabilidade", {}).get("responsavel_tecnico"):
            achados.append({"tipo": "sem_art_responsavel", "severidade": "bloqueante",
                             "sondagem": sond["id"]})

    # 6. Consistência entre furos vizinhos (outlier de NSPT)
    for anterior, atual in zip(ordenadas, ordenadas[1:]):
        prof_comuns = set(c["profundidade_m"] for c in anterior["camadas"]) & \
                      set(c["profundidade_m"] for c in atual["camadas"])
        for prof in prof_comuns:
            n1 = next((c["nspt"] for c in anterior["camadas"] if c["profundidade_m"] == prof), None)
            n2 = next((c["nspt"] for c in atual["camadas"] if c["profundidade_m"] == prof), None)
            if n1 is not None and n2 is not None and abs(n1 - n2) > regras["delta_nspt_suspeito"]:
                achados.append({"tipo": "nspt_inconsistente_entre_furos", "severidade": "alerta",
                                 "sondagens": [anterior["id"], atual["id"]],
                                 "profundidade_m": prof, "nspt_1": n1, "nspt_2": n2})

    bloqueantes = [a for a in achados if a["severidade"] == "bloqueante"]
    return {
        "total_achados": len(achados),
        "bloqueantes": len(bloqueantes),
        "liberado_para_projeto_executivo": len(bloqueantes) == 0,
        "achados": achados,
    }
```

Saída do `qa_qc_sondagem` deve ser anexada como capa do PDF de perfil
geotécnico composto (seção 6.8/`gerar_perfil_geotecnico_pdf`) sempre que
houver ao menos um achado "bloqueante" ou "alerta" — nunca liberar o
perfil silenciosamente quando `liberado_para_projeto_executivo` for falso.
```

---

## Checklist de aplicação (para quem for publicar)

- [x] Gate humano (MN) — **aprovado em 2026-09-12** (sessão de chat).
- [ ] Confirmar o caminho canônico do `SKILL.md` de `rodovias-geotecnia` em
      produção (SharePoint ou outro repositório operacional) — não
      confirmado nesta sessão.
- [ ] Colar o bloco da Seção A como novas seções 10–13 (ou 10–14 se
      Schemas for movido para o final).
- [ ] Estender `references/schema_sondagem.json` com os campos
      `ensaios`, `classificacao`, `baliza_uso`, `rastreabilidade`.
- [x] Teste de fumaça com dados sintéticos rodado em 2026-09-12: todas as
      funções das seções 10-13 executam sem exceção com casos-limite
      (NSPT ausente, cbr_min=None, sondagem sem prof_total, sem sondagem
      associada). Achou e corrigiu 3 bugs reais (categoria_dnit lido no
      campo errado do schema, checagem de profundidade que pulava
      sondagens sem cota_greide_m, "adequado" por omissão de dado em
      avaliar_fundacao_aterro) — ver histórico de commits.
- [ ] Ainda falta validar com dados de um projeto real (não sintéticos)
      antes de liberar para uso em projeto executivo.
- [x] Números de norma NBR/DNIT verificados por pesquisa web em
      2026-09-12 (3 agentes independentes, ver nota no início da
      seção 11) — confiança alta para números/títulos de norma,
      confiança média para os valores numéricos de CBR/expansão/IP
      (fontes secundárias, PDF oficial não acessível nesta sessão).
      `BALIZA_PADRAO_DNIT` já marca por linha quais valores são
      confirmados vs. placeholder de mercado.
- [x] Valores de `aterro_corpo` (CBR≥2%, expansão≤4%) e `aterro_coroamento`
      (expansão≤2%) confirmados por pesquisa web dedicada em 2026-09-12
      (DNIT 108/2009-ES) — confiança média-alta, PDF oficial ainda não
      lido diretamente (bloqueio de rede na sessão). CBR de
      `aterro_coroamento` confirmado como relativo/definido em projeto,
      não um valor fixo — corrigido de "6%" (não confirmado) para `None`
      + `especificacao_projeto` obrigatório, mesmo tratamento de
      `reforco_subleito`.
- [ ] Confirmar contra o PDF oficial do DNIT/IPR (ainda pendente,
      bloqueio de rede): expansão do reforço do subleito (1% vs. 2% —
      fontes divergem) e a tabela completa de CBR por faixa de tráfego N
      da base (DNIT 141/2022-ES) antes de uso em documento normativo
      formal ou disputa contratual.
- [ ] Confirmar se a especificação de terraplenagem/pavimentação do
      projeto em uso diverge da tabela `BALIZA_PADRAO_DNIT` (edital ou
      contrato podem definir CBR/IP mínimos próprios) — usar
      `especificacao_projeto` nesses casos, nunca sobrescrever o padrão
      global.
- [ ] Registrar a mudança no changelog da skill e no `CLAUDE.md` deste
      repositório (seção "GEOTECNIA RODOVIÁRIA — EXTENSÃO", já criada).
