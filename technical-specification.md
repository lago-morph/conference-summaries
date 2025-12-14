# Conference Data Extraction - Technical Specification
## KubeCon + CloudNativeCon North America 2025

### Overview
This document provides the technical specification for automatically extracting conference presentation data from Sched.com websites, specifically tested on KubeCon 2025 North America.

### Conference Information
- **Conference**: KubeCon + CloudNativeCon North America 2025
- **Sponsor**: CNCF (Cloud Native Computing Foundation)
- **Location**: Atlanta, GA, USA
- **Dates**: November 9-13, 2025
- **Sched Identifier**: `kccncna2025`
- **Main URL**: https://kccncna2025.sched.com/list/

### Phase 1: Discovery Method ✅ COMPLETED

#### Search Strategy
Use web search to find Sched.com conference URLs:
- **Search Query**: `"[Conference Name]" sched.com`
- **Example**: `"KubeCon 2025 North America" sched.com`
- **Result Pattern**: `https://[identifier].sched.com/list/`

#### Implementation
- **Tool**: Enhanced MCP web search server with multi-engine support
- **Engines**: DuckDuckGo (primary), Bing (backup), Google (fallback)
- **Rate Limiting**: 100ms delays between requests

### Phase 2: Conference Page Structure ✅ COMPLETED

#### Main Schedule Page Analysis
- **URL Pattern**: `https://[identifier].sched.com/list/`
- **Total Events**: 542 presentations found
- **Page Structure**: Standard Sched.com layout

#### CSS Selectors for Conference Metadata
```css
/* Conference name */
h1

/* Page title */
title

/* Meta description (contains location/dates) */
meta[name="description"]
meta[name="twitter:description"]
```

#### CSS Selectors for Presentation Listings
```css
/* All presentation containers */
.event

/* Presentation links */
.event a.name

/* Presentation titles */
.event a.name (text content)

/* Event URLs */
.event a.name[href] (href attribute)

/* Event times */
h3 (following event containers)

/* Timezone */
h3 span.tz
```

#### URL Pattern for Individual Presentations
- **Base**: `https://[identifier].sched.com/`
- **Individual Event**: `event/[EVENT_ID]/[URL_SLUG]`
- **Example**: `event/27FVb/simplifying-advanced-ai-model-serving-on-kubernetes-using-helm-charts-ajay-vohra-amazon-tianlu-caron-zhang-apple`

### Phase 3: Individual Presentation Page Structure ✅ COMPLETED

#### CSS Selectors for Video Links
```css
/* YouTube embedded videos */
iframe[src*="youtube"]

/* Video link patterns */
a[href*="youtube"]
a[href*="youtu.be"]
a[href*="vimeo"]
```

#### CSS Selectors for Presentation Files
```css
/* Direct file links */
a[href*=".pdf"]
a[href*=".ppt"]
a[href*=".pptx"]

/* File containers */
[class*="file"]
```

#### CSS Selectors for Session Details
```css
/* Date and time */
[class*="time"]
[class*="date"]

/* Speaker information */
.speaker
.presenter
[class*="speaker"]
```

### Data Extraction Patterns

#### Conference Metadata Structure
```yaml
conference:
  name: "KubeCon + CloudNativeCon North America 2025"
  sponsor: "CNCF"
  location: "Atlanta, GA, USA"
  dates: "November 9-13, 2025"
  sched_identifier: "kccncna2025"
  main_url: "https://kccncna2025.sched.com/list/"
```

#### Presentation Data Structure
```yaml
presentations:
  - id: "27FVb"
    title: "Simplifying Advanced AI Model Serving on Kubernetes Using Helm Charts"
    speakers:
      - name: "Ajay Vohra"
        company: "Amazon"
      - name: "Tianlu Caron Zhang"
        company: "Apple"
    date: "Tuesday November 11, 2025"
    time: "12:00pm - 12:30pm EST"
    location: "Building B | Level 4 | B401-402"
    detail_url: "https://kccncna2025.sched.com/event/27FVb/..."
    video_links:
      - platform: "youtube"
        url: "https://www.youtube.com/embed/PVB2hW8PuAM"
        type: "embedded"
    presentation_files:
      - type: "pdf"
        url: "https://static.sched.com/hosted_files/kccncna2025/1c/kubecon-2025-simplifying-advanced-model-serving-on-k8s-using-helm-charts.pdf"
        filename: "kubecon-2025-simplifying-advanced-model-serving-on-k8s-using-helm-charts.pdf"
      - type: "pptx"
        url: "https://static.sched.com/hosted_files/kccncna2025/a0/kubecon-2025-simplifying-advanced-model-serving-on-k8s-using-helm-charts.pptx"
        filename: "kubecon-2025-simplifying-advanced-model-serving-on-k8s-using-helm-charts.pptx"
```

### Implementation Algorithm

#### Step 1: Conference Discovery
```python
def find_conference_sched_url(conference_name):
    search_query = f'"{conference_name}" sched.com'
    results = web_search(search_query)
    for result in results:
        if 'sched.com' in result.url and '/list/' in result.url:
            return result.url
    return None
```

#### Step 2: Extract Presentation List
```python
def extract_presentations(main_url):
    html = fetch_page(main_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    presentations = []
    for event in soup.select('.event'):
        link = event.select_one('a.name')
        if link:
            presentations.append({
                'title': link.get_text().strip(),
                'url': urljoin(main_url, link['href']),
                'id': extract_id_from_url(link['href'])
            })
    return presentations
```

#### Step 3: Extract Individual Presentation Data
```python
def extract_presentation_details(presentation_url):
    html = fetch_page(presentation_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract video links
    video_links = []
    for iframe in soup.select('iframe[src*="youtube"]'):
        video_links.append({
            'platform': 'youtube',
            'url': iframe['src'],
            'type': 'embedded'
        })
    
    # Extract file links
    files = []
    for link in soup.select('a[href*=".pdf"], a[href*=".pptx"]'):
        files.append({
            'type': link['href'].split('.')[-1],
            'url': link['href'],
            'filename': link['href'].split('/')[-1]
        })
    
    # Extract session details
    time_info = soup.select_one('[class*="time"]')
    
    return {
        'video_links': video_links,
        'presentation_files': files,
        'session_details': time_info.get_text().strip() if time_info else None
    }
```

### Validation Results

#### Test Case 1: "Simplifying Advanced AI Model Serving..."
- **Status**: ✅ PASS
- **Video**: Found YouTube embedded video
- **Files**: Found both PDF and PPTX files
- **URL**: Working and accessible

#### Test Case 2: "The Myth of Portability..."
- **Status**: ✅ PASS
- **Video**: Found YouTube embedded video
- **Files**: No files found (as expected)
- **URL**: Working and accessible

#### Test Case 3: "Sponsored Demo Beyond the YAML..."
- **Status**: ❌ NOT FOUND
- **Note**: Presentation may not exist or title may be different

### Rate Limiting and Ethics
- **Request Delay**: 100ms minimum between requests
- **Total Presentations**: 542 events
- **Estimated Time**: ~54 seconds for complete extraction
- **Respectful Scraping**: Text-only extraction, no media downloading
- **Error Handling**: Graceful failures with retry logic

### File Storage Format
Data will be stored in YAML format for human readability and easy parsing:

```yaml
# conference-data.yaml
conference:
  name: "KubeCon + CloudNativeCon North America 2025"
  # ... conference metadata

presentations:
  - # ... presentation data
```

### Next Steps for Automation
1. Implement the extraction algorithm in Python
2. Add error handling and retry logic
3. Create progress tracking for large datasets
4. Add validation for extracted data
5. Test on multiple conference years for consistency