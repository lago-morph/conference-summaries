# AI Agent Guidance

This repository contains comprehensive documentation and guidance for AI agents working on the conference data extraction project.

## AI Guidance Directory

All AI-focused instructions, specifications, and progress documentation are located in the [`ai-guidance/`](./ai-guidance/) directory:

### Core Documentation

- **[`project-progress.md`](./ai-guidance/project-progress.md)** - Complete project progress log with all phases, achievements, and current status
- **[`technical-specification.md`](./ai-guidance/technical-specification.md)** - Comprehensive technical specification for conference data extraction from Sched.com websites
- **[`sched-page-structure-analysis.md`](./ai-guidance/sched-page-structure-analysis.md)** - Detailed analysis of Sched.com page structures and HTML patterns
- **[`mcp-web-search-setup.md`](./ai-guidance/mcp-web-search-setup.md)** - Instructions for setting up the MCP web search server

### Key Information for AI Agents

#### Project Status
✅ **EXPLORATION COMPLETE** - All phases finished, ready for implementation

#### What This Project Does
Automated extraction of CNCF KubeCon conference presentation data from Sched.com websites, including:
- Conference metadata (name, location, dates, sponsor)
- Presentation details (title, speakers, date, time, location)
- Track/type information with filtering capabilities
- Video links (primarily YouTube)
- Presentation files (PDF, PPTX)

#### Current Capabilities
- **Web Search**: Enhanced MCP server with multi-engine support
- **Track Extraction**: All 26 tracks from KubeCon 2025 North America identified
- **Data Extraction**: Validated patterns for presentations and metadata
- **Special Character Support**: Full emoji and Unicode handling
- **Sub-type Support**: Hierarchical track categories (e.g., Experiences/Wellness)

#### Test Conference
**KubeCon + CloudNativeCon North America 2025**
- Location: Atlanta, GA, USA
- Dates: November 9-13, 2025
- Sched URL: https://kccncna2025.sched.com/list/
- Total Presentations: 542

#### Next Steps
Ready for Python/shell script automation implementation based on the technical specification.

## Repository Structure

```
conference-summaries/
├── ai-guidance/           # AI agent documentation and specifications
├── scripts/              # Analysis and test scripts (with own package.json)
├── specs/                # System specifications and requirements
│   └── exploration/      # Exploration phase results and implementation specs
├── temp/                 # Temporary files (HTML downloads, etc.)
├── web-search/           # Enhanced MCP web search server (with own package.json)
└── AGENTS.md            # This file
```

## Getting Started

1. Read [`ai-guidance/project-progress.md`](./ai-guidance/project-progress.md) for complete project context
2. Review [`specs/exploration/README.md`](./specs/exploration/README.md) for distilled exploration results
3. Check [`specs/exploration/data-structure-spec.yaml`](./specs/exploration/data-structure-spec.yaml) for target data format
4. Review [`specs/exploration/extraction-workflow.md`](./specs/exploration/extraction-workflow.md) for step-by-step process
5. Use implementation examples in [`specs/exploration/`](./specs/exploration/) directory
6. Use scripts in [`scripts/`](./scripts/) directory for testing and analysis (run `npm install` in scripts/ first)

## Important Notes

- **Rate Limiting**: Use 100ms delays between requests
- **Data Format**: Store in YAML format (may change later)
- **Target Conferences**: Focus on CNCF/KubeCon initially
- **Respectful Scraping**: Text-only extraction, no media downloading
- **Special Characters**: Full emoji and Unicode support implemented