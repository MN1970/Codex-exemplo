"""
Registro SICRO (amostra) — Pacote A v0.1.
Amostra de códigos SICRO válidos. Em produção, plugar contra DB compartilhado.
"""

SICRO_CODES = [
    # Rodovias
    {"codigo": "0118180", "descricao": "Escavação em material de qualquer natureza, profundidade até 2 m", "categoria": "Movimento de terra"},
    {"codigo": "0118206", "descricao": "Escavação em material de qualquer natureza, profundidade maior que 2 m", "categoria": "Movimento de terra"},
    {"codigo": "0121040", "descricao": "Aterro com material de empréstimo, compactado", "categoria": "Movimento de terra"},
    {"codigo": "0201000", "descricao": "Preparo de sub-base com solo seleccionado", "categoria": "Pavimentação"},
    {"codigo": "0201001", "descricao": "Preparo de base granular", "categoria": "Pavimentação"},
    {"codigo": "0212000", "descricao": "Camada de base de concreto reciclado", "categoria": "Pavimentação"},
    {"codigo": "0301000", "descricao": "Pavimento de CBUQ - camada de rolamento", "categoria": "Pavimentação"},
    # Estruturas
    {"codigo": "0504000", "descricao": "Escavação de poço para fundação", "categoria": "Fundações"},
    {"codigo": "0505000", "descricao": "Sapata de concreto armado", "categoria": "Fundações"},
    # Pontes
    {"codigo": "0702010", "descricao": "Concreto fck 25 MPa, bombeado", "categoria": "Materiais"},
    # Saneamento
    {"codigo": "1401000", "descricao": "Escavação de vala para adutora", "categoria": "Saneamento"},
    {"codigo": "1402000", "descricao": "Assentamento de tubulação de PVC", "categoria": "Saneamento"},
]
