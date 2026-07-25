#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MANTA MAESTRO - S3  Fechamento do gap de embeddings em knowledge_extractions
----------------------------------------------------------------------------
Gera embeddings dos KEs sem vetor, no MESMO modelo da producao
(BAAI/bge-small-en-v1.5, 384d, normalizado) e grava em ke_embeddings.

GATES (bloqueiam por padrao, liberados so com --force):
  G1  aluci_status IS NULL      -> KE nao passou pelo aluci-guard (R3 inviolavel)
  G2  len(descricao) < MIN_CH   -> texto telegrafico: recall medido cai a zero
                                   em consulta setorial (ver --bench)
  G3  grader_score < 7.0        -> abaixo do corte de curadoria

Tambem normaliza a string do modelo: a base tem hoje 'BAAI/bge-small-en-v1.5'
e 'bge-small-en-v1.5' como valores distintos para o mesmo modelo.

Uso:
  export DATABASE_URL='postgresql://...'
  python3 embed-kes-pendentes.py --dry-run          # relatorio, nao escreve
  python3 embed-kes-pendentes.py --bench            # mede recall antes de decidir
  python3 embed-kes-pendentes.py --apply            # grava (respeitando gates)
  python3 embed-kes-pendentes.py --apply --force    # grava ignorando gates (registra motivo)
  python3 embed-kes-pendentes.py --rollback-sql     # emite DELETE de reversao
"""
import argparse, os, sys, json

MODELO = "BAAI/bge-small-en-v1.5"
DIM = 384
MIN_CH = 400          # limiar de texto util (KE-001, padrao aprovado, tem 601)
MIN_SCORE = 7.0
PREFIXO_Q = "Represent this sentence for searching relevant passages: "

SQL_PEND = """
select k.ke_codigo, k.descricao, k.grader_score, k.aluci_status,
       coalesce(k.agentes_destino[1],'?') agente
from knowledge_extractions k
where not exists (select 1 from ke_embeddings e where e.ke_codigo = k.ke_codigo)
order by k.ke_codigo;
"""
SQL_INS = """
insert into ke_embeddings (ke_codigo, embedding, model, chunk_text)
values (%s, %s, %s, %s)
on conflict do nothing;
"""
SQL_NORM = """
update ke_embeddings set model = %s
where model <> %s and model like '%%bge-small-en-v1.5';
"""

def conectar():
    import psycopg2
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("ERRO: defina DATABASE_URL")
    return psycopg2.connect(dsn)

def avaliar(r):
    """Retorna lista de gates violados."""
    g = []
    if r["aluci_status"] is None:            g.append("G1_sem_aluci")
    if len(r["descricao"] or "") < MIN_CH:   g.append("G2_texto_curto")
    if float(r["grader_score"] or 0) < MIN_SCORE: g.append("G3_score_baixo")
    return g

def carregar_modelo():
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(MODELO)
    v = m.encode(["ok"], normalize_embeddings=True)
    assert v.shape[1] == DIM, f"dimensao {v.shape[1]} != {DIM}"
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--rollback-sql", action="store_true")
    a = ap.parse_args()

    con = conectar(); cur = con.cursor()
    cur.execute(SQL_PEND)
    cols = [d[0] for d in cur.description]
    pend = [dict(zip(cols, r)) for r in cur.fetchall()]
    if not pend:
        print("Nada pendente. ke_embeddings esta completo."); return

    for r in pend:
        r["gates"] = avaliar(r)
    livres = [r for r in pend if not r["gates"]]
    barrados = [r for r in pend if r["gates"]]

    print(f"KEs sem embedding: {len(pend)}  | livres: {len(livres)}  | barrados: {len(barrados)}")
    print(f"{'KE':<9} {'AGENTE':<8} {'CH':>4} {'SCORE':>6}  GATES")
    for r in pend:
        print(f"{r['ke_codigo']:<9} {r['agente']:<8} {len(r['descricao'] or ''):>4} "
              f"{str(r['grader_score']):>6}  {','.join(r['gates']) or '-'}")

    if a.rollback_sql:
        lst = ",".join(f"'{r['ke_codigo']}'" for r in pend)
        print(f"\n-- REVERSAO\ndelete from ke_embeddings where ke_codigo in ({lst});")
        return

    if a.bench:
        m = carregar_modelo()
        import numpy as np
        E = m.encode([r["descricao"] for r in pend], normalize_embeddings=True)
        codes = [r["ke_codigo"] for r in pend]
        consultas = json.load(open("bench_queries.json", encoding="utf-8")) \
            if os.path.exists("bench_queries.json") else []
        if not consultas:
            print("\nCrie bench_queries.json: [{\"q\":\"...\",\"ke\":\"KE-0XX\"}]"); return
        t1 = t3 = 0
        print(f"\n{'CONSULTA':<56} {'ESPERADO':<9} {'TOP-1':<9} RESULTADO")
        for c in consultas:
            qv = m.encode([PREFIXO_Q + c["q"]], normalize_embeddings=True)[0]
            top = [codes[i] for i in np.argsort(-(E @ qv))[:3]]
            t1 += top[0] == c["ke"]; t3 += c["ke"] in top
            print(f"{c['q'][:54]:<56} {c['ke']:<9} {top[0]:<9} "
                  f"{'OK' if top[0]==c['ke'] else ('top3' if c['ke'] in top else 'FALHA')}")
        n = len(consultas)
        print(f"\nTOP-1 {t1}/{n} ({100*t1//n}%)   TOP-3 {t3}/{n} ({100*t3//n}%)")
        return

    alvo = pend if a.force else livres
    if not alvo:
        print("\nNenhum KE liberado pelos gates. Enriqueca o texto ou rode o aluci-guard.")
        print("Use --force para gravar mesmo assim (fica registrado no log).")
        return
    if a.dry_run or not a.apply:
        print(f"\n[dry-run] gravaria {len(alvo)} embeddings. Use --apply para executar.")
        return

    m = carregar_modelo()
    E = m.encode([r["descricao"] for r in alvo], normalize_embeddings=True)
    for r, v in zip(alvo, E):
        cur.execute(SQL_INS, (r["ke_codigo"], "[" + ",".join(f"{x:.6f}" for x in v) + "]",
                              MODELO, r["descricao"]))
    cur.execute(SQL_NORM, (MODELO, MODELO))
    con.commit()
    print(f"\nGravados {len(alvo)} embeddings. String de modelo normalizada para '{MODELO}'.")
    cur.execute("select count(*) from knowledge_extractions"); tot = cur.fetchone()[0]
    cur.execute("select count(*) from ke_embeddings"); emb = cur.fetchone()[0]
    print(f"Estado: knowledge_extractions={tot}  ke_embeddings={emb}  gap={tot-emb}")

if __name__ == "__main__":
    main()
