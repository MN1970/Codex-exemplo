---
name: sessao-retomar
description: "Retoma trabalho iniciado em outra plataforma Claude (Chat, Cowork ou Code) lendo o handoff mais recente do projeto no SharePoint da Manta. Use SEMPRE que o usuário disser \"retomar sessão\", \"retomar handoff\", \"continuar o que eu estava fazendo no Chat/Cowork/Code\", \"carregar o handoff\", \"puxa o contexto do SharePoint\", ou mencionar continuar um trabalho salvo de outra plataforma."
---

# Sessão → Retomar handoff

Localiza o handoff mais recente do projeto no SharePoint, carrega o estado destilado da sessão anterior e continua o trabalho a partir dos "Próximos passos".

## Origem no SharePoint

- Site: `https://mnassociados.sharepoint.com/sites/Engenharia`
- Biblioteca: `04_IA`
- Convenção de caminho: `12_HANDOFFS/{projeto}/{AAAAMMDD-HHMM}/HANDOFF.md` + anexos na mesma pasta.
- O handoff mais recente é a subpasta de maior nome (ordenação lexicográfica = cronológica).

Ferramentas: usar o servidor MCP do SharePoint conectado à sessão (tools `list_folders`, `list_files`, `read_document`, `download_file`). Se nenhuma ferramenta SharePoint estiver disponível, avisar o usuário para ativar o conector — não inventar alternativa.

## Passos

1. **Identificar o projeto.** Se o usuário passou o slug (ex.: `/sessao-retomar pa2026-manta`), usar direto. Se não, listar as pastas de `12_HANDOFFS` na biblioteca `04_IA` e: se o contexto da conversa tornar o projeto óbvio, usar; senão, mostrar a lista e perguntar.
2. **Localizar o handoff.** Listar as subpastas de `12_HANDOFFS/{projeto}` e pegar a de maior timestamp. Se o usuário pedir um handoff específico ("o de ontem"), escolher pela data no nome.
3. **Ler o `HANDOFF.md`** com `read_document`.
4. **Inventariar os anexos** da pasta (`list_files`). Baixar apenas os que os próximos passos exigem — não baixar tudo por padrão. No Claude Code, baixar para o diretório de trabalho do projeto; no Chat/Cowork, ler o conteúdo conforme a necessidade.
5. **Reportar ao usuário antes de agir**, em poucas linhas: objetivo, estado atual, e os próximos passos listados no handoff. Sinalizar qualquer pendência/bloqueio registrado.
6. **Executar os próximos passos** do handoff, na ordem, a menos que o usuário redirecione.

## Regras

- Handoffs anteriores do mesmo projeto são histórico: consultar apenas se o mais recente fizer referência a eles ou se o usuário pedir.
- Se a pasta do projeto não existir ou estiver vazia, dizer isso claramente e listar os projetos disponíveis — não inventar contexto.
- Artefatos marcados como "só existe na máquina local" podem não estar acessíveis na plataforma atual; sinalizar ao usuário quando um próximo passo depender deles.
- Ao concluir um bloco de trabalho relevante, sugerir salvar novo handoff com a skill `sessao-salvar` (fecha o ciclo entre plataformas).
