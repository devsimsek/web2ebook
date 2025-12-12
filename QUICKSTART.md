# Quick Start Guide

**Web2Ebook - Convert web pages to ebooks in seconds**

Copyright (c) devsimsek

> **Note:** This code was generated using a proprietary LLM created and experimented on by devsimsek.

## Installation (30 seconds)

```bash
# Clone or download the project
cd web2ebook

# Install dependencies (creates venv automatically)
make install
```

That's it! The Makefile will create a virtual environment and install everything.

## Your First Conversion (10 seconds)

### Single Page

```bash
make run URL=https://example.com/article
```

You'll get three files:

- `Article_Title.epub` - For most e-readers
- `Article_Title.pdf` - Universal format
- `Article_Title.mobi` - For Kindle (requires Calibre)

### Multi-Page Book (Crawl Mode)

```bash
make run URL=https://example.com/tutorial ARGS='--crawl --max-pages 10'
```

This will:

- 🕷️ Crawl up to 10 pages from the same domain
- 📚 Combine them into ONE ebook
- 📖 Each page becomes a chapter
- 📑 Automatic table of contents

## Common Use Cases

### 1. Convert a Blog Post to EPUB

```bash
make run URL=https://myblog.com/awesome-post ARGS='--formats epub'
```

### 2. Crawl Documentation Into One Book

```bash
make run URL=https://docs.example.com/guide ARGS='--crawl --max-pages 20'
```

### 3. Save to Specific Folder

```bash
make run URL=https://example.com/article ARGS='-o ~/Documents/Books'
```

### 4. No Cover Needed

```bash
make run URL=https://example.com/article ARGS='--no-cover'
```

### 5. Custom Cover Image

```bash
make run URL=https://example.com/article ARGS='--cover my_cover.png'
```

## Direct Python Usage

If you prefer to use Python directly:

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Single page
python web2ebook.py https://example.com/article

# Multi-page crawl
python web2ebook.py https://example.com/tutorial --crawl --max-pages 10

# Specific formats only
python web2ebook.py https://example.com/article --formats epub pdf
```

## Tips

✅ **Crawl Mode is Perfect For:**

- Multi-part tutorials
- Documentation sites
- Blog series
- Online books spread across pages

✅ **Single Mode is Best For:**

- Individual articles
- Single blog posts
- One-page documents

⚠️ **Note for MOBI:**

- Requires Calibre installed
- macOS: `brew install --cask calibre`
- Linux: `sudo apt-get install calibre`
- Windows: Download from https://calibre-ebook.com/

🎨 **Auto-generated covers:**

- Beautiful gradient backgrounds
- Extracted metadata
- Professional typography
- Or use your own with `--cover`

📄 **Smart Filtering:**

- Only crawls HTML pages
- Skips images, PDFs, CSS, JS files
- Stays within same domain

🖼️ **Image Handling:**

- Downloads and embeds images
- Shows up in your ebook
- No broken image links

💻 **Code Block Styling:**

- Dark theme for code blocks
- Syntax-friendly colors
- Monospace fonts
- Proper formatting

## Troubleshooting

**"Virtual environment not found"**

```bash
make install
```

**"ebook-convert not found"**

- Install Calibre for MOBI support
- Or skip MOBI: `ARGS='--formats epub pdf'`

**"Failed to download page"**

- Check your internet connection
- Verify the URL is accessible
- Some sites may block automated requests

**"SSL Certificate error"**

```bash
source .venv/bin/activate
pip install --upgrade certifi
```

## Makefile Commands

```bash
make help      # Show all commands
make install   # Create venv and install dependencies
make test      # Verify installation
make run       # Convert a URL (requires URL=...)
make example   # Show more examples
make clean     # Clean up generated files and venv
```

## Next Steps

📖 Read the full [README.md](README.md) for all features

💡 Check [examples.py](examples.py) for Python integration

🚀 Start converting your reading list!

---

**Made with ❤️ by devsimsek**

(Storllm checkpoint: v9.3, revision: 0jk356)
