# AI Agent Guidance

This repository contains a conference data extraction system for CNCF KubeCon conferences from Sched.com websites.

## Project Status
✅ **EXPLORATION COMPLETE** - Ready for production implementation

## What This System Does
Automated extraction of conference presentation data including:
- Conference metadata (name, location, dates, sponsor)
- Presentation details (title, speakers, date, time, location, tracks)
- Video links (primarily YouTube) and presentation files (PDF, PPTX)
- Track filtering system (26 tracks identified, including emoji support)

## Current Capabilities
- **Web Search**: Enhanced MCP server with multi-engine support
- **Data Extraction**: Validated patterns for 542 presentations
- **Special Character Support**: Full emoji and Unicode handling
- **Track Filtering**: User-selectable presentation categories

## Test Conference Validated
**KubeCon + CloudNativeCon North America 2025** (Atlanta, GA, November 9-13, 2025)
- 542 presentations across 26 tracks
- 80-90% extraction success rate
- ~5.6 minutes processing time

## Repository Structure

```
conference-summaries/
├── ai-guidance/           # Context-sensitive setup guides (read headers first)
├── scripts/              # Analysis and test scripts (with own package.json)
├── specs/exploration/     # Exploration results and implementation specs (reference as needed)
├── temp/                 # Temporary files (HTML downloads, etc.)
├── web-search/           # Enhanced MCP web search server (production ready)
└── AGENTS.md            # This file (always read)
```

## Documentation Access Strategy

### Always Read
- **This file** (`AGENTS.md`) - Essential startup context

### Read When Needed (Check Headers First)
- **`ai-guidance/`** - Context-sensitive guides (e.g., MCP server setup)
  - Each document has a header indicating when to read it

### Reference for Specific Tasks
- **`specs/exploration/`** - Complete exploration results and implementation specs
  - Use during requirements gathering, design, and implementation phases
  - Contains data structures, workflows, algorithms, and CSS selectors

## Quick Start for Common Tasks

### If you need to implement the system:
1. Review `specs/exploration/README.md` for overview
2. Check `specs/exploration/data-structure-spec.yaml` for output format
3. Follow `specs/exploration/extraction-workflow.md` for step-by-step process

### If web search isn't working:
1. Read `ai-guidance/mcp-web-search-setup.md` (check header first)

### If you need to analyze or test:
1. Use scripts in `scripts/` directory (run `npm install` first)

## Key Implementation Notes
- **Rate Limiting**: 100ms delays between requests
- **Data Format**: YAML output
- **Target**: CNCF/KubeCon conferences initially
- **Approach**: Respectful text-only extraction