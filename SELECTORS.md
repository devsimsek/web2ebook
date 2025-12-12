# CSS Selectors Guide for Web2Ebook

**Copyright (c) devsimsek**

This guide explains how to use CSS selectors to precisely control content extraction.

## Overview

CSS selectors let you target specific HTML elements on a page:
- **`--content-selector`** - Target the main content container
- **`--exclude-selectors`** - Remove unwanted elements (comments, ads, etc.)

## Content Selector

Use `--content-selector` to specify exactly which element contains the main content.

### Basic Examples

**Target by tag:**
```bash
python web2ebook.py https://example.com/article \
  --content-selector "article"
```

**Target by ID:**
```bash
python web2ebook.py https://example.com/article \
  --content-selector "#main-content"
```

**Target by class:**
```bash
python web2ebook.py https://example.com/article \
  --content-selector ".post-content"
```

**Complex selector:**
```bash
python web2ebook.py https://example.com/article \
  --content-selector "main article.post-body"
```

### When to Use Content Selector

✅ **Use when:**
- The automatic detection grabs too much content
- You want only a specific section
- The page has multiple `<article>` tags
- You know the exact container element

⚠️ **Not needed when:**
- Automatic detection works fine
- Page uses standard HTML5 semantic tags
- Content is in obvious containers

## Exclude Selectors

Use `--exclude-selectors` to remove specific elements from the extracted content.

### Basic Examples

**Remove comments section:**
```bash
python web2ebook.py https://example.com/article \
  --exclude-selectors ".comments"
```

**Remove multiple elements:**
```bash
python web2ebook.py https://example.com/article \
  --exclude-selectors ".comments" ".sidebar" "#related-posts"
```

**Remove by tag:**
```bash
python web2ebook.py https://example.com/article \
  --exclude-selectors "aside" "nav"
```

### Common Use Cases

**Remove comments:**
```bash
--exclude-selectors ".comments" "#disqus_thread" ".comment-section"
```

**Remove ads:**
```bash
--exclude-selectors ".ad" ".advertisement" "#ads" ".sponsored"
```

**Remove social sharing:**
```bash
--exclude-selectors ".share-buttons" ".social-share" ".sharing-widget"
```

**Remove related posts:**
```bash
--exclude-selectors ".related-posts" "#you-might-like" ".recommendations"
```

**Remove navigation:**
```bash
--exclude-selectors "nav" ".breadcrumbs" ".pagination" ".nav-links"
```

## CSS Selector Syntax

### Element Selectors
```
article          - All <article> elements
div              - All <div> elements
p                - All <p> elements
```

### Class Selectors
```
.comments        - Elements with class="comments"
.post-content    - Elements with class="post-content"
.ad              - Elements with class="ad"
```

### ID Selectors
```
#main            - Element with id="main"
#content         - Element with id="content"
#comments        - Element with id="comments"
```

### Combined Selectors
```
div.post         - <div> with class="post"
article#main     - <article> with id="main"
.post .comments  - .comments inside .post
```

### Attribute Selectors
```
[role="main"]              - Elements with role="main"
[class*="comment"]         - Class contains "comment"
[id^="ad"]                 - ID starts with "ad"
```

## Complete Examples

### Example 1: Blog Post
```bash
# Get article content, remove comments and sidebar
python web2ebook.py https://blog.example.com/post \
  --content-selector "article.post" \
  --exclude-selectors ".comments" ".sidebar" ".author-bio"
```

### Example 2: Documentation Site
```bash
# Get main docs content, remove navigation
python web2ebook.py https://docs.example.com/guide \
  --content-selector ".documentation-content" \
  --exclude-selectors "nav" ".toc" ".breadcrumbs"
```

### Example 3: News Article
```bash
# Get article, remove ads and related articles
python web2ebook.py https://news.example.com/article \
  --content-selector "#article-body" \
  --exclude-selectors ".ad" ".related" ".newsletter-signup"
```

### Example 4: Tutorial with Crawl
```bash
# Crawl multiple tutorials, clean each page
python web2ebook.py https://tutorials.example.com/part-1 \
  --crawl --max-pages 10 \
  --content-selector ".tutorial-content" \
  --exclude-selectors ".comments" ".sidebar" "aside" \
  --include "*/part-*.html"
```

### Example 5: Medium Article
```bash
python web2ebook.py https://medium.com/@user/article \
  --content-selector "article" \
  --exclude-selectors ".pw-responses" ".pw-popover" "aside"
```

### Example 6: Dev.to Post
```bash
python web2ebook.py https://dev.to/user/post \
  --content-selector "#article-body" \
  --exclude-selectors ".comments" ".crayons-article__aside"
```

## Finding Selectors

### Method 1: Browser Inspector
1. Open the page in your browser
2. Right-click on the content → "Inspect Element"
3. Look for the element in DevTools
4. Note the class, ID, or tag name

### Method 2: View Source
1. Right-click → "View Page Source"
2. Search for content text
3. Find the containing element
4. Note its selector

### Method 3: Test Selectors
Use browser console to test:
```javascript
// Test content selector
document.querySelector("article")

// Test exclude selector
document.querySelectorAll(".comments")
```

## Tips & Best Practices

### Content Selector
✅ **Do:**
- Use the most specific selector that works
- Prefer IDs over classes when available
- Test on multiple pages if crawling
- Start broad, then narrow down

❌ **Don't:**
- Use overly complex selectors
- Rely on generated class names
- Use position-based selectors (`:nth-child`)

### Exclude Selectors
✅ **Do:**
- Remove distracting elements
- Clean up navigation and ads
- Test to ensure you don't remove too much
- Use multiple selectors for thorough cleaning

❌ **Don't:**
- Remove actual content
- Over-exclude (might remove images/code)
- Use selectors that might not exist on all pages

## Debugging

**Content selector not working?**
- Verify the element exists: `View Source` or browser inspector
- Try a simpler selector: `article` instead of `article.post-content`
- Check if multiple elements match (it uses the first)

**Exclude selector not removing elements?**
- Check spelling and syntax
- Verify the element exists on the page
- Try in browser console: `document.querySelectorAll("your-selector")`

**Too much/little content extracted?**
- Adjust content selector to be more/less specific
- Add more exclude selectors
- Check the default behavior first (might be fine)

## Fallback Behavior

If your selectors don't work, the tool falls back to:
1. User's `--content-selector` (if provided)
2. Common patterns: `<main>`, `<article>`, `#content`
3. Entire `<body>` if nothing found

Elements always removed by default:
- `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, `<iframe>`, `<noscript>`

## Combining with Other Features

**With crawling:**
```bash
python web2ebook.py https://example.com/tutorial \
  --crawl --max-pages 20 \
  --content-selector ".tutorial-body" \
  --exclude-selectors ".comments" \
  --include "*/tutorial/*.html"
```

**With include/exclude URLs:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --include "*/docs/*.html" \
  --exclude "*/index.html" \
  --content-selector "#documentation" \
  --exclude-selectors "nav" ".sidebar"
```

## Common Websites

### Medium
```bash
--content-selector "article" \
--exclude-selectors ".pw-responses" "aside"
```

### Dev.to
```bash
--content-selector "#article-body" \
--exclude-selectors ".comments"
```

### GitHub Markdown
```bash
--content-selector ".markdown-body" \
--exclude-selectors ".breadcrumbs"
```

### WordPress
```bash
--content-selector ".entry-content" \
--exclude-selectors ".comments" ".related-posts"
```

### Substack
```bash
--content-selector ".post-content" \
--exclude-selectors ".subscription-widget"
```

---

**Made with ❤️ by devsimsek**