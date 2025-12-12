#!/usr/bin/env python3
"""
Setup script for web2ebook

Copyright (c) devsimsek
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='web2ebook',
    version='1.0.0',
    description='Convert web pages to ebook formats (EPUB, PDF, MOBI)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='devsimsek',
    author_email='',
    url='https://github.com/devsimsek/web2ebook',
    license='MIT',
    py_modules=['web2ebook'],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'ebooklib>=0.18',
        'reportlab>=4.0.0',
        'Pillow>=10.0.0',
        'html2text>=2020.1.16',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'web2ebook=web2ebook:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='ebook epub pdf mobi converter web scraper kindle',
    project_urls={
        'Bug Reports': 'https://github.com/devsimsek/web2ebook/issues',
        'Source': 'https://github.com/devsimsek/web2ebook',
    },
)