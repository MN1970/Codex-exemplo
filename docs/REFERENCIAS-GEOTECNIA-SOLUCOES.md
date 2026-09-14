# Referências — Engenheiros, Obras e Métodos de Dimensionamento Geotécnico

Levantamento de referência (autores brasileiros e internacionais, obras
canônicas, área de atuação e método de dimensionamento) para soluções
geotécnicas de solo mole, contenção, fundações (incl. fundações de
pontes/OAE), rodovias, túneis, metrôs e ferrovias.

Uso pretendido: fonte inicial para a coleção RAG do agente vertical de
infraestrutura (Manta 03-S1..S4 — `agente-infraestrutura`, que vive no
repositório operacional do Maestro, fora deste repo) e para consulta
direta por qualquer agente/skill que precise citar referência técnica em
geotecnia.

---

## Tabela consolidada

| Autor(es) | Obra(s) de referência | Área de atuação | Solução geotécnica | Método de dimensionamento |
|---|---|---|---|---|
| Márcio de S. S. de Almeida (COPPE/UFRJ) + Maria Esther S. Marques | *Aterros sobre Solos Moles* (Oficina de Textos) | Solo mole, geotecnia marinha, instrumentação | Drenos verticais (geodrenos) + pré-carga | Teoria do adensamento radial de Barron (dissipação de poropressão) |
| idem | idem | idem | Colunas granulares | Analogia com drenos verticais + redistribuição de tensão (arqueamento) |
| idem | idem | idem | Aterro reforçado com geossintético na base | Equilíbrio limite (estabilidade global) + tração admissível do geossintético |
| idem + Ennio Palmeira (UnB) | *Geossintéticos em Geotecnia e Meio Ambiente* | Reforço de solo, geossintéticos | Aterro estaqueado / plataforma de transferência de carga | Terzaghi (1943, efeito arco); Hewlett & Randolph (1988, adotado no BS8006:2010 e no guia francês ASIRI); Russell & Pierpoint (1997, adaptação de Terzaghi com Ka=1); norma BS8006 |
| Ennio Marques Palmeira (UnB, ABC, membro honorário IGS) | *Geossintéticos em Geotecnia e Meio Ambiente*; 350+ artigos | Geossintéticos (reforço, filtração, drenagem) | Reforço de taludes/muros em solo reforçado | Equilíbrio limite + verificação de tração/ancoragem do geossintético; base normativa NBR |
| Nelson Aoki (USP São Carlos) + Dirceu de Alencar Velloso (Estacas Franki/Promon) | Método Aoki-Velloso (1975), Congresso Panamericano de Mecânica dos Solos | Fundações profundas | Estacas (cravadas, hélice, escavadas) | Método Aoki-Velloso: capacidade de carga R = RL (atrito lateral) + RP (ponta), correlacionado a SPT/CPT via fatores F1/F2 |
| Dirceu A. Velloso + Francisco de Rezende Lopes | *Fundações* (Vol. I e II) | Fundações em geral, obras especiais, fundações de pontes/OAE | Fundações de pontes/OAE | Aoki-Velloso e Décourt-Quaresma (1978, também base N-SPT); complementados por Teixeira (1996) e Lobo (2005) |
| José Carlos A. Cintra (USP São Carlos) | *Fundações Diretas: Projeto Geotécnico*; *Fundações por Estacas: Projeto Geotécnico* | Fundações diretas e por estacas | Sapatas / fundações diretas | Teoria clássica de capacidade de carga (Terzaghi, Meyerhof) + recalque admissível |
| Fernando Schnaid (UFRGS; fundador da Rhama Analysis) | *In Situ Testing in Geomechanics* (Routledge); *Ensaios de Campo* | Ensaios in situ, geotecnia de barragens/rejeitos | Investigação geotécnica (SPT, CPTu, DMT) — insumo para todos os dimensionamentos acima | Correlações CPTu/DMT/SPT para parâmetros de resistência e compressibilidade |
| Norma técnica (sem autoria individual) | NBR 16920-2/2021 — Muros e taludes em solos reforçados, Parte 2: Solos grampeados | Contenção | Solo grampeado | Ábacos do método Clouterre (1991); equilíbrio limite (Bishop simplificado, Sarma, Janbu); método alemão de Stocker (1979) |
| Prática consolidada de mercado (Rankine/Coulomb) | — | Contenção | Cortina atirantada | Empuxo ativo/passivo (Rankine/Coulomb) + capacidade de ancoragem dos tirantes (ensaio de arrancamento) |
| CBT — Comitê Brasileiro de Túneis (ABMS, fundado 1990); presidência 2023-24 Daniela Garroux; diretor Edson Peev | Normas/publicações técnicas do comitê | Túneis (NATM/TBM), metrôs | Escavação NATM | Classificação geomecânica RMR (Bieniawski) e Sistema Q (Barton, 1974) → definição de suporte; método de convergência-confinamento para dimensionamento de revestimento |
| Vinicius Zamai Seva (Linha 6-Laranja, Metrô SP, 2020-2024) | Campanhas de investigação geotécnica urbana | Metrô, investigação de subsolo urbano | Programa de sondagens/instrumentação em obra subterrânea urbana | Define o programa de investigação (SPT/CPTu + instrumentação) que alimenta o RMR/Q e a análise numérica (ex. Plaxis) |
| Victor F. B. de Mello | Vasta obra técnica; fundador ABMS; presidente ISSMGE 1981-85 | Geotecnia geral; geotecnia de barragens/metrô SP (Linha 1) | Referência histórica transversal | — |

### Referências internacionais clássicas (contexto)

| Autor | Contribuição | Relevância |
|---|---|---|
| Karl Terzaghi | *Erdbaumechanik* (1925) | Base da mecânica dos solos moderna; teoria de adensamento e capacidade de carga |
| Arthur Casagrande | Harvard | Ensaios de laboratório, formação de geração de engenheiros (incl. Ralph Peck) |
| Ralph B. Peck | *Soil Mechanics in Engineering Practice* | Método observacional |
| Alec Skempton | Imperial College London | Resistência de solos, taludes |
| Laurits Bjerrum | 1º diretor do Norwegian Geotechnical Institute (NGI) | Barragens, taludes, terremotos |
| Z.T. Bieniawski | Sistema RMR (Rock Mass Rating) | Classificação geomecânica para suporte de túneis |
| N. Barton et al. | Sistema Q (Tunnelling Quality Index, 1974) | Classificação geomecânica escandinava, base do método norueguês (NTM) |

---

## Resumo rápido por solução → método

- **Solo mole / adensamento** → Teoria de Barron (drenos verticais), Terzaghi (adensamento 1D clássico).
- **Aterro estaqueado** → Terzaghi (arqueamento) → Hewlett & Randolph → BS8006; alternativa Russell & Pierpoint.
- **Fundações por estaca** → Aoki-Velloso e Décourt-Quaresma (métodos semiempíricos dominantes no Brasil, calibrados com SPT).
- **Solo grampeado** → Clouterre (ábacos) + equilíbrio limite (Bishop/Sarma/Janbu); normatizado pela NBR 16920-2/2021.
- **Cortina atirantada** → Empuxo de terra clássico (Rankine/Coulomb) + ensaio de arrancamento dos tirantes.
- **Túneis NATM/TBM** → Classificação de maciço (RMR/Q) define a classe de suporte; convergência-confinamento dimensiona o revestimento.

---

## Fontes consultadas (busca na internet, 2026-09)

- [Aterros sobre Solos Moles - Oficina de Textos](https://www.ofitexto.com.br/aterros-sobre-solos-moles-2-ed/p)
- [Márcio Souza Soares de Almeida - Academia Nacional de Engenharia](https://anebrasil.org.br/m%C3%A1rcio-souza-soares-de-almeida/)
- [Ennio Marques Palmeira – ABC](https://www.abc.org.br/membro/ennio-marques-palmeira/)
- [Livro Geossintéticos em geotecnia e meio ambiente - Oficina de Texto](https://www.ofitexto.com.br/geossinteticos-em-geotecnia-e-meio-ambiente/p)
- [Nelson Aoki - Blog Ofitexto](https://blog.ofitexto.com.br/autores/nelson-aoki/)
- [Fundações Velloso e Lopes Vol. I](https://pdfcoffee.com/fundaoes-velloso-e-lopes-vol-ipdf-pdf-free.html)
- [Livro Fundações por estacas: projeto geotécnico - Oficina de Texto](https://www.ofitexto.com.br/fundacoes-por-estacas/p)
- [Professor Fernando Schnaid – PPGEC-UFRGS](https://www.ufrgs.br/ppgec/professor-fernando-schnaid/)
- [Fernando Schnaid | Engenheiro Civil](https://fernandoschnaid.com.br/institucional/)
- [Quem somos | Rhama Analysis](https://www.rhama-analysis.com/quem-somos)
- [Solo Grampeado no Brasil: Histórico, aplicações práticas e avanços (2003-2023) - Zenodo](https://zenodo.org/records/13987946)
- [Como dimensionar uma contenção em Solo Grampeado – Além da Inércia](https://alemdainercia.com/2018/04/09/como-dimensionar-uma-contencao-em-solo-grampeado/)
- [German Recommendations for Reinforced Embankments on Pile-Similar Elements](https://www.researchgate.net/publication/226292694_German_Recommendations_for_Reinforced_Embankments_on_Pile-Similar_Elements)
- [Presidente do Comitê Brasileiro de Túneis - ABMS](https://www.abms.com.br/noticia/presidente-do-comite-brasileiro-de-tuneis)
- [Sistema Q (Barton) - Sistemas de Classificações Geomecânicas](https://1library.org/article/sistema-q-barton-sistemas-de-classifica%C3%A7%C3%B5es-geomec%C3%A2nicas.q7560dkz)
- [Engenharia geotécnica e infraestrutura de grande porte - Universo de Negócios](https://universodenegocios.com.br/engenharia-geotecnica-e-infraestrutura-de-grande-porte/)
- [A vida e a obra de Victor Froilano Bachmann de Mello](https://cbdb.org.br/a-vida-e-a-obra-de-victor-froilano-bachmann-de-mello)

**Nota:** este documento é um levantamento de apoio, não uma norma. Antes
de citar qualquer método em laudo/parecer técnico, validar contra a
skill `aluci-guard` (auditoria anti-alucinação de normas/referências) e
contra a fonte primária (norma ABNT vigente ou publicação original).
