# Excluding URLs from Crawling

When using `--crawl` mode, you can exclude specific URLs or patterns from being included in your ebook.

## Quick Examples

### Command Line

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
  --exclude '*admin*' '*/comments' '*/tag/*'
```

**Load from file:**
```bash
python web2ebook.py https://example.com/docs \
  --crawl \
  --exclude-file exclude.txt
```

## Exclude File Format

Create a text file (e.g., `exclude.txt`) with one URL/pattern per line:

```
# Comments start with #
# Empty lines are ignored

# Exact URLs
https://example.com/login
https://example.com/contact

# Wildcard patterns
*admin*
*/tag/*
*/comment*
https://example.com/docs/*/index.html

# Substring matching
login
signup
```

## Pattern Matching

### Wildcards
- `*` - Matches any characters
- `?` - Matches single character

### Examples
- `*admin*` - Matches any URL containing "admin"
- `*/tag/*` - Matches any URL with "/tag/" in path
- `https://example.com/docs/*/index.html` - Matches index.html in any subdirectory

### Substring Matching
If no wildcards are used, the pattern matches anywhere in the URL:
- `login` matches `https://example.com/login` and `https://example.com/user-login`
- `comment` matches `https://example.com/article/comments` and `https://example.com/post/comment-form`

## Common Exclusion Patterns

### Skip Navigation/Structure
```
*/index.html
*/sitemap
*/archive
*/category/*
*/tag/*
```

### Skip User Actions
```
*login*
*signup*
*/profile
*/settings
*/account
```

### Skip Comments/Social
```
*comment*
*/comments
*/reply
*/share
*/tweet
```

### Skip Admin Areas
```
*/admin/*
*/edit
*/delete
*/dashboard
```

## Using with Makefile

```bash
# With exclude URLs
make run URL=https://example.com ARGS='--crawl --exclude "*admin*" "*/tag/*"'

# With exclude file
make run URL=https://example.com ARGS='--crawl --exclude-file exclude.txt'
```

## Tips

✅ **Use exclude files for complex rules** - Easier to manage and reuse

✅ **Start broad, refine later** - Exclude major patterns first, add specifics as needed

✅ **Test your patterns** - Run with `--max-pages 5` first to verify exclusions work

✅ **Comment your exclude files** - Document why certain URLs are excluded

⚠️ **Wildcards are greedy** - `*admin*` will match more than you might expect

⚠️ **Case sensitive** - Patterns match exactly as written

Copyright (c) devsimsek
