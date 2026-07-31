# Documentation CI/CD Pipeline

Configuração automática de geração e deploy de documentação usando markdown-para-HTML estático.

## Arquivos Criados

- **GitHub**: `.github/workflows/docs.yml` (GitHub Actions)
- **GitLab**: `.gitlab-ci.yml` (GitLab CI/CD)
- **Documentação**: Este arquivo

## Como Funciona

### Triggers

Ambos os pipelines disparam quando:

1. **Mudanças em arquivos-chave**:
   - `README.md` — homepage da documentação
   - `ARCHITECTURE.md` — documentação arquitetural
   - `docs/**/*.md` — qualquer markdown em pasta `docs/`
   - `.github/workflows/docs.yml` ou `.gitlab-ci.yml` — próprio pipeline

2. **Branches**:
   - `main` → Deploy automático
   - `develop` → Build + preview
   - Pull/Merge Requests → Build + verificação
   - Manual (`workflow_dispatch` no GitHub)

### Build Process

```
1. Checkout código
2. Instalar dependências (pandoc, Node.js)
3. Criar estrutura de pastas (docs_build/)
4. Converter Markdown → HTML5:
   - README.md → index.html
   - ARCHITECTURE.md → pages/architecture.html
   - docs/*.md → pages/*.html
5. Injetar CSS e navegação
6. Gerar sitemap.txt
7. Criar build-info.json (metadados)
8. Upload artefato/artifact
```

### Deploy

#### GitHub Pages (GitHub)

```yaml
- Build no Ubuntu latest
- Upload artifact para GitHub Pages
- Deploy automático em https://<username>.github.io/<repo>/
- Acesso ao branch: main
```

#### GitLab Pages (GitLab)

```yaml
- Build no Alpine Linux
- Move docs_build/ → public/
- Deploy automático em https://<namespace>.gitlab.io/<project>/
- Preview para branches (non-main)
- Acesso ao branch: main (production)
```

## Estrutura de Saída

```
docs_build/
├── index.html                 # Homepage (from README.md)
├── sitemap.txt                # Sitemap para crawlers
├── build-info.json            # Metadados do build
├── assets/
│   ├── css/
│   │   └── style.css          # Stylesheet (light/dark mode)
│   └── js/
│       └── (scripts aqui)
└── pages/
    ├── architecture.html      # (from ARCHITECTURE.md)
    └── *.html                 # (from docs/*.md)
```

## Styling

O CSS gerado inclui:

- **Design responsivo** (mobile-first)
- **Dark mode** via `prefers-color-scheme`
- **Navegação simples** (header + nav bar)
- **Tipografia legível** (system fonts)
- **Tabelas, código, blockquotes** formatados
- **Links e hover states**

### Cores padrão

- Primária: `#3498db` (azul)
- Background: `#f5f5f5` (claro) / `#1a1a1a` (escuro)
- Texto: `#333` / `#e0e0e0`

## Configuração Recomendada

### Para GitHub

1. Habilitar **Pages** em Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` (criado automaticamente)
4. Pasta: `/ (root)`

### Para GitLab

1. Habilitar **Pages** em Settings → CI/CD → Pages
2. Verificar permissões de CI/CD
3. Pages serão acessíveis após merge para `main`

## Variáveis de Ambiente

### GitHub
Nenhuma configuração adicional necessária.

### GitLab

Opcionalmente adicionar em CI/CD → Variables:

```
DOC_BUILD_DIR = docs_build
CI_PAGES_URL = https://<namespace>.gitlab.io/<project>
```

## Comandos Locais

Para testar localmente sem CI/CD:

```bash
# Instalar pandoc
brew install pandoc          # macOS
apt install pandoc           # Linux
choco install pandoc         # Windows

# Build
mkdir -p docs_build/{assets/css,pages}
pandoc README.md -o docs_build/index.html --css="assets/css/style.css" --standalone

# Servir localmente
cd docs_build
python -m http.server 8000
# Acessar: http://localhost:8000
```

## Troubleshooting

### Docs não aparecem depois de push?

1. **GitHub**: Esperar 1-2 min, verificar Actions tab
2. **GitLab**: Verificar Deployments → Environments
3. Limpar cache do navegador (Ctrl+Shift+Del)

### Build falha com erro de Markdown?

- Verificar sintaxe com `pandoc --from markdown <file>`
- Usar YAML frontmatter correto se necessário
- Ver logs no CI/CD dashboard

### CSS não carrega?

- Verificar paths relativos em `<link>`
- Para pages/: use `../assets/css/style.css`
- Para root: use `assets/css/style.css`

## Expansão Futura

Possíveis melhorias:

- [ ] Gerar TOC (table of contents) automático
- [ ] Tema customizável via variáveis CSS
- [ ] Busca full-text em docs (JS + indexação)
- [ ] Versionamento de docs (v1.0, v2.0, etc)
- [ ] Integração com ReadTheDocs
- [ ] Análise de cobertura de docs
- [ ] Deploy em AWS S3 / Netlify / Vercel

## Referências

- [Pandoc Manual](https://pandoc.org/MANUAL.html)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [GitLab Pages Docs](https://docs.gitlab.com/ee/user/project/pages/)
- [CSS Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries)
