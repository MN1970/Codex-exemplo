# Addendum pronto para deploy — Extensão de Geotecnia Rodoviária
## (perfil de cortes/aterros, baliza de uso de material, banco JSON consolidado, QA/QC de sondagens)

**Status:** 🟡 **proposta técnica — aguardando gate humano (MN) antes de aplicar.**
Ainda **não aplicada** à skill de produção. Diferente do addendum de
`proposta-comercial`, a skill `rodovias-geotecnia` **não vive neste
repositório** (`Codex-exemplo` só versiona os agentes verticais S6–S10 e o
registro mestre — ver `CLAUDE.md`, seção "Arquivos deste repositório") nem
foi confirmado seu caminho canônico no SharePoint nesta sessão. Antes de
publicar, localizar o `SKILL.md` de produção de `rodovias-geotecnia`
(provável local: `04_IA/Manta-Maestro/02-sub-skills/` no SharePoint, por
analogia ao padrão usado por `skill-proposta-comercial-SKILL.md`) e colar o
bloco da Seção A abaixo na posição indicada.

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
        categoria = camadas_superficiais[0].get("categoria_dnit", "indefinido") \
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

    if nspt_min is not None and nspt_min < 4:
        veredito = "solo de fundação mole/fofo — risco de ruptura/recalque"
        tratamentos = ["remoção e substituição do solo mole (se espessura <2 m)",
                        "colchão drenante + geotêxtil de separação",
                        "bermas de equilíbrio (contrapeso lateral)",
                        "PVDs (drenos verticais) + sobrecarga temporária, se espessura grande",
                        "aterro em etapas com monitoramento de recalque/poropressão"]
    elif nspt_min is not None and nspt_min < 8:
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
projeto (DNIT 108/2009-ES, DNIT 141/2010-ES, ou a especificação
particular do edital/contrato quando informada).

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

# ─── SUCS COMPLETO (USCS — ASTM D2487, correspondência NBR 6502/7250) ─────
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
# Critérios de referência DNIT 108/2009-ES (aterros) e DNIT 141/2010-ES
# (pavimentação) — sobrepor pela especificação particular do projeto
# (`especificacao_projeto`) quando o edital/contrato definir valores próprios.
BALIZA_PADRAO_DNIT = {
    "aterro_corpo":        {"cbr_min": 2,  "expansao_max": 4.0, "ip_max": None,  "gi_max": None},
    "aterro_coroamento":   {"cbr_min": 6,  "expansao_max": 2.0, "ip_max": None,  "gi_max": None},
    "reforco_subleito":    {"cbr_min": 8,  "expansao_max": 1.0, "ip_max": None,  "gi_max": None},
    "sub_base":            {"cbr_min": 20, "expansao_max": 1.0, "ip_max": 6,     "gi_max": 4},
    "base":                {"cbr_min": 60, "expansao_max": 0.5, "ip_max": 6,     "gi_max": 0},
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
    if cbr is None:
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

Checklist normativo (NBR 6484:2020, NBR 8036:1983, DNIT) executado
automaticamente sobre o conjunto de sondagens de um projeto, antes de
liberar o perfil geotécnico composto (seção 6) para uso em projeto
executivo.

```python
# Script: scripts/qa_qc_sondagem.py

REGRAS_QA_QC_PADRAO = {
    "espacamento_max_m": 300,        # malha padrão em greenfield (NBR 6484 sugere
                                       # revisar para 100–150 m em cortes altos/OAE)
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
        # 2. Profundidade mínima abaixo do greide
        cota_greide = sond.get("cota_greide_m")
        prof_min_exigida = regras["profundidade_min_relativa_greide"]
        if cota_greide is not None:
            prof_atingida_abaixo_greide = sond["cota_boca"] - prof_min_exigida - \
                                           (sond["cota_boca"] - sond["prof_total"])
            if sond["prof_total"] < prof_min_exigida and not sond.get("impenetravel_atingido"):
                achados.append({"tipo": "profundidade_insuficiente", "severidade": "bloqueante",
                                 "sondagem": sond["id"], "prof_total_m": sond["prof_total"],
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

- [ ] Gate humano (MN) — **pendente**.
- [ ] Confirmar o caminho canônico do `SKILL.md` de `rodovias-geotecnia` em
      produção (SharePoint ou outro repositório operacional) — não
      confirmado nesta sessão.
- [ ] Colar o bloco da Seção A como novas seções 10–13 (ou 10–14 se
      Schemas for movido para o final).
- [ ] Estender `references/schema_sondagem.json` com os campos
      `ensaios`, `classificacao`, `baliza_uso`, `rastreabilidade`.
- [ ] Validar `avaliar_baliza_uso` e `qa_qc_sondagem` com um projeto real
      antes de liberar para uso em projeto executivo (dados de teste
      ainda não rodados nesta sessão).
- [ ] Confirmar se a especificação de terraplenagem/pavimentação do
      projeto em uso diverge da tabela `BALIZA_PADRAO_DNIT` (edital ou
      contrato podem definir CBR/IP mínimos próprios) — usar
      `especificacao_projeto` nesses casos, nunca sobrescrever o padrão
      global.
- [ ] Registrar a mudança no changelog da skill e no `CLAUDE.md` deste
      repositório (seção "GEOTECNIA RODOVIÁRIA — EXTENSÃO", já criada).
