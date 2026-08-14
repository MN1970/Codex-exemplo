import argparse

from .comparador import comparar
from .io_planilha import carregar_estudo_csv
from .otimizador_lp import resolver_alocacao_otima
from .relatorio import gerar_relatorio


def main():
    parser = argparse.ArgumentParser(
        description="Auditor de otimalidade de estudos de movimento de terra (terraplenagem rodoviária)."
    )
    parser.add_argument("--trechos", required=True, help="CSV com volumes de corte/aterro por trecho")
    parser.add_argument("--jazidas", default=None, help="CSV com jazidas e bota-foras")
    parser.add_argument("--composicoes", default=None, help="CSV com composições de custo de execução")
    parser.add_argument("--custo-proposto", type=float, default=None, help="Custo total proposto no estudo (R$)")
    parser.add_argument("--saida", default=None, help="Arquivo de saída do relatório (padrão: stdout)")
    args = parser.parse_args()

    estudo = carregar_estudo_csv(
        caminho_trechos=args.trechos,
        caminho_jazidas=args.jazidas,
        caminho_composicoes=args.composicoes,
        custo_total_proposto=args.custo_proposto,
    )
    resultado = resolver_alocacao_otima(estudo)
    resultado = comparar(estudo, resultado)
    relatorio = gerar_relatorio(resultado)

    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as arquivo:
            arquivo.write(relatorio)
    else:
        print(relatorio)


if __name__ == "__main__":
    main()
