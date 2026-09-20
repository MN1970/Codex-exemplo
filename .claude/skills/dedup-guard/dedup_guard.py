#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dedup-guard — Detecta duplicacao e redundancia de informacao DENTRO de um
mesmo artefato HTML/React da Manta (mesma tabela/bloco/valor repetido em
mais de uma aba/tela, ou o mesmo rotulo com valores divergentes).

Ao contrario do consist-guard (que valida um documento especifico contra
valores canonicos fixados no CONFIG), este script nao tem nenhum valor de
negocio fixo — so thresholds de deteccao, validos para qualquer artefato.

Uso:
  python dedup_guard.py arquivo.html
  python dedup_guard.py            # usa o .html mais recente no diretorio atual
"""
import re, sys, glob, os, hashlib, difflib

# ===== CONFIG (thresholds de deteccao — nao sao valores de negocio) =====
MIN_BLOCK_CHARS = 40          # tamanho minimo de texto p/ um bloco (table/section) entrar na analise
SIMILARITY_THRESHOLD = 0.90   # ratio (difflib) acima do qual dois blocos viram "quase-duplicata"
MAX_BLOCKS_FOR_SIMILARITY = 250  # limite de blocos comparados par-a-par (evita custo quadratico em docs gigantes)
LABEL_VALUE_MIN_REPEATS = 3   # mesmo rotulo + mesmo valor repetido N+ vezes -> candidato a centralizar

LABEL_VALUE_RE = re.compile(
    r'([A-ZÀ-Ý][A-Za-zÀ-ÿ0-9 /\-\.]{2,40}?)\s*[:=]\s*'
    r'(R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d{1,3}(?:\.\d{3})*(?:,\d+)?%?)'
)


def strip_noise(html):
    html = re.sub(r"data:[^\"')\s]+", " ", html)
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    return html


def latest_html():
    fs = glob.glob("*.html")
    if not fs:
        return None
    return max(fs, key=os.path.getmtime)


def extract_top_level_blocks(html, tag):
    """Extrai blocos <tag>...</tag> no nivel mais externo (nao capta duplicatas
    internas de secoes aninhadas como se fossem blocos separados)."""
    open_re = re.compile(r"<%s\b[^>]*>" % tag, re.I)
    close_re = re.compile(r"</%s\s*>" % tag, re.I)
    blocks, pos = [], 0
    while True:
        m_open = open_re.search(html, pos)
        if not m_open:
            break
        start = m_open.start()
        depth = 1
        cursor = m_open.end()
        end = len(html)
        while depth > 0:
            nxt_open = open_re.search(html, cursor)
            nxt_close = close_re.search(html, cursor)
            if not nxt_close:
                end = len(html)
                break
            if nxt_open and nxt_open.start() < nxt_close.start():
                depth += 1
                cursor = nxt_open.end()
            else:
                depth -= 1
                cursor = nxt_close.end()
                end = nxt_close.end()
        blocks.append((tag, start, end, html[start:end]))
        pos = end
    return blocks


def plain_text(block_html):
    txt = re.sub(r"<[^>]+>", " ", block_html)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def line_of(html, offset):
    return html.count("\n", 0, offset) + 1


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else latest_html()
    if not path or not os.path.exists(path):
        print("ERRO: arquivo nao encontrado.")
        return 2
    raw = open(path, encoding="utf-8", errors="ignore").read()
    clean = strip_noise(raw)
    name = os.path.basename(path)

    R = []
    def ok(m): R.append(("OK", m))
    def flag(m): R.append(("FLAG", m))
    def err(m): R.append(("ERRO", m))

    # ---- 1) BLOCOS DUPLICADOS / QUASE-DUPLICADOS (table, section) ----
    blocks = []
    for tag in ("table", "section"):
        blocks += extract_top_level_blocks(clean, tag)

    candidates = []
    for tag, start, end, html_block in blocks:
        txt = plain_text(html_block)
        if len(txt) >= MIN_BLOCK_CHARS:
            candidates.append((tag, start, txt))

    if not candidates:
        ok("Nenhum bloco <table>/<section> com texto suficiente para analisar (ok se artefato for pequeno)")
    else:
        # exatas: agrupar por hash do texto normalizado
        by_hash = {}
        for tag, start, txt in candidates:
            h = hashlib.sha1(txt.lower().encode("utf-8")).hexdigest()
            by_hash.setdefault(h, []).append((tag, start, txt))

        exact_dup_starts = set()
        for h, group in by_hash.items():
            if len(group) > 1:
                lines = ", ".join("%s@L%d" % (tag, line_of(clean, start)) for tag, start, _ in group)
                excerpt = group[0][2][:80]
                flag("Bloco duplicado literalmente (%dx): %s — \"%s...\"" % (len(group), lines, excerpt))
                exact_dup_starts.update(start for _, start, _ in group)
            else:
                pass

        # quase-duplicatas: comparar pares que nao sao ja duplicata exata
        rest = [c for c in candidates if c[1] not in exact_dup_starts]
        if len(rest) > MAX_BLOCKS_FOR_SIMILARITY:
            flag("Muitos blocos (%d) — pulando checagem de quase-duplicata par-a-par (custo quadratico)" % len(rest))
        else:
            seen_pairs_flagged = 0
            for i in range(len(rest)):
                tag_i, start_i, txt_i = rest[i]
                for j in range(i + 1, len(rest)):
                    tag_j, start_j, txt_j = rest[j]
                    if tag_i != tag_j:
                        continue
                    if abs(len(txt_i) - len(txt_j)) / max(len(txt_i), len(txt_j)) > 0.3:
                        continue  # tamanhos muito diferentes, nao vale a pena comparar
                    ratio = difflib.SequenceMatcher(None, txt_i, txt_j).ratio()
                    if ratio >= SIMILARITY_THRESHOLD:
                        flag("Blocos quase-identicos (%.0f%% similar): %s@L%d <-> %s@L%d" % (
                            ratio * 100, tag_i, line_of(clean, start_i), tag_j, line_of(clean, start_j)))
                        seen_pairs_flagged += 1
            if seen_pairs_flagged == 0 and not any(len(g) > 1 for g in by_hash.values()):
                ok("Nenhum bloco duplicado ou quase-duplicado encontrado (%d blocos analisados)" % len(candidates))

    # ---- 2) e 3) ROTULO:VALOR — divergencia ou repeticao ----
    label_hits = {}
    for m in LABEL_VALUE_RE.finditer(clean):
        label_raw, value = m.group(1), m.group(2)
        label_norm = re.sub(r"\s+", " ", label_raw).strip().lower()
        label_hits.setdefault(label_norm, []).append((value.strip(), line_of(clean, m.start())))

    any_label_issue = False
    for label, hits in label_hits.items():
        if len(hits) < 2:
            continue
        values = {v for v, _ in hits}
        if len(values) > 1:
            any_label_issue = True
            detail = ", ".join("%s@L%d" % (v, l) for v, l in hits)
            err("Rotulo \"%s\" com valores DIVERGENTES: %s" % (label, detail))
        elif len(hits) >= LABEL_VALUE_MIN_REPEATS:
            any_label_issue = True
            lines = ", ".join("L%d" % l for _, l in hits)
            flag("Rotulo \"%s\" repetido %dx com o MESMO valor (%s) em: %s — considerar centralizar numa unica fonte" % (
                label, len(hits), hits[0][0], lines))
    if not any_label_issue:
        ok("Nenhum rotulo:valor divergente ou repetido em excesso encontrado")

    # ---- 4) IDs duplicados ----
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', raw)
    dup_ids = sorted({i for i in ids if ids.count(i) > 1})
    if dup_ids:
        err("id duplicado no HTML (%d ids distintos repetidos): %s" % (len(dup_ids), ", ".join(dup_ids[:15])))
    else:
        ok("Nenhum id duplicado no HTML")

    # RELATORIO
    nO = sum(1 for n, _ in R if n == "OK")
    nF = sum(1 for n, _ in R if n == "FLAG")
    nE = sum(1 for n, _ in R if n == "ERRO")
    print("=" * 64)
    print("dedup-guard · %s" % name)
    print("=" * 64)
    for niv, m in R:
        if niv != "OK":
            print({"FLAG": "  ⚠", "ERRO": "  ✗"}[niv] + " [" + niv + "] " + m)
    print("-" * 64)
    print("Resumo: %d OK · %d FLAG · %d ERRO" % (nO, nF, nE))
    print("Veredito: " + ("REPROVADO (inconsistencias)" if nE else ("REVISAR (duplicacoes)" if nF else "APROVADO")))
    return 1 if nE else 0


if __name__ == "__main__":
    sys.exit(main())
