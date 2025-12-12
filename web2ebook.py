#!/usr/bin/env python3
"""
web2ebook - Convert web pages to ebook formats (EPUB, PDF, MOBI)

Copyright (c) devsimsek

This script downloads web pages and converts them into readable ebook formats
while preserving styling, metadata, and generating optional cover images.
"""

import os
import sys
import argparse
import requests
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
import hashlib
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from ebooklib import epub
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image as PILImage, ImageDraw, ImageFont
import html2text


class WebPageDownloader:
    """Downloads and processes web pages with assets"""

    def __init__(self, url, user_agent=None):
        self.url = url
        self.base_url = self._get_base_url(url)
        self.session = requests.Session()
        # Connection pooling for speed
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_base_url(self, url):
        """Extract base URL from full URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def download(self):
        """Download the web page content"""
        try:
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            # Ensure proper encoding
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to download page: {e}")
    
    def download_image(self, img_url):
        """Download an image and return bytes with proper content type"""
        try:
            # Make URL absolute
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(self.url, img_url)
            
            response = self.session.get(img_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not any(t in content_type for t in ['image/', 'octet-stream']):
                return None
            
            content = response.content
            # Verify it's not empty or too small
            if len(content) < 100:
                return None
                
            return content
        except Exception as e:
            return None


class MetadataExtractor:
    """Extract metadata from web pages"""

    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    def extract(self):
        """Extract all relevant metadata"""
        metadata = {
            'title': self._get_title(),
            'author': self._get_author(),
            'description': self._get_description(),
            'publisher': self._get_publisher(),
            'date': self._get_date(),
            'language': self._get_language(),
            'keywords': self._get_keywords(),
            'url': self.url
        }
        return metadata

    def _get_title(self):
        """Extract page title"""
        # Try Open Graph
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return self._clean_title(og_title['content'])

        # Try Twitter Card
        twitter_title = self.soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return self._clean_title(twitter_title['content'])

        # Try regular title tag
        title_tag = self.soup.find('title')
        if title_tag:
            return self._clean_title(title_tag.get_text().strip())

        # Try first h1 tag
        h1_tag = self.soup.find('h1')
        if h1_tag:
            return self._clean_title(h1_tag.get_text().strip())

        return "Untitled Document"

    def _clean_title(self, title):
        """Clean up title by removing version numbers and weird formatting"""
        if not title:
            return "Untitled Document"
        
        # Fix common encoding issues
        title = title.replace('â', "'").replace('â', '"').replace('â', '"')
        title = title.replace('â', '—').replace('â¢', '•').replace('Â', '')
        
        # Remove version numbers at the start (e.g., "30.3.7", "1.2.3")
        title = re.sub(r'^\d+(\.\d+)*\.?\s*', '', title)
        
        # Remove common separators and site names at the end
        title = re.split(r'\s*[\|•·\-–—]\s*', title)[0]
        
        # Clean up whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize first letter if all lowercase or all uppercase
        if title.islower() or title.isupper():
            title = title.title()
        
        return title or "Untitled Document"

    def _get_author(self):
        """Extract author information"""
        # Try meta author tag
        author_tag = self.soup.find('meta', attrs={'name': 'author'})
        if author_tag and author_tag.get('content'):
            return author_tag['content']

        # Try article:author
        article_author = self.soup.find('meta', property='article:author')
        if article_author and article_author.get('content'):
            return article_author['content']

        # Try to find author in common HTML patterns
        author_selectors = [
            {'class': re.compile(r'author', re.I)},
            {'itemprop': 'author'}
        ]

        for selector in author_selectors:
            author_elem = self.soup.find(['span', 'div', 'a', 'p'], selector)
            if author_elem:
                return author_elem.get_text().strip()

        return "Unknown Author"

    def _get_description(self):
        """Extract page description"""
        # Try meta description
        desc_tag = self.soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            return desc_tag['content']

        # Try Open Graph
        og_desc = self.soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content']

        return ""

    def _get_publisher(self):
        """Extract publisher information"""
        publisher_tag = self.soup.find('meta', property='og:site_name')
        if publisher_tag and publisher_tag.get('content'):
            return publisher_tag['content']

        # Try to extract from URL
        parsed = urlparse(self.url)
        return parsed.netloc

    def _get_date(self):
        """Extract publication date"""
        # Try article:published_time
        date_tag = self.soup.find('meta', property='article:published_time')
        if date_tag and date_tag.get('content'):
            return date_tag['content']

        # Try time tag
        time_tag = self.soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']

        return datetime.now().isoformat()

    def _get_language(self):
        """Extract language"""
        html_tag = self.soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang']

        lang_tag = self.soup.find('meta', attrs={'http-equiv': 'content-language'})
        if lang_tag and lang_tag.get('content'):
            return lang_tag['content']

        return 'en'

    def _get_keywords(self):
        """Extract keywords"""
        keywords_tag = self.soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            return keywords_tag['content']

        return ""


class CoverGenerator:
    """Generate ebook covers from metadata"""

    def __init__(self, metadata, width=800, height=1200):
        self.metadata = metadata
        self.width = width
        self.height = height

    def generate(self, output_path):
        """Generate a cover image"""
        # Create a new image with a gradient background
        img = PILImage.new('RGB', (self.width, self.height), color='#2c3e50')
        draw = ImageDraw.Draw(img)

        # Create gradient effect
        for i in range(self.height):
            shade = int(44 + (62 - 44) * (i / self.height))
            color = f'#{shade:02x}3e50'
            draw.line([(0, i), (self.width, i)], fill=color)

        # Add decorative border
        border_width = 20
        draw.rectangle(
            [border_width, border_width, self.width - border_width, self.height - border_width],
            outline='#ecf0f1',
            width=3
        )

        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
            author_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
            meta_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
        except:
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
                meta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            except:
                title_font = ImageFont.load_default()
                author_font = ImageFont.load_default()
                meta_font = ImageFont.load_default()

        # Draw title (wrap text if too long)
        title = self.metadata.get('title', 'Untitled')
        title_lines = self._wrap_text(title, title_font, self.width - 100)

        y_position = 300
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x_position = (self.width - text_width) // 2
            draw.text((x_position, y_position), line, fill='#ecf0f1', font=title_font)
            y_position += 80

        # Draw author
        author = self.metadata.get('author', 'Unknown Author')
        bbox = draw.textbbox((0, 0), author, font=author_font)
        text_width = bbox[2] - bbox[0]
        x_position = (self.width - text_width) // 2
        draw.text((x_position, y_position + 50), author, fill='#bdc3c7', font=author_font)

        # Draw publisher at bottom
        publisher = self.metadata.get('publisher', '')
        if publisher:
            bbox = draw.textbbox((0, 0), publisher, font=meta_font)
            text_width = bbox[2] - bbox[0]
            x_position = (self.width - text_width) // 2
            draw.text((x_position, self.height - 100), publisher, fill='#95a5a6', font=meta_font)

        # Save the image
        img.save(output_path, 'PNG')
        return output_path

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            # Create a temporary image to measure text
            test_img = PILImage.new('RGB', (1, 1))
            test_draw = ImageDraw.Draw(test_img)
            bbox = test_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines[:3]  # Limit to 3 lines


class ContentProcessor:
    """Process and clean HTML content for ebook conversion"""

    def __init__(self, html_content, base_url, content_selector=None, exclude_selectors=None):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = base_url
        self.content_selector = content_selector
        self.exclude_selectors = exclude_selectors or []

    def extract_main_content(self):
        """Extract main content from the page"""
        # Remove unwanted elements first
        for element in self.soup(['script', 'style', 'nav', 'header', 'footer', 
                                   'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Remove user-specified excluded selectors
        for selector in self.exclude_selectors:
            try:
                for element in self.soup.select(selector):
                    element.decompose()
            except Exception as e:
                print(f"Warning: Invalid exclude selector '{selector}': {e}")
        
        # Try to find main content area
        main_content = None
        
        # If user specified a content selector, use it
        if self.content_selector:
            try:
                main_content = self.soup.select_one(self.content_selector)
                if main_content:
                    return main_content
            except Exception as e:
                print(f"Warning: Invalid content selector '{self.content_selector}': {e}")
        
        # Try common content selectors
        content_selectors = [
            {'id': 'content'},
            {'class': re.compile(r'content|article|post|entry', re.I)},
            {'role': 'main'},
            'main',
            'article'
        ]
        
        for selector in content_selectors:
            if isinstance(selector, str):
                main_content = self.soup.find(selector)
            else:
                main_content = self.soup.find(['div', 'main', 'article', 'section'], selector)
            
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = self.soup.find('body') or self.soup
        
        return main_content

    def clean_content(self, content):
        """Clean and normalize content"""
        if not content:
            return self.soup
        
        # Remove comments
        for comment in content.find_all(string=lambda text: isinstance(text, type(lambda: None))):
            if hasattr(comment, 'extract'):
                comment.extract()
        
        # Fix encoding issues in text nodes
        for text_node in content.find_all(string=True):
            if text_node.parent.name not in ['script', 'style']:
                fixed_text = str(text_node)
                fixed_text = fixed_text.replace('â', "'").replace('â', '"').replace('â', '"')
                fixed_text = fixed_text.replace('â', '—').replace('â¢', '•').replace('Â', ' ')
                if fixed_text != str(text_node):
                    text_node.replace_with(fixed_text)
        
        # Make all URLs absolute
        for tag in content.find_all(['a', 'img', 'link']):
            for attr in ['href', 'src']:
                if tag.get(attr):
                    tag[attr] = urljoin(self.base_url, tag[attr])
        
        return content

    def get_images(self, content):
        """Extract all images from content"""
        images = []
        for img in content.find_all('img'):
            src = img.get('src')
            if src:
                images.append({
                    'src': urljoin(self.base_url, src),
                    'alt': img.get('alt', ''),
                    'element': img
                })
        return images


class EPUBConverter:
    """Convert web content to EPUB format"""

    def __init__(self, metadata, content, images=None):
        self.metadata = metadata
        self.content = content
        self.images = images or []
        self.book = epub.EpubBook()

    def convert(self, output_path, cover_path=None):
        """Create EPUB file"""
        # Set metadata
        book_id = hashlib.md5(self.metadata['url'].encode()).hexdigest()
        self.book.set_identifier(book_id)
        self.book.set_title(self.metadata['title'])
        self.book.set_language(self.metadata['language'])
        self.book.add_author(self.metadata['author'])

        if self.metadata.get('description'):
            self.book.add_metadata('DC', 'description', self.metadata['description'])

        if self.metadata.get('publisher'):
            self.book.add_metadata('DC', 'publisher', self.metadata['publisher'])

        if self.metadata.get('date'):
            self.book.add_metadata('DC', 'date', self.metadata['date'])

        # Add cover if provided
        if cover_path and os.path.exists(cover_path):
            with open(cover_path, 'rb') as cover_file:
                self.book.set_cover('cover.png', cover_file.read())

        # Add CSS for styling
        css = '''
@namespace epub "http://www.idpf.org/2007/ops";
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 2em;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: Arial, sans-serif;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.3;
            color: #2c3e50;
        }
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.3em; }
        p {
            margin: 1em 0;
            text-align: justify;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        blockquote {
            margin: 1em 2em;
            padding: 0.5em 1em;
            border-left: 3px solid #ccc;
            font-style: italic;
            background-color: #f9f9f9;
            color: #555;
        }
        code {
            font-family: "Courier New", "Consolas", monospace;
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
            border: 1px solid #e1e1e8;
        }
        pre {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 1em;
            overflow-x: auto;
            border-radius: 5px;
            border: 1px solid #444;
            line-height: 1.4;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            border: none;
            color: #f8f8f2;
            display: block;
            font-size: 0.85em;
        }
        '''

        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css
        )
        self.book.add_item(nav_css)

        # Create chapter
        chapter = epub.EpubHtml(
            title=self.metadata['title'],
            file_name='content.xhtml',
            lang=self.metadata['language']
        )

        # Process content and add images
        content_html = str(self.content)
        chapter.content = content_html
        chapter.add_item(nav_css)

        self.book.add_item(chapter)

        # Add table of contents
        self.book.toc = (epub.Link('content.xhtml', self.metadata['title'], 'content'),)

        # Add navigation files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Define spine
        self.book.spine = ['nav', chapter]

        # Write EPUB file
        epub.write_epub(output_path, self.book, {})
        return output_path


class PDFConverter:
    """Convert web content to PDF format"""

    def __init__(self, metadata, content):
        self.metadata = metadata
        self.content = content
        self.h2t = html2text.HTML2Text()
        self.h2t.body_width = 0

    def convert(self, output_path, cover_path=None):
        """Create PDF file"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []
        styles = getSampleStyleSheet()

        # Add custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))

        # Add cover page (scaled to fit within margins)
        if cover_path and os.path.exists(cover_path):
            try:
                # Page dimensions minus margins
                available_width = letter[0] - 144  # 72pt margins on each side
                available_height = letter[1] - 144
                
                # Create image and get dimensions
                img = Image(cover_path)
                
                # Ensure we have valid dimensions
                if not hasattr(img, 'imageWidth') or not hasattr(img, 'imageHeight'):
                    raise ValueError("Could not get image dimensions")
                
                img_width = float(img.imageWidth)
                img_height = float(img.imageHeight)
                
                if img_width <= 0 or img_height <= 0:
                    raise ValueError(f"Invalid image dimensions: {img_width}x{img_height}")
                
                # Calculate scaling to fit within available space
                width_scale = available_width / img_width
                height_scale = available_height / img_height
                scale = min(width_scale, height_scale, 1.0)  # Don't upscale
                
                # Set final dimensions
                img.drawWidth = img_width * scale
                img.drawHeight = img_height * scale
                
                # Verify final size fits
                if img.drawHeight > available_height or img.drawWidth > available_width:
                    # Force fit with more aggressive scaling
                    img.drawWidth = available_width * 0.9
                    img.drawHeight = available_height * 0.9
                
                story.append(img)
                story.append(PageBreak())
            except Exception as e:
                print(f"Warning: Could not add cover to PDF: {e}")
                # Continue without cover

        # Add title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(self.metadata['title'], styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"by {self.metadata['author']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        if self.metadata.get('publisher'):
            story.append(Paragraph(self.metadata['publisher'], styles['Normal']))

        story.append(PageBreak())

        # Convert HTML to text with formatting
        text = self.h2t.handle(str(self.content))

        # Process text paragraphs
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                # Handle headings
                if para.startswith('#'):
                    level = len(para) - len(para.lstrip('#'))
                    text = para.lstrip('#').strip()
                    style = styles[f'Heading{min(level, 4)}']
                    story.append(Paragraph(text, style))
                else:
                    # Regular paragraph
                    # Escape special characters for reportlab
                    para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(para, styles['CustomBody']))

                story.append(Spacer(1, 0.1*inch))

        # Add metadata page at the end
        story.append(PageBreak())
        story.append(Paragraph("Metadata", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))

        metadata_text = f"""
        Title: {self.metadata['title']}<br/>
        Author: {self.metadata['author']}<br/>
        Source: {self.metadata['url']}<br/>
        Date: {self.metadata['date']}<br/>
        """

        if self.metadata.get('publisher'):
            metadata_text += f"Publisher: {self.metadata['publisher']}<br/>"

        story.append(Paragraph(metadata_text, styles['Normal']))

        # Build PDF
        doc.build(story)
        return output_path


class MOBIConverter:
    """Convert EPUB to MOBI format using Calibre's ebook-convert"""

    def __init__(self, epub_path):
        self.epub_path = epub_path

    def convert(self, output_path):
        """Convert EPUB to MOBI"""
        # Check if ebook-convert is available
        if not shutil.which('ebook-convert'):
            raise Exception(
                "Calibre's ebook-convert is not installed. "
                "Please install Calibre from https://calibre-ebook.com/"
            )

        import subprocess

        try:
            result = subprocess.run(
                ['ebook-convert', self.epub_path, output_path],
                capture_output=True,
                text=True,
                check=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to convert to MOBI: {e.stderr}")


class Web2Ebook:
    """Main converter class"""

    def __init__(self, url, output_dir=None, generate_cover=True, custom_cover=None, crawl=False, max_pages=10, exclude_urls=None, include_urls=None, content_selector=None, exclude_selectors=None):
        self.url = url
        self.output_dir = output_dir or os.getcwd()
        self.generate_cover = generate_cover
        self.custom_cover = custom_cover
        self.temp_dir = None
        self.crawl = crawl
        self.max_pages = max_pages
        self.visited_urls = set()
        self.base_domain = self._extract_domain(url)
        self.exclude_urls = set(exclude_urls) if exclude_urls else set()
        self.exclude_patterns = self._compile_exclude_patterns()
        self.include_urls = set(include_urls) if include_urls else set()
        self.include_patterns = self._compile_include_patterns()
        self.content_selector = content_selector
        self.exclude_selectors = exclude_selectors or []

    def _extract_domain(self, url):
        """Extract base domain from URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _compile_exclude_patterns(self):
        """Compile regex patterns from exclude URLs for pattern matching"""
        patterns = []
        for pattern in self.exclude_urls:
            if '*' in pattern or '?' in pattern:
                # Convert glob-like pattern to regex
                regex_pattern = pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
                patterns.append(re.compile(regex_pattern))
        return patterns
    
    def _compile_include_patterns(self):
        """Compile regex patterns from include URLs for pattern matching"""
        patterns = []
        for pattern in self.include_urls:
            if '*' in pattern or '?' in pattern:
                # Convert glob-like pattern to regex
                regex_pattern = pattern.replace('.', r'\.').replace('*', '.*').replace('?', '.')
                patterns.append(re.compile(regex_pattern))
        return patterns

    def _should_exclude_url(self, url):
        """Check if URL should be excluded"""
        # Exact match
        if url in self.exclude_urls:
            return True

        # Pattern match
        for pattern in self.exclude_patterns:
            if pattern.match(url):
                return True

        # Substring matching only for patterns without wildcards and without protocol
        # This prevents "https://example.com/" from matching "https://example.com/page.html"
        for exclude in self.exclude_urls:
            if '*' not in exclude and '?' not in exclude:
                # Only do substring match if exclude pattern doesn't look like a full URL
                if not exclude.startswith('http://') and not exclude.startswith('https://'):
                    if exclude in url:
                        return True

        return False
    
    def _should_include_url(self, url):
        """Check if URL matches include patterns (if any are specified)"""
        # If no include patterns specified, include everything
        if not self.include_urls:
            return True
        
        # Exact match
        if url in self.include_urls:
            return True
        
        # Pattern match
        for pattern in self.include_patterns:
            if pattern.match(url):
                return True
        
        # Substring matching for patterns without wildcards and without protocol
        for include in self.include_urls:
            if '*' not in include and '?' not in include:
                # Only do substring match if include pattern doesn't look like a full URL
                if not include.startswith('http://') and not include.startswith('https://'):
                    if include in url:
                        return True
        
        return False
    
    def _find_links(self, soup, current_url):
        """Find all valid links on the page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Make absolute
            absolute_url = urljoin(current_url, href)

            # Only follow links from same domain
            if absolute_url.startswith(self.base_domain):
                # Skip anchors and already visited
                if '#' in absolute_url:
                    absolute_url = absolute_url.split('#')[0]

                # Skip if already visited
                if absolute_url in self.visited_urls:
                    continue

                # Check if URL should be excluded
                if self._should_exclude_url(absolute_url):
                    continue
                
                # Check if URL matches include patterns
                if not self._should_include_url(absolute_url):
                    continue
                
                # Only include HTML-like URLs (filter out images, PDFs, etc)
                if self._is_html_url(absolute_url):
                    links.append(absolute_url)
        return links

    def _is_html_url(self, url):
        """Check if URL likely points to an HTML page"""
        # Remove query string and fragments
        path = urlparse(url).path.lower()

        # Skip common non-HTML extensions
        skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip',
                          '.mp4', '.mp3', '.css', '.js', '.xml', '.json',
                          '.svg', '.ico', '.webp', '.bmp', '.doc', '.docx']

        for ext in skip_extensions:
            if path.endswith(ext):
                return False

        # If it has .html or .htm, it's HTML
        if path.endswith(('.html', '.htm')):
            return True

        # If no extension or ends with /, assume it's HTML
        if not path or path.endswith('/') or '.' not in path.split('/')[-1]:
            return True

        return False

    def convert(self, formats=['epub', 'pdf', 'mobi']):
        """Convert web page to specified ebook formats"""
        if self.crawl:
            return self._convert_multiple(formats)
        else:
            return self._convert_single(self.url, formats)

    def _convert_multiple(self, formats):
        """Convert multiple pages by crawling and combining into one ebook"""
        console = Console()
        
        urls_to_visit = [self.url]
        self.visited_urls = set()
        all_chapters = []
        main_metadata = None
        excluded_count = 0
        start_time = time.time()
        
        # Status tracking
        completed_titles = []
        current_status = "Starting..."
        queue_size = 1
        
        def generate_table():
            """Generate live status table"""
            table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
            table.add_column("Key", style="cyan bold", width=15)
            table.add_column("Value", style="white")
            
            elapsed = int(time.time() - start_time)
            progress_bar = f"[{'█' * (len(self.visited_urls) * 20 // max(self.max_pages, 1))}{'░' * (20 - len(self.visited_urls) * 20 // max(self.max_pages, 1))}]"
            
            table.add_row("📊 Progress", f"{progress_bar} {len(self.visited_urls)}/{self.max_pages}")
            table.add_row("📖 Book", main_metadata['title'] if main_metadata else "Loading...")
            table.add_row("🔄 Status", current_status)
            table.add_row("📚 Chapters", str(len(all_chapters)))
            table.add_row("📝 Queue", str(queue_size))
            
            if self.include_urls:
                table.add_row("✅ Include", f"{len(self.include_urls)} pattern(s)")
            
            if self.exclude_urls:
                table.add_row("🚫 Exclude", f"{len(self.exclude_urls)} pattern(s)")
            
            table.add_row("⏱️  Time", f"{elapsed}s")
            
            # Recent chapters
            if completed_titles:
                table.add_row("", "")
                table.add_row("✅ Recent", "")
                for title in completed_titles[-5:]:
                    table.add_row("", f"  • {title[:50]}")
            
            return Panel(table, title="[bold cyan]🕷️  Web2Ebook Crawler[/bold cyan]", border_style="cyan")
        
        with Live(generate_table(), refresh_per_second=4, console=console) as live:
            while urls_to_visit and len(self.visited_urls) < self.max_pages:
                current_url = urls_to_visit.pop(0)
                queue_size = len(urls_to_visit)
                
                if current_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(current_url)
                current_status = f"Downloading {len(self.visited_urls)}/{self.max_pages}"
                live.update(generate_table())
                
                try:
                    downloader = WebPageDownloader(current_url)
                    html = downloader.download()
                    
                    current_status = "Parsing HTML..."
                    live.update(generate_table())
                    
                    soup = BeautifulSoup(html, 'lxml')  # lxml is faster than html.parser
                    
                    # Extract metadata from first page
                    if main_metadata is None:
                        metadata_extractor = MetadataExtractor(soup, current_url)
                        main_metadata = metadata_extractor.extract()
                        main_metadata['title'] = f"{main_metadata['title']} (Complete)"
                    
                    # Process content
                    current_status = "Processing content..."
                    live.update(generate_table())

                    processor = ContentProcessor(html, current_url, self.content_selector, self.exclude_selectors)
                    main_content = processor.extract_main_content()
                    clean_content = processor.clean_content(main_content)
                    
                    # Download images with threading - non-blocking
                    images = processor.get_images(clean_content)
                    image_data_list = []
                    
                    if images:
                        current_status = f"Downloading {len(images)} images..."
                        live.update(generate_table())
                        
                        with ThreadPoolExecutor(max_workers=8) as executor:
                            future_to_img = {executor.submit(downloader.download_image, img['src']): img for img in images}
                            completed = 0
                            for future in as_completed(future_to_img):
                                img_data = future_to_img[future]
                                try:
                                    img_bytes = future.result()
                                    if img_bytes:
                                        img_data['bytes'] = img_bytes
                                        image_data_list.append(img_data)
                                        completed += 1
                                        current_status = f"Downloaded {completed}/{len(images)} images"
                                        live.update(generate_table())
                                except:
                                    pass
                    
                    # Extract chapter title
                    chapter_metadata = MetadataExtractor(soup, current_url).extract()
                    chapter_title = chapter_metadata['title']
                    
                    # Store chapter
                    all_chapters.append({
                        'title': chapter_title,
                        'content': clean_content,
                        'url': current_url,
                        'images': image_data_list
                    })
                    
                    completed_titles.append(chapter_title)
                    
                    # Find more links
                    if len(self.visited_urls) < self.max_pages:
                        current_status = "Finding links..."
                        live.update(generate_table())
                        
                        new_links = self._find_links(soup, current_url)
                        for link in new_links:
                            if link not in self.visited_urls and link not in urls_to_visit:
                                urls_to_visit.append(link)
                        
                        queue_size = len(urls_to_visit)
                    
                    current_status = "✓ Complete"
                    live.update(generate_table())
                    time.sleep(0.1)  # Minimal delay
                
                except Exception as e:
                    current_status = f"⚠ Error: {str(e)[:30]}"
                    live.update(generate_table())
                    time.sleep(0.2)
                    continue
            
            current_status = f"✅ Completed! Creating ebook..."
            live.update(generate_table())
            time.sleep(1)
        
        console.print(f"\n[bold green]✅ Crawled {len(all_chapters)} pages in {int(time.time() - start_time)}s[/bold green]")
        console.print(f"[cyan]📚 Creating combined ebook...[/cyan]\n")
        
        # Now create single ebook with all chapters
        return self._create_combined_ebook(main_metadata, all_chapters, formats)

    def _create_combined_ebook(self, metadata, chapters, formats):
        """Create a single ebook from multiple chapters"""
        self.temp_dir = tempfile.mkdtemp()

        try:
            # Handle cover
            cover_path = None
            if self.custom_cover and os.path.exists(self.custom_cover):
                cover_path = self.custom_cover
                print(f"🎨 Using custom cover")
            elif self.generate_cover:
                cover_path = os.path.join(self.temp_dir, 'cover.png')
                cover_gen = CoverGenerator(metadata)
                cover_gen.generate(cover_path)
                print(f"🎨 Generated cover image")

            # Generate output filename
            safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]

            results = {}

            # Convert to EPUB
            if 'epub' in formats:
                epub_path = os.path.join(self.output_dir, f"{safe_title}.epub")
                print(f"📚 Creating combined EPUB: {epub_path}")
                self._create_multi_chapter_epub(metadata, chapters, epub_path, cover_path)
                results['epub'] = epub_path
                print(f"✅ EPUB created with {len(chapters)} chapters")

            # Convert to PDF
            if 'pdf' in formats:
                pdf_path = os.path.join(self.output_dir, f"{safe_title}.pdf")
                print(f"📄 Creating combined PDF: {pdf_path}")
                self._create_multi_chapter_pdf(metadata, chapters, pdf_path, cover_path)
                results['pdf'] = pdf_path
                print(f"✅ PDF created with {len(chapters)} chapters")

            # Convert to MOBI
            if 'mobi' in formats:
                if 'epub' not in results:
                    temp_epub = os.path.join(self.temp_dir, 'temp.epub')
                    self._create_multi_chapter_epub(metadata, chapters, temp_epub, cover_path)
                    epub_for_mobi = temp_epub
                else:
                    epub_for_mobi = results['epub']

                mobi_path = os.path.join(self.output_dir, f"{safe_title}.mobi")
                print(f"📱 Creating MOBI: {mobi_path}")
                try:
                    mobi_converter = MOBIConverter(epub_for_mobi)
                    mobi_converter.convert(mobi_path)
                    results['mobi'] = mobi_path
                    print(f"✅ MOBI created successfully")
                except Exception as e:
                    print(f"⚠️  MOBI conversion failed: {e}")

            return results

        finally:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def _create_multi_chapter_epub(self, metadata, chapters, output_path, cover_path):
        """Create EPUB with multiple chapters"""
        book = epub.EpubBook()

        # Set metadata
        book_id = hashlib.md5(metadata['url'].encode()).hexdigest()
        book.set_identifier(book_id)
        book.set_title(metadata['title'])
        book.set_language(metadata['language'])
        book.add_author(metadata['author'])

        if metadata.get('description'):
            book.add_metadata('DC', 'description', metadata['description'])
        if metadata.get('publisher'):
            book.add_metadata('DC', 'publisher', metadata['publisher'])
        if metadata.get('date'):
            book.add_metadata('DC', 'date', metadata['date'])

        # Add cover
        if cover_path and os.path.exists(cover_path):
            with open(cover_path, 'rb') as cover_file:
                book.set_cover('cover.png', cover_file.read())

        # Add CSS
        css = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body { font-family: Georgia, serif; line-height: 1.6; margin: 2em; color: #333; }
        h1, h2, h3, h4, h5, h6 { font-family: Arial, sans-serif; font-weight: bold;
                                 margin-top: 1.5em; margin-bottom: 0.5em; line-height: 1.3; color: #2c3e50; }
        h1 { font-size: 2em; } h2 { font-size: 1.5em; } h3 { font-size: 1.3em; }
        p { margin: 1em 0; text-align: justify; }
        img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        blockquote { margin: 1em 2em; padding-left: 1em; border-left: 3px solid #ccc;
                     font-style: italic; color: #555; background-color: #f9f9f9; padding: 0.5em 1em; }
        code { font-family: "Courier New", "Consolas", monospace; background-color: #f4f4f4;
               padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; color: #c7254e;
               border: 1px solid #e1e1e8; }
        pre { background-color: #2d2d2d; color: #f8f8f2; padding: 1em; overflow-x: auto;
              border-radius: 5px; border: 1px solid #444; line-height: 1.4; }
        pre code { background-color: transparent; padding: 0; border: none; color: #f8f8f2;
                   display: block; font-size: 0.85em; }
        ul, ol { margin: 1em 0; padding-left: 2em; }
        li { margin: 0.5em 0; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        th, td { border: 1px solid #ddd; padding: 0.5em; text-align: left; }
        th { background-color: #f4f4f4; font-weight: bold; }
        '''

        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                                media_type="text/css", content=css)
        book.add_item(nav_css)

        # Embed images with proper handling
        image_counter = 0
        image_map = {}  # Map old src to new src
        
        for chapter_data in chapters:
            if 'images' in chapter_data:
                for img_data in chapter_data['images']:
                    if 'bytes' in img_data and img_data['bytes']:
                        image_counter += 1
                        
                        # Detect image type from content
                        img_bytes = img_data['bytes']
                        if img_bytes[:4] == b'\x89PNG':
                            ext, media = 'png', 'image/png'
                        elif img_bytes[:3] == b'\xff\xd8\xff':
                            ext, media = 'jpg', 'image/jpeg'
                        elif img_bytes[:6] in (b'GIF87a', b'GIF89a'):
                            ext, media = 'gif', 'image/gif'
                        elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP':
                            ext, media = 'webp', 'image/webp'
                        else:
                            ext, media = 'jpg', 'image/jpeg'
                        
                        img_name = f'images/img_{image_counter}.{ext}'
                        img_item = epub.EpubItem(
                            uid=f"img_{image_counter}",
                            file_name=img_name,
                            media_type=media,
                            content=img_bytes
                        )
                        book.add_item(img_item)
                        
                        # Map old URL to new path
                        old_src = img_data['src']
                        image_map[old_src] = img_name
        
        # Replace all image sources in content
        for chapter_data in chapters:
            content_str = str(chapter_data['content'])
            for old_src, new_src in image_map.items():
                # Try different quote styles
                content_str = content_str.replace(f'src="{old_src}"', f'src="{new_src}"')
                content_str = content_str.replace(f"src='{old_src}'", f'src="{new_src}"')
                content_str = content_str.replace(f'src={old_src}', f'src="{new_src}"')
            chapter_data['content'] = content_str

        # Create chapters
        epub_chapters = []
        toc_entries = []

        for idx, chapter_data in enumerate(chapters, 1):
            # Create chapter
            chapter = epub.EpubHtml(
                title=chapter_data['title'],
                file_name=f'chapter_{idx}.xhtml',
                lang=metadata['language']
            )
        
            # Process content to improve code blocks
            content_html = str(chapter_data['content'])
        
            # Fix any remaining encoding issues
            content_html = content_html.replace('â', "'").replace('â', '"').replace('â', '"')
            content_html = content_html.replace('â', '—').replace('â¢', '•').replace('Â', ' ')
        
            # Wrap code blocks better - find <pre> tags without <code> inside
            content_html = re.sub(
                r'<pre(?![^>]*class=["\'])(.*?)>(.*?)</pre>',
                r'<pre\1><code>\2</code></pre>',
                content_html,
                flags=re.DOTALL
            )
        
            chapter.content = f"<h1>{chapter_data['title']}</h1>" + content_html
            chapter.add_item(nav_css)

            book.add_item(chapter)
            epub_chapters.append(chapter)
            toc_entries.append(epub.Link(f'chapter_{idx}.xhtml', chapter_data['title'], f'ch{idx}'))

        # Set table of contents
        book.toc = tuple(toc_entries)

        # Add navigation
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define spine
        book.spine = ['nav'] + epub_chapters

        # Write file
        epub.write_epub(output_path, book, {})

    def _create_multi_chapter_pdf(self, metadata, chapters, output_path, cover_path):
        """Create PDF with multiple chapters"""
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        story = []
        styles = getSampleStyleSheet()
        
        # Add cover page (scaled to fit within margins)
        if cover_path and os.path.exists(cover_path):
            try:
                # Page dimensions minus margins
                available_width = letter[0] - 144  # 72pt margins on each side
                available_height = letter[1] - 144
                
                # Create image and get dimensions
                img = Image(cover_path)
                
                # Ensure we have valid dimensions
                if not hasattr(img, 'imageWidth') or not hasattr(img, 'imageHeight'):
                    raise ValueError("Could not get image dimensions")
                
                img_width = float(img.imageWidth)
                img_height = float(img.imageHeight)
                
                if img_width <= 0 or img_height <= 0:
                    raise ValueError(f"Invalid image dimensions: {img_width}x{img_height}")
                
                # Calculate scaling to fit within available space
                width_scale = available_width / img_width
                height_scale = available_height / img_height
                scale = min(width_scale, height_scale, 1.0)  # Don't upscale
                
                # Set final dimensions
                img.drawWidth = img_width * scale
                img.drawHeight = img_height * scale
                
                # Verify final size fits
                if img.drawHeight > available_height or img.drawWidth > available_width:
                    # Force fit with more aggressive scaling
                    img.drawWidth = available_width * 0.9
                    img.drawHeight = available_height * 0.9
                
                story.append(img)
                story.append(PageBreak())
            except Exception as e:
                print(f"Warning: Could not add cover to PDF: {e}")
                # Continue without cover
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(metadata['title'], styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"by {metadata['author']}", styles['Normal']))
        if metadata.get('publisher'):
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(metadata['publisher'], styles['Normal']))
        story.append(PageBreak())

        # Add chapters
        h2t = html2text.HTML2Text()
        h2t.body_width = 0

        for idx, chapter_data in enumerate(chapters, 1):
            # Chapter title
            story.append(Paragraph(f"Chapter {idx}: {chapter_data['title']}", styles['Heading1']))
            story.append(Spacer(1, 0.3*inch))

            # Chapter content
            text = h2t.handle(str(chapter_data['content']))
            paragraphs = text.split('\n\n')

            for para in paragraphs:
                para = para.strip()
                if para:
                    if para.startswith('#'):
                        level = len(para) - len(para.lstrip('#'))
                        text = para.lstrip('#').strip()
                        style = styles[f'Heading{min(level, 4)}']
                        story.append(Paragraph(text, style))
                    elif para.startswith('```') or para.startswith('    '):
                        # Code block - use Preformatted style
                        code_text = para.strip('`').strip()
                        # Escape for XML
                        code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f'<font name="Courier" size="9">{code_text}</font>',
                                             styles['Code']))
                    else:
                        para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(para, styles['BodyText']))
                    story.append(Spacer(1, 0.1*inch))

            # Page break between chapters
            if idx < len(chapters):
                story.append(PageBreak())

        doc.build(story)

    def _convert_single(self, url, formats):
        """Convert a single page to ebook formats"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()

        try:
            # Download web page
            downloader = WebPageDownloader(url)
            html_content = downloader.download()

            # Parse and extract metadata
            soup = BeautifulSoup(html_content, 'html.parser')
            metadata_extractor = MetadataExtractor(soup, url)
            metadata = metadata_extractor.extract()

            print(f"📖 Title: {metadata['title']}")
            print(f"✍️  Author: {metadata['author']}")

            # Process content
            processor = ContentProcessor(html_content, url, self.content_selector, self.exclude_selectors)
            main_content = processor.extract_main_content()
            clean_content = processor.clean_content(main_content)

            # Handle cover
            cover_path = None
            if self.custom_cover and os.path.exists(self.custom_cover):
                cover_path = self.custom_cover
                print(f"🎨 Using custom cover: {self.custom_cover}")
            elif self.generate_cover:
                cover_path = os.path.join(self.temp_dir, 'cover.png')
                cover_gen = CoverGenerator(metadata)
                cover_gen.generate(cover_path)
                print(f"🎨 Generated cover image")

            # Generate output filename
            safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]

            results = {}

            # Convert to EPUB
            if 'epub' in formats:
                epub_path = os.path.join(self.output_dir, f"{safe_title}.epub")
                print(f"📚 Creating EPUB: {epub_path}")
                epub_converter = EPUBConverter(metadata, clean_content)
                epub_converter.convert(epub_path, cover_path)
                results['epub'] = epub_path
                print(f"✅ EPUB created successfully")

            # Convert to PDF
            if 'pdf' in formats:
                pdf_path = os.path.join(self.output_dir, f"{safe_title}.pdf")
                print(f"📄 Creating PDF: {pdf_path}")
                pdf_converter = PDFConverter(metadata, clean_content)
                pdf_converter.convert(pdf_path, cover_path)
                results['pdf'] = pdf_path
                print(f"✅ PDF created successfully")

            # Convert to MOBI
            if 'mobi' in formats:
                if 'epub' not in results:
                    # Need to create EPUB first
                    temp_epub = os.path.join(self.temp_dir, 'temp.epub')
                    epub_converter = EPUBConverter(metadata, clean_content)
                    epub_converter.convert(temp_epub, cover_path)
                    epub_for_mobi = temp_epub
                else:
                    epub_for_mobi = results['epub']

                mobi_path = os.path.join(self.output_dir, f"{safe_title}.mobi")
                print(f"📱 Creating MOBI: {mobi_path}")
                try:
                    mobi_converter = MOBIConverter(epub_for_mobi)
                    mobi_converter.convert(mobi_path)
                    results['mobi'] = mobi_path
                    print(f"✅ MOBI created successfully")
                except Exception as e:
                    print(f"⚠️  MOBI conversion failed: {e}")

            return results

        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert web pages to ebook formats (EPUB, PDF, MOBI)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com/article
  %(prog)s https://example.com/article --formats epub pdf
  %(prog)s https://example.com/article --no-cover
  %(prog)s https://example.com/article --cover my_cover.png
  %(prog)s https://example.com/article -o /path/to/output

Copyright (c) devsimsek
        """
    )

    parser.add_argument(
        'url',
        help='URL of the web page to convert'
    )

    parser.add_argument(
        '-f', '--formats',
        nargs='+',
        choices=['epub', 'pdf', 'mobi'],
        default=['epub', 'pdf', 'mobi'],
        help='Output formats (default: all formats)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: current directory)',
        default=None
    )

    parser.add_argument(
        '--no-cover',
        action='store_true',
        help='Do not generate a cover image'
    )

    parser.add_argument(
        '--cover',
        help='Path to custom cover image',
        default=None
    )

    parser.add_argument(
        '--crawl',
        action='store_true',
        help='Crawl and convert multiple pages from the starting URL'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum number of pages to crawl (default: 10)'
    )

    parser.add_argument(
        '--exclude',
        nargs='*',
        default=[],
        help='URLs or patterns to exclude from crawling (supports wildcards)'
    )

    parser.add_argument(
        '--exclude-file',
        help='File containing URLs to exclude (one per line)'
    )
    
    parser.add_argument(
        '--include',
        nargs='*',
        default=[],
        help='URLs or patterns to include when crawling (supports wildcards)'
    )
    
    parser.add_argument(
        '--include-file',
        help='File containing URLs to include (one per line)'
    )
    
    parser.add_argument(
        '--content-selector',
        help='CSS selector to target specific content container (e.g., "article", "#main-content")'
    )
    
    parser.add_argument(
        '--exclude-selectors',
        nargs='*',
        default=[],
        help='CSS selectors for elements to exclude (e.g., ".comments", "#sidebar")'
    )
    
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    print("=" * 60)
    print("Web2Ebook Converter")
    print("Copyright (c) devsimsek")
    print("=" * 60)
    print()

    # Process exclude list
    exclude_urls = list(args.exclude) if args.exclude else []
    
    # Load from file if provided
    if args.exclude_file:
        try:
            with open(args.exclude_file, 'r') as f:
                file_excludes = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                exclude_urls.extend(file_excludes)
                print(f"📄 Loaded {len(file_excludes)} exclude patterns from {args.exclude_file}")
        except FileNotFoundError:
            print(f"⚠️  Warning: Exclude file not found: {args.exclude_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not read exclude file: {e}")
    
    # Process include list
    include_urls = list(args.include) if args.include else []
    
    # Load from file if provided
    if args.include_file:
        try:
            with open(args.include_file, 'r') as f:
                file_includes = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                include_urls.extend(file_includes)
                print(f"📄 Loaded {len(file_includes)} include patterns from {args.include_file}")
        except FileNotFoundError:
            print(f"⚠️  Warning: Include file not found: {args.include_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not read include file: {e}")

    try:
        converter = Web2Ebook(
            args.url,
            output_dir=args.output,
            generate_cover=not args.no_cover,
            custom_cover=args.cover,
            crawl=args.crawl,
            max_pages=args.max_pages,
            exclude_urls=exclude_urls,
            include_urls=include_urls,
            content_selector=args.content_selector,
            exclude_selectors=args.exclude_selectors
        )

        results = converter.convert(formats=args.formats)

        print()
        print("=" * 60)
        print("✨ Conversion completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        for format_type, path in results.items():
            print(f"  {format_type.upper()}: {path}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
