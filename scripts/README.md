# Analysis and Test Scripts

This directory contains various scripts used for testing, analysis, and exploration during the conference data extraction project development.

## Script Categories

### Web Search Testing
- **`test-search.js`** - Basic MCP web search server testing
- **`test-fixed.js`** - Enhanced web search testing with multiple engines
- **`debug-search.js`** - Debug script for troubleshooting search issues

### Conference Analysis Scripts
- **`analyze-sched.js`** - Main conference page structure analysis
- **`analyze-sched-structure.js`** - Detailed Sched.com page structure exploration
- **`analyze-tracks.js`** - Extract all available conference tracks/types
- **`analyze-individual-presentation.js`** - Individual presentation page analysis
- **`analyze-contribfest.js`** - Analysis of ContribFest presentation with emoji
- **`analyze-fun-run.js`** - Analysis of Fun Run event with sub-types

## Usage

These scripts were used during the exploration phase to understand Sched.com page structures and validate extraction patterns. They require:

1. Node.js environment
2. Dependencies: `axios`, `cheerio`
3. Working MCP web search server (for search-related scripts)

## Rate Limiting

All scripts implement 100ms delays between requests to be respectful to Sched.com servers.

## Output

Scripts generate various outputs:
- Console logs with analysis results
- JSON files with extracted data (saved to `temp/` directory)
- HTML files for debugging (saved to `temp/` directory)

## Target Conference

Scripts are configured for **KubeCon + CloudNativeCon North America 2025**:
- Base URL: `https://kccncna2025.sched.com/`
- Total presentations: 542
- Available tracks: 26

## Note

These are exploration and analysis tools, not production scripts. For production implementation, refer to the technical specification in `ai-guidance/technical-specification.md`.