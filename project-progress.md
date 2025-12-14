# Conference Data Extraction Project - Progress Log

## Project Overview

**Goal**: Create an automated system to extract comprehensive CNCF KubeCon conference presentation data from Sched.com websites.

**Scope**: 
- Focus on CNCF/KubeCon conferences initially
- Extract conference metadata and presentation details
- Store data in YAML format
- Target video links (primarily YouTube) and presentation files

## The Process (3 Phases)

1. **Discovery Phase**: Web search for "<conference name> sched.com" to find Sched.com abbreviation/identifier
2. **Conference Scraping**: Visit `<abbreviation>.sched.com` to gather:
   - Conference metadata (name, CNCF as sponsor, location, dates)
   - List of all presentations with basic info (title, speakers, date, detail page links)
3. **Presentation Detail Scraping**: For each presentation, visit detail page to extract:
   - Video links (YouTube + other platforms)
   - Presentation file links (PDF, PPTX, etc.)

## Test Case: KubeCon 2025 North America (Atlanta)

Three sample presentations with different content patterns:

1. **"simplifying advanced ai model serving on kubernetes using helm charts"**
   - Has: YouTube video + presentation files (PPTX + PDF)

2. **"sponsored demo beyond the yaml architecting a composable secure and open source platform for the enterprise"**
   - Has: Neither video nor presentation files

3. **"the myth of portability why your cloud native app is married to your provider"**
   - Has: YouTube video only (no presentation files)

## Exploration Plan (Current Phase)

### Phase 1: Discovery Method Analysis ✅ BLOCKED
- Test web search strategies to find KubeCon 2025 North America Sched.com identifier
- **STATUS**: Installed web search MCP server, need to restart Kiro to activate

### Phase 2: Conference Page Structure Analysis (PENDING)
- Visit main conference Sched.com page
- Document page structure and HTML selectors
- Create structured documentation

### Phase 3: Individual Presentation Page Analysis (PENDING)
- Visit all three test presentation pages
- Document page structure variations
- Create extraction patterns for different content scenarios

### Phase 4: Documentation Creation (PENDING)
- Create technical specification document
- Document CSS selectors/XPath expressions
- Sample YAML output format
- Edge cases and variations

### Phase 5: Validation (PENDING)
- Test extraction patterns on sample presentations
- Verify data completeness and accuracy

## Technical Setup Completed

- ✅ Cloned web search MCP server from https://github.com/pskill9/web-search
- ✅ Installed dependencies and built server
- ✅ Created MCP configuration at `.kiro/settings/mcp.json`
- ⏳ **NEXT**: Restart Kiro to activate web search capabilities

## Next Steps After Restart

1. Test web search functionality
2. Search for "KubeCon 2025 North America sched.com"
3. Identify the Sched.com URL and abbreviation
4. Begin Phase 2: Conference page structure analysis

## Deliverables (Target)

- Technical specification document with page structures
- Sample YAML output showing target data format
- Notes on automation feasibility and challenges
- Extraction patterns for different presentation content types