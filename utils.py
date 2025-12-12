#!/usr/bin/env python3
"""
Web2Ebook - Utility Functions

Copyright (c) devsimsek

Helper utilities for web2ebook conversion process.
"""

import os
import re
import hashlib
from urllib.parse import urlparse, urljoin
from datetime import datetime
import json


def sanitize_filename(filename, max_length=50):
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: The filename string to sanitize
        max_length: Maximum length of the filename
    
    Returns:
        A safe filename string
    """
    # Remove invalid characters
    filename = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    # Limit length
    filename = filename[:max_length]
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename or 'untitled'


def generate_unique_id(url):
    """
    Generate a unique ID from a URL.
    
    Args:
        url: The URL to generate ID from
    
    Returns:
        A unique hash string
    """
    return hashlib.md5(url.encode()).hexdigest()


def is_valid_url(url):
    """
    Check if a URL is valid.
    
    Args:
        url: The URL to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url, base_url=None):
    """
    Normalize a URL, making it absolute if necessary.
    
    Args:
        url: The URL to normalize
        base_url: The base URL for relative URLs
    
    Returns:
        An absolute URL
    """
    if not url:
        return None
    
    # If already absolute, return as-is
    if url.startswith(('http://', 'https://')):
        return url
    
    # If base_url provided, make absolute
    if base_url:
        return urljoin(base_url, url)
    
    return url


def get_file_extension(url_or_path):
    """
    Extract file extension from URL or path.
    
    Args:
        url_or_path: URL or file path
    
    Returns:
        File extension (without dot) or empty string
    """
    path = urlparse(url_or_path).path
    ext = os.path.splitext(path)[1].lower()
    return ext.lstrip('.')


def format_file_size(size_bytes):
    """
    Format bytes into human-readable size.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def parse_date(date_string):
    """
    Parse various date formats into ISO format.
    
    Args:
        date_string: Date string in various formats
    
    Returns:
        ISO formatted date string
    """
    if not date_string:
        return datetime.now().isoformat()
    
    # Common date formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%B %d, %Y',
        '%d %B %Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string.split('+')[0].split('Z')[0].strip(), fmt)
            return dt.isoformat()
        except:
            continue
    
    # Return current date if parsing fails
    return datetime.now().isoformat()


def truncate_text(text, max_length, suffix='...'):
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append (default: '...')
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_whitespace(text):
    """
    Clean excessive whitespace from text.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_domain(url):
    """
    Extract domain from URL.
    
    Args:
        url: The URL
    
    Returns:
        Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc


def is_image_url(url):
    """
    Check if URL points to an image.
    
    Args:
        url: The URL to check
    
    Returns:
        True if image URL, False otherwise
    """
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico']
    ext = get_file_extension(url)
    return ext in image_extensions


def create_directory(path):
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path to create
    
    Returns:
        True if created or exists, False on error
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False


def read_json_file(filepath):
    """
    Read JSON file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON data or None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {filepath}: {e}")
        return None


def write_json_file(data, filepath):
    """
    Write data to JSON file.
    
    Args:
        data: Data to write
        filepath: Path to JSON file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing JSON file {filepath}: {e}")
        return False


def merge_dicts(*dicts):
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Variable number of dictionaries
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def get_timestamp(format='%Y%m%d_%H%M%S'):
    """
    Get current timestamp as string.
    
    Args:
        format: strftime format string
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format)


def validate_metadata(metadata):
    """
    Validate and normalize metadata dictionary.
    
    Args:
        metadata: Metadata dictionary
    
    Returns:
        Validated and normalized metadata
    """
    required_fields = {
        'title': 'Untitled Document',
        'author': 'Unknown Author',
        'language': 'en',
        'date': datetime.now().isoformat(),
    }
    
    # Ensure required fields exist
    for field, default in required_fields.items():
        if field not in metadata or not metadata[field]:
            metadata[field] = default
    
    # Clean text fields
    text_fields = ['title', 'author', 'description', 'publisher', 'keywords']
    for field in text_fields:
        if field in metadata and metadata[field]:
            metadata[field] = clean_whitespace(str(metadata[field]))
    
    return metadata


def estimate_reading_time(text, words_per_minute=200):
    """
    Estimate reading time for text.
    
    Args:
        text: Text content
        words_per_minute: Average reading speed
    
    Returns:
        Estimated reading time in minutes
    """
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))


def strip_html_tags(html_text):
    """
    Remove HTML tags from text (simple regex-based).
    
    Args:
        html_text: HTML text
    
    Returns:
        Plain text
    """
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    return clean_whitespace(text)


def get_text_preview(text, length=200):
    """
    Get a preview of text content.
    
    Args:
        text: Full text
        length: Preview length
    
    Returns:
        Text preview
    """
    text = clean_whitespace(text)
    return truncate_text(text, length)


def format_author_name(author):
    """
    Format author name consistently.
    
    Args:
        author: Author name
    
    Returns:
        Formatted author name
    """
    if not author:
        return 'Unknown Author'
    
    # Remove common prefixes
    author = re.sub(r'^(by|By|BY)\s+', '', author)
    
    # Clean whitespace
    author = clean_whitespace(author)
    
    # Capitalize properly
    if author.islower() or author.isupper():
        author = author.title()
    
    return author


def detect_language(text):
    """
    Simple language detection based on character patterns.
    
    Args:
        text: Text to analyze
    
    Returns:
        Language code (default: 'en')
    """
    if not text:
        return 'en'
    
    # Count different character sets
    latin = len(re.findall(r'[a-zA-Z]', text))
    cyrillic = len(re.findall(r'[а-яА-Я]', text))
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text))
    arabic = len(re.findall(r'[\u0600-\u06ff]', text))
    
    total = latin + cyrillic + cjk + arabic
    if total == 0:
        return 'en'
    
    # Simple detection based on majority
    if cyrillic / total > 0.5:
        return 'ru'
    elif cjk / total > 0.3:
        return 'zh'  # or 'ja', 'ko'
    elif arabic / total > 0.5:
        return 'ar'
    else:
        return 'en'


def get_color_from_string(text):
    """
    Generate a consistent color from string.
    
    Args:
        text: Input string
    
    Returns:
        Hex color code
    """
    hash_value = int(hashlib.md5(text.encode()).hexdigest()[:6], 16)
    r = (hash_value >> 16) & 0xFF
    g = (hash_value >> 8) & 0xFF
    b = hash_value & 0xFF
    return f'#{r:02x}{g:02x}{b:02x}'


# Export all utility functions
__all__ = [
    'sanitize_filename',
    'generate_unique_id',
    'is_valid_url',
    'normalize_url',
    'get_file_extension',
    'format_file_size',
    'parse_date',
    'truncate_text',
    'clean_whitespace',
    'extract_domain',
    'is_image_url',
    'create_directory',
    'read_json_file',
    'write_json_file',
    'merge_dicts',
    'get_timestamp',
    'validate_metadata',
    'estimate_reading_time',
    'strip_html_tags',
    'get_text_preview',
    'format_author_name',
    'detect_language',
    'get_color_from_string',
]


if __name__ == '__main__':
    # Test utilities
    print("Web2Ebook Utilities Test")
    print("Copyright (c) devsimsek")
    print("=" * 60)
    
    # Test sanitize_filename
    print("\n1. Sanitize Filename:")
    print(f"   Input: 'My Article: A Test (2024)!'")
    print(f"   Output: '{sanitize_filename('My Article: A Test (2024)!')}'")
    
    # Test URL validation
    print("\n2. URL Validation:")
    print(f"   'https://example.com' -> {is_valid_url('https://example.com')}")
    print(f"   'not-a-url' -> {is_valid_url('not-a-url')}")
    
    # Test file size formatting
    print("\n3. File Size Formatting:")
    print(f"   1024 bytes -> {format_file_size(1024)}")
    print(f"   1048576 bytes -> {format_file_size(1048576)}")
    
    # Test truncate text
    print("\n4. Text Truncation:")
    long_text = "This is a very long text that should be truncated at some point"
    print(f"   Original: '{long_text}'")
    print(f"   Truncated (30): '{truncate_text(long_text, 30)}'")
    
    # Test timestamp
    print("\n5. Timestamp:")
    print(f"   Current: {get_timestamp()}")
    
    print("\n" + "=" * 60)
    print("All utility tests completed!")