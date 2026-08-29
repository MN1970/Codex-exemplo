# assets/ — logo oficial da Manta

## Status atual

`logo-manta-placeholder.svg` é um **stand-in**, não o logo oficial. É o
monograma laranja "M" que a skill `padrao-manta` desenha de memória quando
não encontra um arquivo real — e é exatamente por isso que o logo sai
diferente a cada relatório gerado: cada geração é um redesenho novo, não
uma cópia de um arquivo fixo.

Nenhum arquivo real do logo (PNG/SVG oficial) foi localizado neste
repositório, no Google Drive ou no SharePoint da Manta durante a auditoria
de 2026-08-29 (ver `docs/DIAGNOSTICO-DESIGN-RELATORIOS.md`).

## Como substituir pelo logo real

1. Peça o arquivo oficial ao time de branding/marketing — de preferência
   **SVG** (vetor, nítido em qualquer tamanho) ou **PNG** em alta resolução
   com fundo transparente.
2. Suba o arquivo aqui via GitHub (**Add file → Upload files**) como
   `assets/logo-manta.svg` (ou `.png`). Isso preserva os bytes originais
   exatamente — nenhum modelo de IA deve "redesenhar" o logo a partir daqui.
3. Gere o base64 a partir do arquivo real (nunca escrito à mão):
   ```bash
   base64 -w0 assets/logo-manta.png > assets/logo-manta.base64.txt
   ```
4. Use esse base64 como `<img src="data:image/png;base64,...">` no header
   e no rodapé do template de relatório — é a forma correta de embutir o
   logo em artefatos HTML, já que eles não carregam imagens por URL externa
   de forma confiável.
5. Remova `logo-manta-placeholder.svg` e atualize as referências no
   template (`docs/mockups/relatorio-diagnostico-manta-maestro.html`) e na
   skill `padrao-manta` para apontar para o arquivo real.

Até que isso aconteça, qualquer relatório do Manta Maestro vai continuar
usando esse placeholder — consistente entre si, mas não é o logo oficial.
