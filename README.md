# pacel.li

Personal website for Vincent Pacelli, built with [Hugo](https://gohugo.io/).

## Prerequisites

- [Hugo](https://gohugo.io/getting-started/installing/) (extended edition recommended, v0.120+)
- Python 3.8+ (only needed for BibTeX → YAML conversion)
- `pybtex` and `pyyaml` Python packages (only needed for conversion)

## Quick Start

```bash
# Install Python dependencies (one-time, only for bib conversion)
pip install pybtex pyyaml

# Build the site
hugo server
```

Visit `http://localhost:1313` to preview.

## Project Structure

```
.
├── hugo.yaml                 # Site configuration
├── publications.bib          # BibTeX source of truth for publications
├── scripts/
│   └── bib2yaml.py           # Converts .bib → data/publications.yaml
├── content/
│   ├── _index.md             # Home page (bio, links — edit this!)
│   └── publications/
│       └── _index.md         # Publications page intro text
├── data/
│   ├── publications.yaml     # Generated from .bib — don't edit directly
│   └── research.yaml         # Research area cards (edit this!)
├── layouts/
│   ├── _default/
│   │   └── baseof.html       # Base HTML template
│   ├── index.html            # Home page template
│   ├── publications/
│   │   └── list.html         # Publications page template
│   └── partials/
│       ├── head.html         # <head> tag
│       ├── nav.html          # Navigation bar
│       ├── footer.html       # Footer
│       └── pub-entry.html    # Single publication card
└── static/
    ├── css/
    │   └── style.css         # All styles
    ├── cv/
    │   └── pacelli_cv.pdf    # Your CV (add this file)
    └── img/
        └── prof_pic.jpg      # Profile photo (add this file)
```

## Editing Content

### Bio / Home Page

Edit `content/_index.md`. The YAML front matter controls your name, subtitle,
profile image path, email, and external links. The Markdown body below `---`
is your bio text.

### Research Areas

Edit `data/research.yaml`. Each entry has a `title`, `description`, and list
of `tags`.

### Publications

1. Edit `publications.bib` — add, remove, or update entries.
2. Run the conversion script:
   ```bash
   python scripts/bib2yaml.py
   ```
3. The script writes `data/publications.yaml`, which the Hugo templates read.

You can add custom fields to BibTeX entries:
- `arxiv = {2412.12156}` — generates an arXiv link
- `note = {Oral}` or `note = {Submitted; Under Review}` — rendered as a badge
- `doi = {10.xxxx/...}` — generates a DOI link

### CV

Place your CV PDF at `static/cv/pacelli_cv.pdf`. The nav bar links to it
directly.

### Profile Photo

Place your photo at `static/img/prof_pic.jpg`. If the file is missing, a
placeholder with your initials is shown.

## Building for Production

```bash
hugo --minify
```

Output goes to `public/`. Deploy this directory to GitHub Pages, Netlify,
Cloudflare Pages, or any static host.

### GitHub Pages Deployment

Add this as `.github/workflows/deploy.yml`:

```yaml
name: Deploy Hugo site

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true
      - run: hugo --minify
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

## Customization

All colors, fonts, and spacing are controlled by CSS variables at the top of
`static/css/style.css`. The crimson accent can be swapped by changing
`--crimson`, `--crimson-dark`, and `--crimson-light`.
