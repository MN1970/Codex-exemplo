#!/usr/bin/env python3
"""quickXorHash (algoritmo do OneDrive/SharePoint) de arquivos locais.

Uso: python3 scripts/sp_quickxorhash.py ARQUIVO [ARQUIVO ...]

Imprime o hash em base64, no mesmo formato de `hashes.quickXorHash` que o
SharePoint devolve em get_file_metadata. Serve para conferir, depois de um
upload, que o arquivo publicado é byte a byte igual ao do repositório.
"""
import base64
import sys

WIDTH = 160
SHIFT = 11


def quickxorhash(data: bytes) -> str:
    acc = 0
    for i, byte in enumerate(data):
        bit = (i * SHIFT) % WIDTH
        acc ^= byte << bit
        if bit + 8 > WIDTH:
            acc ^= byte >> (WIDTH - bit)
    acc &= (1 << WIDTH) - 1
    out = bytearray(acc.to_bytes(20, "little"))
    for j, b in enumerate(len(data).to_bytes(8, "little")):
        out[12 + j] ^= b
    return base64.b64encode(bytes(out)).decode()


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, "rb") as fh:
            print(quickxorhash(fh.read()), path)
