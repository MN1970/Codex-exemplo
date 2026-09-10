---
name: sessao-salvar
description: Salva um handoff da sessão atual no SharePoint da Manta para continuar o trabalho em outra plataforma Claude (Chat, Cowork ou Code). Use SEMPRE que o usuário disser "salvar sessão", "salvar handoff", "handoff", "vou continuar no Code", "vou continuar no Chat", "vou continuar no Cowork", "passa esse trabalho para o Code", "salvar contexto para continuar depois", ou pedir para transferir o trabalho atual para outra plataforma.
---

# Sessão → Salvar handoff

Destila o estado da sessão atual em um `HANDOFF.md` estruturado e sobe para o SharePoint, junto com os artefatos produzidos. Outra sessão Claude (em qualquer plataforma) retoma o trabalho com a skill `sessao-retomar`.

## Destino no SharePoint

- Site: `https://mnassociados.sharepoint.com/sites/Engenharia`
- Biblioteca: `04_IA`
- Convenção de caminho: `12_HANDOFFS/{projeto}/{AAAAMMDD-HHMM}/`
  - `{projeto}` = slug kebab-case do projeto (ex.: `pa2026-manta`, `portal-metro-l4`). Reutilizar slug existente se a pasta do projeto já existir — listar as pastas de `12_HANDOFFS` antes de criar uma nova.
  - `{AAAAMMDD-HHMM}` = data/hora atual (ex.: `20260901-1630`). Cada handoff é uma pasta autocontida.
  - Dentro da pasta: `HANDOFF.md` + anexos (artefatos da sessão).

Ferramentas: usar o servidor MCP do SharePoint conectado à sessão (tools `list_folders`, `create_folder`, `upload_file`). Se nenhuma ferramenta SharePoint estiver disponível, avisar o usuário para ativar o conector antes de prosseguir — não inventar alternativa.

## Passos

1. **Identificar o projeto.** Deduzir do contexto da conversa. Listar `12_HANDOFFS` na biblioteca `04_IA`; se existir pasta com slug equivalente, usar. Se houver dúvida real, perguntar ao usuário em uma linha.
2. **Destilar a sessão** no formato abaixo. Regra de ouro: escrever para um leitor que NÃO tem acesso a esta conversa. Nada de "como discutido acima". Registrar decisões E caminhos descartados.
3. **Criar as pastas** `12_HANDOFFS/{projeto}` (se não existir) e `12_HANDOFFS/{projeto}/{AAAAMMDD-HHMM}`.
4. **Subir o `HANDOFF.md`.**
5. **Subir os anexos**: artefatos produzidos na sessão que a próxima sessão vai precisar (HTML, planilhas, scripts, documentos). Artefatos publicados (artifact URL, site no ar) entram só como link na tabela de Artefatos. Arquivos que só existem localmente e não podem ser subidos: registrar o path na tabela com a observação "só existe na máquina local".
6. **Confirmar ao usuário**: caminho completo do handoff + instrução de retomada (`/sessao-retomar {projeto}` na outra plataforma, ou "retomar sessão do projeto {projeto}").

## Formato do HANDOFF.md

```markdown
---
projeto: <slug>
origem: <chat | cowork | code>
data: <AAAA-MM-DDTHH:MM>
autor: <e-mail do usuário>
---

# HANDOFF — <título curto>

## Objetivo
1–3 frases. O que se está tentando entregar.

## Estado atual
O que já foi feito, na ordem. O que foi validado e o que não foi.

## Decisões tomadas e porquês
- Decisão → motivo. Incluir caminhos descartados.

## Artefatos
| Artefato | Onde está | Observação |
|---|---|---|

## Contexto técnico necessário
IDs, URLs, nomes de bancos/sites/bibliotecas, convenções relevantes.

## Próximos passos
1. Passos concretos e executáveis, em ordem.

## Pendências / bloqueios
- Dependências externas, aprovações, informações faltantes.
```

## Regras

- NUNCA gravar senhas, tokens, chaves de API ou credenciais no handoff — apenas indicar onde encontrá-los (ex.: "chave no .env local", "token no gerenciador de senhas").
- O handoff é resumo destilado, não transcript. Máximo ~2 páginas; artefatos grandes vão como anexo, não colados no corpo.
- Se a sessão cobre mais de um projeto, gerar um handoff por projeto.
- Não sobrescrever handoffs anteriores — cada save cria pasta nova com timestamp novo.
