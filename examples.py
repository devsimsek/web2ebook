#!/usr/bin/env python3
"""
Web2Ebook - Example Usage Scripts

Copyright (c) devsimsek

This file contains example usage patterns for the web2ebook library.
"""

from web2ebook import Web2Ebook, WebPageDownloader, MetadataExtractor, CoverGenerator
from bs4 import BeautifulSoup


def example_basic_conversion():
    """
    Example 1: Basic conversion to all formats
    """
    print("=" * 60)
    print("Example 1: Basic Conversion")
    print("=" * 60)

    url = 'https://example.com/article'
    converter = Web2Ebook(url)
    results = converter.convert()

    print("Generated files:")
    for format_type, path in results.items():
        print(f"  {format_type}: {path}")


def example_specific_formats():
    """
    Example 2: Convert to specific formats only
    """
    print("\n" + "=" * 60)
    print("Example 2: Specific Formats (EPUB and PDF only)")
    print("=" * 60)

    url = 'https://example.com/article'
    converter = Web2Ebook(url, output_dir='./output')
    results = converter.convert(formats=['epub', 'pdf'])

    print("Generated files:")
    for format_type, path in results.items():
        print(f"  {format_type}: {path}")


def example_custom_cover():
    """
    Example 3: Use a custom cover image
    """
    print("\n" + "=" * 60)
    print("Example 3: Custom Cover Image")
    print("=" * 60)

    url = 'https://example.com/article'
    converter = Web2Ebook(
        url,
        output_dir='./output',
        custom_cover='my_custom_cover.png'
    )
    results = converter.convert(formats=['epub'])

    print(f"EPUB with custom cover: {results['epub']}")


def example_no_cover():
    """
    Example 4: Disable cover generation
    """
    print("\n" + "=" * 60)
    print("Example 4: No Cover Generation")
    print("=" * 60)

    url = 'https://example.com/article'
    converter = Web2Ebook(
        url,
        output_dir='./output',
        generate_cover=False
    )
    results = converter.convert(formats=['epub', 'pdf'])

    print("Generated files:")
    for format_type, path in results.items():
        print(f"  {format_type}: {path}")


def example_metadata_extraction():
    """
    Example 5: Extract and display metadata only
    """
    print("\n" + "=" * 60)
    print("Example 5: Metadata Extraction")
    print("=" * 60)

    url = 'https://example.com/article'

    # Download the page
    downloader = WebPageDownloader(url)
    html = downloader.download()

    # Parse and extract metadata
    soup = BeautifulSoup(html, 'html.parser')
    extractor = MetadataExtractor(soup, url)
    metadata = extractor.extract()

    print("\nExtracted Metadata:")
    print(f"  Title: {metadata['title']}")
    print(f"  Author: {metadata['author']}")
    print(f"  Publisher: {metadata['publisher']}")
    print(f"  Date: {metadata['date']}")
    print(f"  Language: {metadata['language']}")
    print(f"  Description: {metadata['description'][:100]}...")
    print(f"  Keywords: {metadata['keywords']}")


def example_cover_generation_only():
    """
    Example 6: Generate cover image only
    """
    print("\n" + "=" * 60)
    print("Example 6: Generate Cover Only")
    print("=" * 60)

    # Define metadata manually
    metadata = {
        'title': 'My Awesome Article',
        'author': 'John Doe',
        'publisher': 'Example Publishing',
        'description': 'An amazing article about technology'
    }

    # Generate cover
    cover_gen = CoverGenerator(metadata, width=800, height=1200)
    cover_path = 'generated_cover.png'
    cover_gen.generate(cover_path)

    print(f"Cover generated: {cover_path}")


def example_batch_conversion():
    """
    Example 7: Batch convert multiple URLs
    """
    print("\n" + "=" * 60)
    print("Example 7: Batch Conversion")
    print("=" * 60)

    urls = [
        'https://example.com/article1',
        'https://example.com/article2',
        'https://example.com/article3',
    ]

    for i, url in enumerate(urls, 1):
        print(f"\nConverting {i}/{len(urls)}: {url}")
        try:
            converter = Web2Ebook(url, output_dir='./batch_output')
            results = converter.convert(formats=['epub'])
            print(f"  ✓ Success: {results['epub']}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


def example_error_handling():
    """
    Example 8: Proper error handling
    """
    print("\n" + "=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    url = 'https://example.com/article'

    try:
        converter = Web2Ebook(url, output_dir='./output')
        results = converter.convert(formats=['epub', 'pdf', 'mobi'])

        print("Conversion successful!")
        for format_type, path in results.items():
            print(f"  {format_type}: {path}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        print("Please check:")
        print("  1. Internet connection")
        print("  2. URL accessibility")
        print("  3. Calibre installation (for MOBI)")


def example_custom_output_naming():
    """
    Example 9: Working with output files
    """
    print("\n" + "=" * 60)
    print("Example 9: Custom Output Handling")
    print("=" * 60)

    import os
    import shutil

    url = 'https://example.com/article'

    # Convert to temporary location
    converter = Web2Ebook(url, output_dir='./temp_output')
    results = converter.convert(formats=['epub'])

    # Move to custom location with custom name
    epub_path = results['epub']
    custom_path = './my_books/custom_name.epub'

    os.makedirs('./my_books', exist_ok=True)
    shutil.move(epub_path, custom_path)

    print(f"Ebook saved as: {custom_path}")


def example_real_world_workflow():
    """
    Example 10: Real-world workflow
    """
    print("\n" + "=" * 60)
    print("Example 10: Real-World Workflow")
    print("=" * 60)

    import os
    from datetime import datetime

    # Configuration
    urls = [
        'https://example.com/tutorial-part-1',
        'https://example.com/tutorial-part-2',
    ]

    output_base = './my_ebooks'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create output directory with timestamp
    output_dir = os.path.join(output_base, f'conversion_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)

    print(f"Output directory: {output_dir}")

    # Convert all URLs
    successful = []
    failed = []

    for url in urls:
        print(f"\nProcessing: {url}")
        try:
            converter = Web2Ebook(
                url,
                output_dir=output_dir,
                generate_cover=True
            )
            results = converter.convert(formats=['epub', 'pdf'])
            successful.append((url, results))
            print("  ✓ Success")
        except Exception as e:
            failed.append((url, str(e)))
            print(f"  ✗ Failed: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"Successful: {len(successful)}/{len(urls)}")
    print(f"Failed: {len(failed)}/{len(urls)}")

    if successful:
        print("\nSuccessful conversions:")
        for url, results in successful:
            print(f"\n  {url}")
            for format_type, path in results.items():
                print(f"    {format_type}: {path}")

    if failed:
        print("\nFailed conversions:")
        for url, error in failed:
            print(f"  {url}: {error}")


def main():
    """Run all examples"""
    print("Web2Ebook - Example Usage Scripts")
    print("Copyright (c) devsimsek")
    print()

    # Uncomment the examples you want to run:

    # example_basic_conversion()
    # example_specific_formats()
    # example_custom_cover()
    # example_no_cover()
    # example_metadata_extraction()
    # example_cover_generation_only()
    # example_batch_conversion()
    # example_error_handling()
    # example_custom_output_naming()
    # example_real_world_workflow()

    print("\nTo run examples, uncomment the desired example functions in main()")
    print("Or run individual examples by importing them:")
    print("  from examples import example_basic_conversion")
    print("  example_basic_conversion()")


if __name__ == '__main__':
    main()
