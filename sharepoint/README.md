# SharePoint mirror — Manta Maestro v4.2

Espelho versionado da pasta destino no SharePoint:

```
mnassociados.sharepoint.com/sites/Engenharia
  └── Documentos Compartilhados/
      └── 04_IA/
          └── Manta-Maestro/
              └── 01-agentes-fundamentais/
                  ├── agente-portos/       ← este mirror
                  ├── agente-aeroportos/   ← este mirror
                  ├── agente-saneamento/   ← este mirror
                  ├── agente-energia/      ← este mirror
                  └── agente-barragens/    ← este mirror
```

Cada subpasta aqui contém o `SKILL.md` pronto para upload. Ao concluir
a v4.2, arrastar cada pasta inteira para o SP no path acima
(criando as pastas SP correspondentes primeiro — ver
`docs/DEPLOY-v4.2.md` seção 3.1).

Esse mirror existe para:
1. Versionar os SKILL.md com git (histórico + review).
2. Facilitar reuso entre agentes (basta copiar dessa pasta).
3. Permitir CI/CD futuro que sincronize automaticamente com o SP via Graph API.
