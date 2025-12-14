# Web Search MCP Server - Modifications

## Original Source
This MCP server is based on the web search server from:
- **Repository**: https://github.com/pskill9/web-search
- **Original Author**: pskill9
- **License**: Check original repository for license terms

## Modifications Made

### Problem Addressed
The original server was experiencing issues with Google's anti-bot measures, returning empty results due to JavaScript-heavy pages designed to prevent automated scraping.

### Solution Implemented
Created an enhanced version (`src/index-fixed.ts`) with the following improvements:

1. **Multi-Engine Search Strategy**:
   - Primary: DuckDuckGo HTML search (most reliable)
   - Backup: Bing search
   - Fallback: Google with alternative headers

2. **Robust Error Handling**:
   - Graceful fallback between search engines
   - Better error reporting and logging
   - Timeout handling for network requests

3. **Enhanced Parsing**:
   - Multiple CSS selectors for different search result formats
   - Better handling of URL formats and edge cases
   - Improved text extraction and cleaning

### Files Modified/Added
- `src/index-fixed.ts` - Enhanced search server implementation
- `build-fixed/index-fixed.js` - Compiled version
- `test-fixed.js` - Test script for the enhanced version
- `debug-search.js` - Debugging utilities
- `test-search.js` - Original test script (modified)

### Performance Improvements
- Reduced reliance on Google's increasingly restrictive search API
- Better success rate for search queries
- More consistent results across different query types

### Testing Results
- ✅ Successfully finds KubeCon 2025 North America Sched.com URL
- ✅ Handles specific presentation searches
- ✅ Rate limiting compatible (100ms delays between requests)
- ✅ Fallback mechanisms working properly

## Usage
The enhanced server maintains the same MCP interface as the original:
- Tool name: `search`
- Parameters: `query` (required), `limit` (optional, max 10)
- Returns: Array of search results with title, url, description

## Attribution
Original concept and MCP server framework by pskill9. Enhancements for reliability and multi-engine support added for conference data extraction project.