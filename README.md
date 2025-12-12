# Web2Ebook

Convert web pages into beautiful, readable ebook formats (EPUB, PDF, MOBI) while preserving styling and metadata.

**Copyright (c) devsimsek**

> **Note:** This code was generated using a proprietary LLM created and experimented on by devsimsek.

## Features

✨ **Multiple Format Support**
- EPUB (widely compatible)
- PDF (universal format)
- MOBI (Kindle format, requires Calibre)

🎨 **Style Preservation**
- Maintains text formatting and structure
- Embeds images directly into ebooks
- Professional typography for reading
- Beautiful code block styling with dark theme

📚 **Smart Content Extraction**
- Automatically identifies main content
- Removes navigation, ads, and clutter
- Extracts and preserves metadata
- Filters out non-HTML files (images, PDFs, etc.)

🕷️ **Multi-Page Crawling**
- Crawl and combine multiple pages into one ebook
- Each page becomes a chapter
- Automatic table of contents generation
- Smart link following within same domain

🎭 **Cover Generation**
- Automatically generates beautiful covers from metadata
- Option to use custom cover images
- Gradient backgrounds with elegant typography

📝 **Metadata Support**
- Extracts title, author, description
- Preserves publication date and publisher
- Supports Open Graph and meta tags

## Installation

### Prerequisites

1. **Python 3.7+** is required

2. **For MOBI conversion** (optional): Install [Calibre](https://calibre-ebook.com/)
   - macOS: `brew install --cask calibre`
   - Ubuntu/Debian: `sudo apt-get install calibre`
   - Windows: Download from https://calibre-ebook.com/download

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests beautifulsoup4 lxml ebooklib reportlab Pillow html2text
```

## Usage

### Basic Usage

Convert a web page to all formats (EPUB, PDF, MOBI):

```bash
python web2ebook.py https://example.com/article
```

### Crawl Multiple Pages

Crawl and combine multiple pages into one ebook:

```bash
python web2ebook.py https://example.com/tutorial --crawl --max-pages 10
```

### Exclude URLs from Crawling

**Exclude specific URLs:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --exclude https://example.com/login https://example.com/contact
```

**Use wildcard patterns:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --exclude '*/comments' '*login*' '*/tag/*'
```

**Load exclusions from file:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --exclude-file exclude.txt
```

Example `exclude.txt`:
```
# Exclude login and admin pages
https://example.com/login
https://example.com/admin/*

# Exclude by pattern
*comment*
*/tag/*
*/category/*
```

### Include URLs for Targeted Crawling

**Include specific URLs only (whitelist):**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --include https://example.com/chapter-1.html https://example.com/chapter-2.html
```

**Use wildcard patterns to target specific content:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --include '*/chapter-*.html' 'https://example.com/docs/guide/*'
```

**Load inclusions from file:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --include-file include.txt
```

Example `include.txt`:
```
# Only crawl chapters, skip navigation
https://example.com/chapter-*.html
*/tutorial/part-*.html

# Or specific pages
https://example.com/intro.html
https://example.com/conclusion.html
```

**Combine include and exclude:**
```bash
# Include all chapters but exclude appendix chapters
python web2ebook.py https://example.com/book \
  --crawl \
  --include '*/chapter-*.html' \
  --exclude '*/chapter-appendix-*.html'
```

### Specify Output Formats

Convert to specific formats only:

```bash
# EPUB only
python web2ebook.py https://example.com/article --formats epub

# PDF and EPUB
python web2ebook.py https://example.com/article --formats pdf epub
```

### Custom Output Directory

```bash
python web2ebook.py https://example.com/article -o /path/to/output
```

### Cover Options

**Disable auto-generated cover:**
```bash
python web2ebook.py https://example.com/article --no-cover
```

**Use custom cover image:**
```bash
python web2ebook.py https://example.com/article --cover my_cover.png
```

### Complete Example

```bash
python web2ebook.py \
  https://example.com/my-article \
  --formats epub pdf \
  --output ./ebooks \
  --cover custom_cover.jpg \
  --crawl \
  --max-pages 20 \
  --exclude-file exclude.txt
```

## Command-Line Options

```
positional arguments:
  url                   URL of the web page to convert

optional arguments:
  -h, --help            Show help message and exit
  -f, --formats {epub,pdf,mobi}
                        Output formats (default: all formats)
  -o, --output OUTPUT   Output directory (default: current directory)
  --no-cover            Do not generate a cover image
  --cover COVER         Path to custom cover image
  --crawl               Crawl and convert multiple pages into one ebook
  --max-pages N         Maximum number of pages to crawl (default: 10)
  --exclude [URL ...]   URLs or patterns to exclude from crawling
  --exclude-file FILE   File containing URLs to exclude (one per line)
  --include [URL ...]   URLs or patterns to include when crawling (whitelist)
  --include-file FILE   File containing URLs to include (one per line)
```

## How It Works

1. **Download**: Fetches the web page content
2. **Extract**: Identifies main content and removes clutter
3. **Parse**: Extracts metadata (title, author, date, etc.)
4. **Process**: Cleans HTML and normalizes styling
5. **Generate**: Creates cover image (if enabled)
6. **Convert**: Produces ebook files in requested formats

## Output Examples

When you run:
```bash
python web2ebook.py https://example.com/article
```

You'll get:
```
Article_Title.epub
Article_Title.pdf
Article_Title.mobi
```

## Supported Websites

Web2Ebook works with most websites, but performs best with:

- Blog posts and articles
- Documentation pages
- News articles
- Tutorial pages
- Long-form content

It automatically detects and extracts content from common HTML structures and metadata formats (Open Graph, Schema.org, etc.).

## Styling

### EPUB
- Clean, readable typography
- Justified text alignment
- Proper heading hierarchy
- Responsive images
- Preserved links

### PDF
- Letter-size pages (8.5" x 11")
- Professional margins
- Title page with metadata
- Page breaks between sections
- Embedded cover image

### MOBI
- Kindle-optimized format
- Converted from EPUB
- Compatible with Kindle devices and apps

## Dependencies

- **requests**: HTTP library for downloading pages
- **beautifulsoup4**: HTML parsing and manipulation
- **lxml**: Fast XML and HTML parser
- **ebooklib**: EPUB file creation
- **reportlab**: PDF generation
- **Pillow**: Image processing and cover generation
- **html2text**: HTML to formatted text conversion
- **Calibre** (optional): Required for MOBI conversion

## Troubleshooting

### MOBI conversion fails

Make sure Calibre is installed and `ebook-convert` is in your PATH:

```bash
# Test if ebook-convert is available
ebook-convert --version
```

If not found, install Calibre and add it to your PATH.

### Font errors on cover generation

The script tries multiple font locations. If you get font warnings, it will fall back to default fonts. The cover will still be generated successfully.

### SSL/Certificate errors

If you encounter SSL errors, you may need to update your SSL certificates:

```bash
pip install --upgrade certifi
```

### Page download fails

- Check your internet connection
- Verify the URL is accessible
- Some sites may block automated requests

## Advanced Usage

### As a Python Module

You can also use Web2Ebook in your Python scripts:

```python
from web2ebook import Web2Ebook

# Basic conversion
converter = Web2Ebook('https://example.com/article')
results = converter.convert(formats=['epub', 'pdf'])

# With options
converter = Web2Ebook(
    url='https://example.com/article',
    output_dir='./output',
    generate_cover=True,
    custom_cover='my_cover.png'
)
results = converter.convert(formats=['epub'])

print(f"EPUB created: {results['epub']}")
```

### Custom Processing

You can also use individual components:

```python
from web2ebook import WebPageDownloader, MetadataExtractor, CoverGenerator

# Download page
downloader = WebPageDownloader('https://example.com/article')
html = downloader.download()

# Extract metadata
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
extractor = MetadataExtractor(soup, 'https://example.com/article')
metadata = extractor.extract()

# Generate cover
cover_gen = CoverGenerator(metadata)
cover_gen.generate('cover.png')
```

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

Copyright (c) devsimsek

## Support

For issues, questions, or suggestions, please open an issue on the repository.

## Changelog

### Version 1.0.0
- Initial release
- EPUB, PDF, and MOBI support
- Automatic cover generation
- Metadata extraction
- Style preservation
- Content cleaning and extraction

## Acknowledgments

Built with:
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB generation
- [ReportLab](https://www.reportlab.com/) for PDF creation
- [Calibre](https://calibre-ebook.com/) for MOBI conversion
- [Pillow](https://python-pillow.org/) for image processing

## Credits

This project was generated using a proprietary LLM created by devsimsek as part of ongoing AI experimentation.

---

**Made with ❤️ by devsimsek**