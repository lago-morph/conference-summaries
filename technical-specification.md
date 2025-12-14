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

/* Track/Type information */
.sched-event-type a[href*="type/"]

/* Experience level */
.tip-custom-fields a[href*="/company/"]
```

### Special Character Handling

#### Unicode and Emoji Support
- **Emoji in Titles**: Presentations may contain emoji characters (e.g., 🚨, 🏃)
- **URL Encoding**: Track URLs with special characters are URL-encoded (e.g., %F0%9F%9A%A8)
- **Text Extraction**: Use proper Unicode handling to preserve emoji and special characters
- **YAML Storage**: Store emoji and Unicode characters directly in YAML (UTF-8 encoding)

#### Implementation Notes
```python
# Proper Unicode handling for titles and track names
title = soup.select_one('.event .name').get_text().strip()  # Preserves emoji
track_name = urllib.parse.unquote_plus(track_url.split('type/')[1])  # Decodes URL encoding
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
    track: "AI + ML"
    track_url: "https://kccncna2025.sched.com/type/AI+%2B+ML"
    sub_track: null  # No sub-track for this presentation
    sub_track_url: null
    experience_level: "Intermediate"
    special_characters:
      has_emoji: false
      emoji_in_title: null
      emoji_in_track: null
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

### Track/Type Extraction ✅ COMPLETED

#### Track Discovery Method
Tracks are available as filter links on the main conference page with the URL pattern:
- **Filter URL Pattern**: `https://[identifier].sched.com/overview/type/[TRACK_NAME]`
- **List URL Pattern**: `https://[identifier].sched.com/list/type/[TRACK_NAME]`
- **Total Tracks Found**: 26 tracks for KubeCon 2025 North America

#### CSS Selectors for Track Extraction
```css
/* Track filter links */
a[href*="/overview/type/"]
a[href*="type/"]

/* Alternative selectors */
.filter a
.type-filter a
[class*="filter"] a
[class*="type"] a
```

#### Track Data Structure
```yaml
available_tracks:
  - name: "AI + ML"                    # Decoded track name
    display_text: "AI + ML"            # Text shown on page
    list_url: "https://kccncna2025.sched.com/list/type/AI+%2B+ML"
    overview_url: "https://kccncna2025.sched.com/overview/type/AI%20%2B%20ML"
    has_emoji: false                   # Whether track contains emoji
    has_subtypes: false                # Whether track has sub-categories
```

#### Special Track Considerations
- **Emoji Tracks**: Some tracks contain emoji (e.g., "⚡ Lightning Talks", "🚨 ContribFest")
- **URL Encoding**: Track names with special characters are URL-encoded in links
- **Sub-types**: Some tracks have sub-categories (e.g., "Experiences/Wellness")
- **Filtering**: Users can select tracks to include/exclude from extraction

#### Track Filtering Configuration
```yaml
track_filtering:
  enabled: true
  default_action: "include_all"
  user_selectable: true
  exclude_by_default:
    - "Breaks"
    - "Registration"
    - "Solutions Showcase"
```

### Implementation Algorithm

#### Step 0: Track Discovery (New)
```python
def extract_available_tracks(main_url):
    html = fetch_page(main_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    tracks = []
    track_links = soup.select('a[href*="/overview/type/"]')
    
    for link in track_links:
        href = link['href']
        display_text = link.get_text().strip()
        
        # Extract track name from URL
        if '/overview/type/' in href:
            type_part = href.split('/overview/type/')[1]
            track_name = urllib.parse.unquote_plus(type_part)
            
            # Check for emoji
            has_emoji = any(ord(char) > 127 for char in display_text)
            
            tracks.append({
                'name': track_name,
                'display_text': display_text,
                'list_url': href.replace('/overview/', '/list/'),
                'overview_url': urljoin(main_url, href),
                'has_emoji': has_emoji
            })
    
    return sorted(tracks, key=lambda x: x['name'])
```

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

#### Step 2: Extract Presentation List (with Track Filtering)
```python
def extract_presentations(main_url, excluded_tracks=None):
    html = fetch_page(main_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    presentations = []
    for event in soup.select('.event'):
        link = event.select_one('a.name')
        if link:
            presentation = {
                'title': link.get_text().strip(),
                'url': urljoin(main_url, link['href']),
                'id': extract_id_from_url(link['href'])
            }
            
            # If track filtering is enabled, check track before adding
            if excluded_tracks:
                # Extract track info quickly to filter
                track_info = extract_track_from_url(presentation['url'])
                if track_info and track_info['track'] not in excluded_tracks:
                    presentations.append(presentation)
            else:
                presentations.append(presentation)
    
    return presentations

def extract_track_from_url(presentation_url):
    """Quick track extraction for filtering purposes"""
    try:
        html = fetch_page(presentation_url)
        soup = BeautifulSoup(html, 'html.parser')
        
        track_link = soup.select_one('.sched-event-type a[href*="type/"]')
        if track_link:
            href = track_link['href']
            if 'type/' in href:
                type_part = href.split('type/')[1].split('/')[0]
                return {'track': urllib.parse.unquote_plus(type_part)}
        return None
    except:
        return None
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
    
    # Extract track/type information (including sub-types)
    track_links = soup.select('.sched-event-type a[href*="type/"]')
    track = None
    track_url = None
    sub_track = None
    sub_track_url = None
    
    for link in track_links:
        href = link['href']
        text = link.get_text().strip()
        
        if 'type/' in href:
            type_part = href.split('type/')[1]
            parts = type_part.split('/')
            
            if len(parts) == 1:
                # Main type only
                track = urllib.parse.unquote_plus(parts[0])
                track_url = urljoin(presentation_url, href)
            elif len(parts) == 2:
                # Sub-type (URL contains main type + sub-type)
                if not track:  # Set main type if not already set
                    track = urllib.parse.unquote_plus(parts[0])
                    track_url = urljoin(presentation_url, f"type/{parts[0]}")
                sub_track = urllib.parse.unquote_plus(parts[1])
                sub_track_url = urljoin(presentation_url, href)
    
    # Extract experience level
    experience_link = soup.select_one('.tip-custom-fields a[href*="/company/"]')
    experience_level = experience_link.get_text().strip() if experience_link else None
    
    return {
        'video_links': video_links,
        'presentation_files': files,
        'track': track,
        'track_url': track_url,
        'sub_track': sub_track,
        'sub_track_url': sub_track_url,
        'experience_level': experience_level,
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

### Complete Extraction Workflow

#### Full Process with Track Filtering
```python
def extract_conference_data(conference_name, excluded_tracks=None):
    # Step 0: Find conference URL
    main_url = find_conference_sched_url(conference_name)
    if not main_url:
        raise Exception(f"Could not find Sched.com URL for {conference_name}")
    
    # Step 1: Extract available tracks for user selection
    available_tracks = extract_available_tracks(main_url)
    print(f"Found {len(available_tracks)} available tracks")
    
    # Step 2: Get user track preferences (if interactive)
    if excluded_tracks is None:
        excluded_tracks = get_user_track_preferences(available_tracks)
    
    # Step 3: Extract presentation list with filtering
    presentations = extract_presentations(main_url, excluded_tracks)
    print(f"Found {len(presentations)} presentations after filtering")
    
    # Step 4: Extract detailed data for each presentation
    detailed_presentations = []
    for i, presentation in enumerate(presentations):
        print(f"Processing {i+1}/{len(presentations)}: {presentation['title']}")
        
        details = extract_presentation_details(presentation['url'])
        presentation.update(details)
        detailed_presentations.append(presentation)
        
        # Rate limiting
        time.sleep(0.1)  # 100ms delay
    
    # Step 5: Extract conference metadata
    conference_info = extract_conference_metadata(main_url)
    
    return {
        'conference': conference_info,
        'available_tracks': available_tracks,
        'presentations': detailed_presentations,
        'extraction_summary': {
            'total_presentations_found': len(presentations),
            'excluded_tracks': excluded_tracks,
            'success_rate': calculate_success_rate(detailed_presentations)
        }
    }
```

### Track Filtering Implementation

#### User Interface for Track Selection
```python
def get_user_track_preferences(available_tracks):
    """Interactive track selection for filtering"""
    print("\nAvailable tracks:")
    for i, track in enumerate(available_tracks):
        emoji_indicator = " 📱" if track['has_emoji'] else ""
        subtype_indicator = " 📁" if track.get('has_subtypes') else ""
        print(f"{i+1:2d}. {track['display_text']}{emoji_indicator}{subtype_indicator}")
    
    print("\nEnter track numbers to EXCLUDE (comma-separated), or press Enter for none:")
    user_input = input().strip()
    
    excluded_tracks = []
    if user_input:
        try:
            indices = [int(x.strip()) - 1 for x in user_input.split(',')]
            excluded_tracks = [available_tracks[i]['name'] for i in indices if 0 <= i < len(available_tracks)]
        except ValueError:
            print("Invalid input, proceeding without exclusions")
    
    return excluded_tracks
```

### Performance Considerations

#### Optimization Strategies
- **Track Pre-filtering**: Filter presentations by track before detailed extraction
- **Parallel Processing**: Process multiple presentations concurrently (with rate limiting)
- **Caching**: Cache track information to avoid repeated requests
- **Progress Tracking**: Show progress for large conferences (500+ presentations)

#### Estimated Processing Times
- **Track Discovery**: ~1-2 seconds
- **Presentation List**: ~2-3 seconds  
- **Individual Details**: ~0.5 seconds per presentation + 0.1s delay
- **Total for 542 presentations**: ~325 seconds (~5.4 minutes)

### Next Steps for Automation
1. Implement the complete extraction algorithm in Python
2. Add interactive track filtering interface
3. Add error handling and retry logic for failed requests
4. Create progress tracking with ETA for large datasets
5. Add validation for extracted data completeness
6. Test on multiple conference years for consistency
7. Add support for batch processing multiple conferences
8. Implement data export formats (JSON, CSV, database)