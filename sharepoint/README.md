# SharePoint mirror — Manta Maestro v4.3

Espelho versionado da pasta destino no SharePoint:

```
mnassociados.sharepoint.com/sites/Engenharia
  └── Documentos Compartilhados/
      └── 04_IA/
          └── Manta-Maestro/
              └── 01-agentes-fundamentais/
                  ├── agente-portos/       ← v4.2 (S6)
                  ├── agente-aeroportos/   ← v4.2 (S7)
                  ├── agente-saneamento/   ← v4.2 (S8)
                  ├── agente-energia/      ← v4.2 (S9)
                  ├── agente-barragens/    ← v4.2 (S10)
                  └── agente-sp-hub/       ← v4.3 (Manta 20 — SP Hub)
```

Cada subpasta aqui contém o `SKILL.md` pronto para upload. Ao concluir
a versão vigente, arrastar cada pasta inteira para o SP no path acima
(criando as pastas SP correspondentes primeiro — ver
`docs/DEPLOY-v4.2.md` seção 3.1; para a v4.3, seguir a spec canônica em
`docs/MANTA-20-SPHUB-SPEC-v2.0.md`).

Esse mirror existe para:
1. Versionar os SKILL.md com git (histórico + review).
2. Facilitar reuso entre agentes (basta copiar dessa pasta).
3. Permitir CI/CD futuro que sincronize automaticamente com o SP via Graph API.
