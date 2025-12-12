#!/usr/bin/env python3
"""
Web2Ebook - Installation Test Script

Copyright (c) devsimsek

This script tests if all dependencies are properly installed.
"""

import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    print("-" * 60)
    
    modules = [
        ('requests', 'HTTP library'),
        ('bs4', 'BeautifulSoup4'),
        ('lxml', 'LXML parser'),
        ('ebooklib', 'EbubLib'),
        ('reportlab', 'ReportLab'),
        ('PIL', 'Pillow'),
        ('html2text', 'HTML2Text'),
    ]
    
    failed = []
    passed = []
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✓ {description:<20} ({module_name})")
            passed.append(module_name)
        except ImportError as e:
            print(f"✗ {description:<20} ({module_name}) - FAILED")
            print(f"  Error: {e}")
            failed.append(module_name)
    
    print("-" * 60)
    print(f"Passed: {len(passed)}/{len(modules)}")
    print(f"Failed: {len(failed)}/{len(modules)}")
    
    return len(failed) == 0


def test_calibre():
    """Test if Calibre's ebook-convert is available (optional)"""
    print("\nTesting Calibre (optional for MOBI)...")
    print("-" * 60)
    
    import shutil
    
    if shutil.which('ebook-convert'):
        print("✓ Calibre ebook-convert found")
        print("  MOBI conversion is available")
        return True
    else:
        print("⚠ Calibre ebook-convert not found")
        print("  MOBI conversion will not be available")
        print("  Install from: https://calibre-ebook.com/")
        return False


def test_basic_functionality():
    """Test basic functionality of the script"""
    print("\nTesting basic functionality...")
    print("-" * 60)
    
    try:
        from bs4 import BeautifulSoup
        from PIL import Image, ImageDraw
        import tempfile
        import os
        
        # Test HTML parsing
        html = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').get_text()
        assert title == "Test", "HTML parsing failed"
        print("✓ HTML parsing works")
        
        # Test image creation
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test", fill='white')
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            tmp_path = tmp.name
        
        # Verify file exists
        assert os.path.exists(tmp_path), "Image creation failed"
        print("✓ Image generation works")
        
        # Cleanup
        os.unlink(tmp_path)
        
        # Test EPUB creation
        from ebooklib import epub
        book = epub.EpubBook()
        book.set_identifier('test123')
        book.set_title('Test Book')
        book.set_language('en')
        print("✓ EPUB library works")
        
        # Test PDF creation
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            c = canvas.Canvas(tmp.name, pagesize=letter)
            c.drawString(100, 750, "Test PDF")
            c.save()
            tmp_path = tmp.name
        
        assert os.path.exists(tmp_path), "PDF creation failed"
        print("✓ PDF generation works")
        os.unlink(tmp_path)
        
        print("-" * 60)
        print("All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        print("-" * 60)
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Web2Ebook Installation Test")
    print("Copyright (c) devsimsek")
    print("=" * 60)
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n⚠️  Some dependencies are missing!")
        print("\nTo install all dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        print("  pip install requests beautifulsoup4 lxml ebooklib reportlab Pillow html2text")
        sys.exit(1)
    
    # Test Calibre (optional)
    calibre_ok = test_calibre()
    
    # Test functionality
    func_ok = test_basic_functionality()
    
    # Final summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Dependencies: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Calibre:      {'✓ Available' if calibre_ok else '⚠ Not available (optional)'}")
    print(f"Functionality: {'✓ PASS' if func_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if imports_ok and func_ok:
        print("\n✨ Installation successful!")
        print("\nYou can now use web2ebook:")
        print("  python web2ebook.py https://example.com/article")
        print("\nFor more information, see README.md or QUICKSTART.md")
        return 0
    else:
        print("\n❌ Installation incomplete. Please fix the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())