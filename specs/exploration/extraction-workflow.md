# Conference Data Extraction Workflow

This document defines the complete step-by-step process for extracting conference data from Sched.com websites.

## Overview

The extraction process consists of 5 main phases, each with specific responsibilities and data gathering requirements.

## Phase 1: Conference Discovery

**Objective**: Find the Sched.com URL for a given conference name

### Input
- Conference name (e.g., "KubeCon 2025 North America")

### Process
1. **Web Search**: Search for `"[Conference Name]" sched.com`
2. **URL Pattern Matching**: Look for URLs matching `https://[identifier].sched.com/`
3. **Validation**: Verify the URL returns a valid conference page

### Output
- `sched_identifier`: The conference identifier (e.g., "kccncna2025")
- `main_url`: The main conference URL (e.g., "https://kccncna2025.sched.com/list/")

### Data Gathered
```yaml
conference:
  sched_identifier: "kccncna2025"
  main_url: "https://kccncna2025.sched.com/list/"
```

### Implementation
- Use web search MCP server with multiple engines (DuckDuckGo, Bing, Google)
- Pattern match against search results
- Validate URL accessibility

---

## Phase 2: Conference Metadata Extraction

**Objective**: Extract basic conference information from the main page

### Input
- Main conference URL from Phase 1

### Process
1. **Fetch Main Page**: GET request to main conference URL
2. **Parse HTML**: Extract metadata using CSS selectors
3. **Clean Data**: Format dates, locations, and names

### CSS Selectors Used
```css
h1                              /* Conference name */
title                           /* Page title */
meta[name="description"]        /* Location and dates */
meta[name="twitter:description"] /* Alternative metadata */
```

### Data Gathered
```yaml
conference:
  name: "KubeCon + CloudNativeCon North America 2025"
  sponsor: "CNCF"  # Inferred from conference type
  location: "Atlanta, GA, USA"
  dates: "November 9-13, 2025"
  extraction_date: "2025-01-13"
```

### Implementation
- Parse HTML with Cheerio
- Extract and clean text content
- Infer sponsor from conference name patterns
- Format dates consistently

---

## Phase 3: Track Discovery and Filtering

**Objective**: Extract all available tracks and allow user filtering

### Input
- Main conference URL from Phase 1

### Process
1. **Find Track Links**: Locate filter links on main page
2. **Extract Track Data**: Parse track names and URLs
3. **Handle Special Characters**: Decode emoji and Unicode
4. **User Selection**: Present tracks for filtering (optional)

### CSS Selectors Used
```css
a[href*="/overview/type/"]      /* Track filter links */
a[href*="type/"]               /* Alternative track links */
```

### Data Gathered
```yaml
available_tracks:
  - name: "AI + ML"
    display_text: "AI + ML"
    list_url: "https://kccncna2025.sched.com/list/type/AI+%2B+ML"
    overview_url: "https://kccncna2025.sched.com/overview/type/AI%20%2B%20ML"
    has_emoji: false
    has_subtypes: false

track_filtering:
  enabled: true
  default_action: "include_all"
  user_selectable: true
  exclude_by_default: ["Breaks", "Registration"]
```

### Implementation
- Parse track filter links
- URL decode track names
- Detect emoji characters
- Present user interface for track selection

---

## Phase 4: Presentation List Extraction

**Objective**: Get list of all presentations (with optional track filtering)

### Input
- Main conference URL from Phase 1
- Excluded tracks list from Phase 3 (optional)

### Process
1. **Fetch Presentation List**: GET request to main conference page
2. **Parse Event Containers**: Extract presentation links and basic info
3. **Apply Track Filtering**: Skip presentations in excluded tracks (if enabled)
4. **Build Presentation Index**: Create list of presentations to process

### CSS Selectors Used
```css
.event                          /* Presentation containers */
.event a.name                   /* Presentation links */
.event a.name[href]            /* Event URLs */
h3                             /* Time sections */
h3 span.tz                     /* Timezone info */
```

### Data Gathered
```yaml
presentations:
  - id: "27FVb"
    title: "Simplifying Advanced AI Model Serving on Kubernetes Using Helm Charts"
    detail_url: "https://kccncna2025.sched.com/event/27FVb/..."
    # Additional details filled in Phase 5
```

### Implementation
- Parse HTML event containers
- Extract presentation IDs from URLs
- Apply track filtering if enabled
- Build processing queue

---

## Phase 5: Individual Presentation Detail Extraction

**Objective**: Extract complete details for each presentation

### Input
- List of presentation URLs from Phase 4

### Process
1. **Fetch Detail Page**: GET request to individual presentation URL
2. **Extract All Data**: Parse speakers, times, tracks, videos, files
3. **Handle Special Cases**: Emoji, sub-types, missing data
4. **Rate Limiting**: 100ms delay between requests

### CSS Selectors Used
```css
/* Video Links */
iframe[src*="youtube"]          /* YouTube embedded videos */
a[href*="youtube"]             /* YouTube direct links */
a[href*="vimeo"]               /* Vimeo links */

/* Presentation Files */
a[href*=".pdf"]                /* PDF files */
a[href*=".pptx"]               /* PowerPoint files */

/* Session Details */
[class*="time"]                 /* Date and time */
.speaker, .presenter           /* Speaker information */
.sched-event-type a[href*="type/"] /* Track/type links */
.tip-custom-fields a[href*="/company/"] /* Experience level */
```

### Data Gathered
```yaml
presentations:
  - id: "27FVb"
    title: "Simplifying Advanced AI Model Serving on Kubernetes Using Helm Charts"
    speakers:
      - name: "Ajay Vohra"
        company: "Amazon"
    date: "Tuesday November 11, 2025"
    time: "12:00pm - 12:30pm EST"
    location: "Building B | Level 4 | B401-402"
    track: "AI + ML"
    track_url: "https://kccncna2025.sched.com/type/AI+%2B+ML"
    sub_track: null
    sub_track_url: null
    experience_level: "Intermediate"
    video_links:
      - platform: "youtube"
        url: "https://www.youtube.com/embed/PVB2hW8PuAM"
        type: "embedded"
        video_id: "PVB2hW8PuAM"
    presentation_files:
      - type: "pdf"
        url: "https://static.sched.com/hosted_files/..."
        filename: "presentation.pdf"
    content_status:
      has_video: true
      has_presentation_files: true
      file_count: 2
```

### Implementation
- Parse individual presentation pages
- Extract video embed codes and direct links
- Find presentation file downloads
- Handle track hierarchies (main track + sub-track)
- Detect and preserve emoji characters
- Track content availability statistics

---

## Error Handling and Edge Cases

### Rate Limiting
- **Delay**: 100ms minimum between requests
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout**: 15 second timeout per request

### Special Character Handling
- **Emoji Support**: Preserve Unicode characters in titles and tracks
- **URL Encoding**: Properly decode track URLs with special characters
- **Text Cleaning**: Remove extra whitespace and normalize formatting

### Missing Data Scenarios
- **No Video**: Set `video_links: []` and `has_video: false`
- **No Files**: Set `presentation_files: []` and `has_presentation_files: false`
- **Missing Speakers**: Handle events without speaker information
- **Sub-tracks**: Detect and parse hierarchical track structures

### Validation
- **URL Validation**: Verify all extracted URLs are accessible
- **Data Completeness**: Track success rates and missing data
- **Format Consistency**: Ensure consistent date/time formatting

---

## Performance Characteristics

### Timing Estimates (KubeCon 2025 North America - 542 presentations)
- **Phase 1**: Discovery - ~2 seconds
- **Phase 2**: Conference metadata - ~3 seconds  
- **Phase 3**: Track extraction - ~2 seconds
- **Phase 4**: Presentation list - ~3 seconds
- **Phase 5**: Detail extraction - ~325 seconds (542 × 0.6s average)
- **Total**: ~5.6 minutes for complete extraction

### Memory Usage
- **Minimal**: Process presentations one at a time
- **Temporary Storage**: HTML content discarded after parsing
- **Output Size**: ~500KB YAML for 542 presentations

### Success Rates (Based on Testing)
- **Conference Discovery**: 100%
- **Metadata Extraction**: 100%
- **Track Extraction**: 100%
- **Presentation Listing**: 100%
- **Detail Extraction**: 80-90% (some presentations may have missing data)

---

## Output Format

The final output is a single YAML file containing all extracted data in the structure defined in `data-structure-spec.yaml`.

### File Organization
```yaml
conference:          # Phase 2 data
  name: "..."
  sponsor: "..."
  # ... metadata

available_tracks:    # Phase 3 data
  - name: "..."
    # ... track info

track_filtering:     # Phase 3 configuration
  enabled: true
  # ... filtering settings

presentations:       # Phase 4 + 5 data
  - id: "..."
    title: "..."
    # ... complete presentation data

extraction_summary:  # Statistics
  total_presentations_found: 542
  success_rate: "85%"
  # ... summary stats
```

This workflow provides a complete, tested approach for automated conference data extraction that can be implemented in any programming language.