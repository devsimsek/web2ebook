# Web2Ebook Makefile
# Copyright (c) devsimsek

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ACTIVATE := . $(VENV)/bin/activate

.PHONY: help install test clean run example venv

help:
	@echo "Web2Ebook - Makefile Commands"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make test       - Run installation tests"
	@echo "  make clean      - Clean generated files and venv"
	@echo "  make run        - Run with example URL (set URL=...)"
	@echo "  make example    - Show usage examples"
	@echo "  make venv       - Create virtual environment only"
	@echo ""
	@echo "Examples:"
	@echo "  make install"
	@echo "  make test"
	@echo "  make run URL=https://example.com/article"
	@echo "  make run URL=https://example.com/tutorial --crawl --max-pages 5"
	@echo ""

venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "✓ Virtual environment created at $(VENV)"

install: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "✓ Installation complete!"
	@echo ""
	@echo "To activate the virtual environment manually, run:"
	@echo "  source $(VENV)/bin/activate"
	@echo ""
	@echo "Run 'make test' to verify installation."

test:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@echo "Running installation tests..."
	$(PYTHON) test_installation.py

clean:
	@echo "Cleaning generated files..."
	rm -f *.epub *.pdf *.mobi *.png
	rm -rf __pycache__
	rm -rf *.egg-info
	rm -rf build dist
	rm -rf output temp_output batch_output my_books my_ebooks ebooks test_output
	@echo "Cleaning virtual environment..."
	rm -rf $(VENV)
	@echo "✓ Clean complete!"

run:
ifndef URL
	@echo "Error: URL not specified"
	@echo "Usage: make run URL=https://example.com/article"
	@echo "       make run URL=https://example.com/article ARGS='--crawl --max-pages 5'"
	@exit 1
endif
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(PYTHON) web2ebook.py $(URL) $(ARGS)

example:
	@echo "Web2Ebook - Usage Examples"
	@echo "=========================="
	@echo ""
	@echo "1. Basic conversion (all formats):"
	@echo "   make run URL=https://example.com/article"
	@echo ""
	@echo "2. EPUB only:"
	@echo "   make run URL=https://example.com/article ARGS='--formats epub'"
	@echo ""
	@echo "3. Crawl multiple pages:"
	@echo "   make run URL=https://example.com/tutorial ARGS='--crawl --max-pages 10'"
	@echo ""
	@echo "4. Custom output directory:"
	@echo "   make run URL=https://example.com/article ARGS='-o ~/Documents/Books'"
	@echo ""
	@echo "5. With custom cover:"
	@echo "   make run URL=https://example.com/article ARGS='--cover my_cover.png'"
	@echo ""
	@echo "6. Without cover:"
	@echo "   make run URL=https://example.com/article ARGS='--no-cover'"
	@echo ""
	@echo "See README.md for more examples!"