"""
Registro de normas ABNT válidas — Pacote A v0.2.
Cobre seleção das normas mais comuns em infraestrutura.
Atualizar conforme necessário com o catálogo ABNT oficial.

v0.2 (2026-09-23, testes T3): títulos corrigidos (7590, 12212, 12214,
12215, 12217, 5356, 15749, 12266), removida a entrada inexistente
"NBR 60076" (a adoção brasileira da IEC 60076 é a série NBR 5356),
edições atualizadas (6118:2023, 6122:2019) e normas de uso comum
acrescentadas. `verificado: False` = título não conferido na fonte.
"""

NORMAS_ABNT = [
    # Rodovias, pavimentação e estruturas
    {"codigo": "NBR 7187", "titulo": "Projeto de pontes, viadutos e passarelas de concreto", "data": ""},
    {"codigo": "NBR 7188", "titulo": "Carga móvel rodoviária e de pedestres em pontes, viadutos, passarelas e outras estruturas", "data": ""},
    {"codigo": "NBR 6118", "titulo": "Projeto de estruturas de concreto", "data": "2023"},
    {"codigo": "NBR 6122", "titulo": "Projeto e execução de fundações", "data": "2019"},
    {"codigo": "NBR 6123", "titulo": "Forças devidas ao vento em edificações", "data": ""},
    {"codigo": "NBR 6484", "titulo": "Solo — Sondagem de simples reconhecimento com SPT", "data": ""},
    {"codigo": "NBR 8681", "titulo": "Ações e segurança nas estruturas", "data": "2003-11"},
    {"codigo": "NBR 8800", "titulo": "Projeto de estruturas de aço e de estruturas mistas de aço e concreto de edifícios", "data": ""},
    {"codigo": "NBR 9062", "titulo": "Projeto e execução de estruturas de concreto pré-moldado", "data": ""},
    {"codigo": "NBR 11682", "titulo": "Estabilidade de encostas", "data": ""},
    {"codigo": "NBR 12655", "titulo": "Concreto de cimento Portland — Preparo, controle, recebimento e aceitação", "data": ""},
    {"codigo": "NBR 7480", "titulo": "Aço destinado a armaduras para estruturas de concreto armado", "data": ""},
    {"codigo": "NBR 7483", "titulo": "Cordoalhas de aço para estruturas de concreto protendido", "data": ""},
    {"codigo": "NBR 9782", "titulo": "Amassamento de solo-cal para rodovias", "data": "1987-07", "verificado": False},
    # Ferrovias
    {"codigo": "NBR 7590", "titulo": "Trilho Vignole — Requisitos", "data": "2012-07 (cancelada)"},
    # Edificações
    {"codigo": "NBR 15575", "titulo": "Edificações habitacionais — Desempenho", "data": ""},
    {"codigo": "NBR 9050", "titulo": "Acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos", "data": ""},
    {"codigo": "NBR 5626", "titulo": "Sistemas prediais de água fria e água quente", "data": ""},
    {"codigo": "NBR 8160", "titulo": "Sistemas prediais de esgoto sanitário", "data": ""},
    {"codigo": "NBR 10844", "titulo": "Instalações prediais de águas pluviais", "data": ""},
    {"codigo": "NBR 16401", "titulo": "Instalações de ar-condicionado — Sistemas centrais e unitários", "data": ""},
    {"codigo": "NBR 10151", "titulo": "Acústica — Medição e avaliação de níveis de pressão sonora", "data": ""},
    # Abastecimento de água
    {"codigo": "NBR 12211", "titulo": "Estudos de concepção de sistemas públicos de abastecimento de água", "data": ""},
    {"codigo": "NBR 12212", "titulo": "Projeto de poço tubular para captação de água subterrânea", "data": "2017-09"},
    {"codigo": "NBR 12213", "titulo": "Projeto de captação de água de superfície para abastecimento público", "data": "1992-09"},
    {"codigo": "NBR 12214", "titulo": "Projeto de sistema de bombeamento de água para abastecimento público", "data": ""},
    {"codigo": "NBR 12215", "titulo": "Projeto de adutora de água para abastecimento público", "data": ""},
    {"codigo": "NBR 12216", "titulo": "Projeto de estação de tratamento de água para abastecimento público", "data": "1992-09"},
    {"codigo": "NBR 12217", "titulo": "Projeto de reservatório de distribuição de água para abastecimento público", "data": ""},
    {"codigo": "NBR 12218", "titulo": "Projeto de rede de distribuição de água para abastecimento público", "data": ""},
    {"codigo": "NBR 15527", "titulo": "Aproveitamento de água de chuva de coberturas para fins não potáveis", "data": ""},
    # Esgotamento sanitário
    {"codigo": "NBR 9648", "titulo": "Estudo de concepção de sistemas de esgotamento sanitário", "data": "1986-10"},
    {"codigo": "NBR 9649", "titulo": "Projeto de redes coletoras de esgoto sanitário", "data": "1986-10"},
    {"codigo": "NBR 9650", "titulo": "Projeto de estações elevatórias de esgoto sanitário", "data": "1986-10", "verificado": False},
    {"codigo": "NBR 9651", "titulo": "Projeto de sistemas de tratamento de esgoto sanitário", "data": "1986-10", "verificado": False},
    # Tratamento e qualidade de água
    {"codigo": "NBR 12209", "titulo": "Elaboração de projetos hidráulico-sanitários de estações de tratamento de esgotos sanitários", "data": "2011"},
    {"codigo": "NBR 10004", "titulo": "Resíduos sólidos - Classificação", "data": "2004-11"},
    {"codigo": "NBR 15645", "titulo": "Projeto de emissário submarino e subfluvial para disposição de efluentes", "data": "2008-10", "verificado": False},
    # Tubulações e sistemas prediais
    {"codigo": "NBR 12266", "titulo": "Projeto e execução de valas para assentamento de tubulação de água, esgoto ou drenagem urbana", "data": ""},
    {"codigo": "NBR 13969", "titulo": "Tanques sépticos - Unidades de tratamento complementar e disposição final do efluente líquido - Projeto, construção e operação", "data": "1997-12"},
    # Energia e transmissão
    {"codigo": "NBR 5422", "titulo": "Projeto de linhas aéreas de transmissão de energia elétrica", "data": ""},
    {"codigo": "NBR 5356", "titulo": "Transformadores de potência (série; adoção da IEC 60076)", "data": ""},
    {"codigo": "NBR 5410", "titulo": "Instalações elétricas de baixa tensão", "data": ""},
    {"codigo": "NBR 5419", "titulo": "Proteção contra descargas atmosféricas", "data": ""},
    {"codigo": "NBR 14039", "titulo": "Instalações elétricas de média tensão de 1,0 kV a 36,2 kV", "data": ""},
    {"codigo": "NBR 6979", "titulo": "Disjuntores de alta tensão", "data": "2013-07", "verificado": False},
    {"codigo": "NBR 8186", "titulo": "Disjuntores de média tensão", "data": "1983-12", "verificado": False},
    {"codigo": "NBR 15749", "titulo": "Medição de resistência de aterramento e de potenciais na superfície do solo em sistemas de aterramento", "data": "2009-08 (cancelada)"},
    # Óleo e gás
    {"codigo": "NBR 17505", "titulo": "Armazenamento de líquidos inflamáveis e combustíveis", "data": ""},
    # Barragens e mineração
    {"codigo": "NBR 13028", "titulo": "Mineração - Elaboração e apresentação de projeto de barragens para disposição de rejeitos, contenção de sedimentos e reservação de água", "data": "2017"},
    {"codigo": "NBR 13029", "titulo": "Mineração - Elaboração e apresentação de projeto de disposição de estéril em pilha", "data": ""},
    {"codigo": "NBR 13030", "titulo": "Elaboração e apresentação de projeto de reabilitação de áreas degradadas pela mineração", "data": ""},
]
