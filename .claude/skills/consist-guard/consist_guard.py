#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consist-guard — Rotina de revisao de consistencia de um documento HTML
tecnico Manta (tese, laudo, parecer) antes de fechar ou enviar.
Verifica: integridade estrutural, consistencia numerica, logica de datas,
numeracao sequencial, pendencias e rastreabilidade — em QUALQUER versao (vNNN).

Este script NAO vem com nenhum valor de negocio pre-preenchido. Antes do
primeiro uso em um documento, preencha o bloco CONFIG abaixo com os valores
canonicos DESSE documento (quantum, datas-chave, numero de capitulos,
strings obsoletas, fontes exigidas). Sem isso, os respectivos checks ficam
marcados como "nao configurado" e nao validam nada.

Uso:
  python consist_guard.py                 # ultima versao tese-vNNN em ../_deploy
  python consist_guard.py arquivo.html    # versao especifica
"""
import re, sys, glob, os

DEPLOY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_deploy")

# ===== CONFIG — preencha com os valores canonicos do SEU documento =====
# Deixe um campo em branco (None / [] / "") para pular aquele check sem
# quebrar o script.
EXPECT = {
    "total_cIGV": None,      # total com imposto (ex.: total com IGV/ICMS) do documento fechado
    "subtotal_sIGV": None,   # subtotal sem imposto
    "A_sIGV": None,          # categoria A sem imposto
    "B_sIGV": None,          # categoria B sem imposto
    "C_sIGV": None,          # categoria C sem imposto
    "D_sIGV": None,          # categoria D sem imposto
    "fechas_orden": [],      # datas-chave, na ordem cronologica esperada, ex.: ["01/01/2025", "01/06/2025"]
    "capitulos": None,       # numero de capitulos esperado no sumario (toc)
}
FORBIDDEN = []               # strings obsoletas que NAO devem mais aparecer no documento fechado
DIVERGENCIAS_CITADAS = []    # valores/citacoes conhecidos como divergencia a resolver antes de fechar
PENDENCIAS_MARK = ["a cargar", "a confirmar"]  # termos genericos de pendencia usados em documentos Manta
FONTES_RASTREAVEIS = ["SharePoint"]  # fontes-chave que o documento deve citar (normas, pareceres, dictames, etc.)

def strip_b64(t):
    t = re.sub(r"data:[^\"')\s]+", " ", t)            # remove blobs base64
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return t

def latest_file():
    fs = glob.glob(os.path.join(DEPLOY, "*tese-v*.html"))
    if not fs: return None
    return max(fs, key=lambda f: int(re.search(r"tese-v(\d+)", f).group(1)) if re.search(r"tese-v(\d+)", f) else 0)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else latest_file()
    if not path or not os.path.exists(path):
        print("ERRO: arquivo não encontrado."); return 2
    raw = open(path, encoding="utf-8", errors="ignore").read()
    clean = strip_b64(raw)
    name = os.path.basename(path)
    R = []
    def ok(m): R.append(("OK", m))
    def flag(m): R.append(("FLAG", m))
    def err(m): R.append(("ERRO", m))

    # 1) ESTRUTURA (no raw)
    for tag in ("div", "section", "table"):
        a, b = raw.count("<%s" % tag), raw.count("</%s>" % tag)
        (ok if a == b else err)("Tags <%s> balanceadas: %d/%d" % (tag, a, b))
    (ok if raw.rstrip().endswith("</html>") else err)("Termina em </html>")

    # 2) VALORES OBSOLETOS (no clean)
    if not FORBIDDEN:
        ok("Lista de valores obsoletos nao configurada (FORBIDDEN vazio) — check pulado")
    else:
        for s in FORBIDDEN:
            n = clean.count(s)
            (ok if n == 0 else flag)("Obsoleto '%s': %dx" % (s, n))

    # 3) QUANTUM
    quantum_keys = ("total_cIGV","subtotal_sIGV","A_sIGV","B_sIGV","C_sIGV","D_sIGV")
    if all(EXPECT[k] is None for k in quantum_keys):
        ok("Quantum nao configurado (EXPECT vazio) — check pulado")
    else:
        for k in quantum_keys:
            v = EXPECT[k]
            if v is None:
                continue
            (ok if v in clean else flag)("Quantum %s=%s presente" % (k, v))

    # 4) DATAS (presença + ordem cronológica do texto canônico)
    if not EXPECT["fechas_orden"]:
        ok("Datas-chave nao configuradas — check pulado")
    else:
        pres = [f for f in EXPECT["fechas_orden"] if f in clean]
        (ok if pres == EXPECT["fechas_orden"] else flag)("Datas-chave (ordem): %s" % pres)

    # 5) NUMERAÇÃO sequencial
    if EXPECT["capitulos"] is None:
        ok("Numero de capitulos esperado nao configurado — check pulado")
    else:
        ints = sorted({int(n) for n in re.findall(r'class="toc-num">(\d+)\.</span>', clean)})
        (ok if ints == list(range(1, EXPECT["capitulos"]+1)) else flag)(
            "Capítulos toc: %s (esperado 1..%d)" % (ints, EXPECT["capitulos"]))

    # 6) PENDÊNCIAS marcadas
    for ph in PENDENCIAS_MARK:
        n = len(re.findall(re.escape(ph), clean, re.I))
        if n: flag("Pendência marcada '%s': %dx (a completar)" % (ph, n))
    ecx = len(re.findall(r"N°\s*x{2,}", clean)) + len(re.findall(r"EC\D{0,4}x{3,}", clean, re.I))
    (ok if ecx == 0 else flag)("Nº de EC en blanco (xxx): %d" % ecx)
    if not DIVERGENCIAS_CITADAS:
        ok("Lista de divergencias conhecidas nao configurada — check pulado")
    else:
        for pend in DIVERGENCIAS_CITADAS:
            if pend in clean: flag("Divergência citada: '%s' (a resolver)" % pend)

    # 7) RASTREABILIDADE (fontes-chave)
    if not FONTES_RASTREAVEIS:
        ok("Fontes rastreaveis nao configuradas — check pulado")
    else:
        for src in FONTES_RASTREAVEIS:
            (ok if src in clean else flag)("Fonte '%s' referenciada" % src)

    # RELATÓRIO
    nO=sum(1 for n,_ in R if n=="OK"); nF=sum(1 for n,_ in R if n=="FLAG"); nE=sum(1 for n,_ in R if n=="ERRO")
    print("="*64); print("consist-guard · %s" % name); print("="*64)
    for niv,m in R:
        if niv!="OK": print({"FLAG":"  ⚠","ERRO":"  ✗"}[niv]+" ["+niv+"] "+m)
    print("-"*64)
    print("Resumo: %d OK · %d FLAG · %d ERRO" % (nO,nF,nE))
    print("Veredito: " + ("REPROVADO (erros)" if nE else ("REVISAR (flags)" if nF else "APROVADO")))
    return 1 if nE else 0

if __name__ == "__main__":
    sys.exit(main())
