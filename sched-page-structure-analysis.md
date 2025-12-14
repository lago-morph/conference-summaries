# Sched.com Page Structure Analysis
## KubeCon + CloudNativeCon North America 2025

### Conference Information
- **Conference Name**: KubeCon + CloudNativeCon North America 2025
- **Sched.com Identifier**: `kccncna2025`
- **Main Schedule URL**: https://kccncna2025.sched.com/list/
- **Location**: Atlanta, GA, USA
- **Dates**: November 9-13, 2025 (from meta description)
- **Sponsor**: CNCF (Cloud Native Computing Foundation)

### Page Structure Analysis

#### Main Schedule Page (`/list/`)
- **Total Events Found**: 542 events
- **Page Title**: "KubeCon + CloudNativeCon North America 2025: Full Schedule"
- **HTML Structure**: Standard Sched.com layout with event listings

#### Individual Presentation Structure

Each presentation follows this HTML pattern:
```html
<span class="event ev_[NUMBER]">
  <a href="event/[EVENT_ID]/[URL_SLUG]" id="[UNIQUE_ID]" class="name">
    [PRESENTATION_TITLE] - [SPEAKER_NAME], [COMPANY] & [SPEAKER_NAME], [COMPANY]
  </a>
</span>
<div class="sched-event-details-container">
  <!-- Additional details -->
</div>
<h3>[TIME] <span class='tz'>EST</span></h3>
```

#### URL Pattern for Individual Presentations
- **Base URL**: `https://kccncna2025.sched.com/`
- **Individual Event URL**: `event/[EVENT_ID]/[URL_SLUG]`
- **Example**: `event/27FVb/simplifying-advanced-ai-model-serving-on-kubernetes-using-helm-charts-ajay-vohra-amazon-tianlu-caron-zhang-apple`

#### CSS Selectors for Data Extraction

**Conference Metadata:**
- Page title: `title` element
- Conference name: `h1` element
- Meta description contains location and dates

**Presentation Listings:**
- All presentations: `.event` class spans
- Presentation links: `a.name` within `.event` spans
- Presentation titles: Text content of `a.name` elements
- Event URLs: `href` attribute of `a.name` elements
- Event times: `h3` elements following event containers
- Timezone: `span.tz` within time elements

### Test Presentations Found

#### 1. "Simplifying Advanced AI Model Serving on Kubernetes Using Helm Charts"
- **Status**: ✅ Found
- **Event ID**: `27FVb`
- **URL**: `event/27FVb/simplifying-advanced-ai-model-serving-on-kubernetes-using-helm-charts-ajay-vohra-amazon-tianlu-caron-zhang-apple`
- **Full URL**: https://kccncna2025.sched.com/event/27FVb/simplifying-advanced-ai-model-serving-on-kubernetes-using-helm-charts-ajay-vohra-amazon-tianlu-caron-zhang-apple
- **Speakers**: Ajay Vohra (Amazon), Tianlu Caron Zhang (Apple)
- **Time**: 12:00pm EST
- **Expected Content**: YouTube video + presentation files (PPTX + PDF)

#### 2. "Sponsored Demo Beyond the YAML..."
- **Status**: ❌ Not Found
- **Note**: This presentation may not exist in the current schedule, or the title may be different

#### 3. "The Myth of Portability: Why Your Cloud Native App Is Married To Your Provider"
- **Status**: ✅ Found
- **Event ID**: `27FVz`
- **URL**: `event/27FVz/the-myth-of-portability-why-your-cloud-native-app-is-married-to-your-provider-corey-quinn-the-duckbill-group`
- **Full URL**: https://kccncna2025.sched.com/event/27FVz/the-myth-of-portability-why-your-cloud-native-app-is-married-to-your-provider-corey-quinn-the-duckbill-group
- **Speaker**: Corey Quinn (The Duckbill Group)
- **Time**: 2:30pm EST
- **Expected Content**: YouTube video only (no presentation files)

### Data Extraction Strategy

#### Phase 2: Conference Page Analysis ✅ COMPLETED
- Main schedule page structure documented
- CSS selectors identified
- URL patterns established
- Test presentations located (2 of 3 found)

#### Phase 3: Individual Presentation Page Analysis (NEXT)
For each presentation URL, extract:
- Video links (YouTube, other platforms)
- Presentation file links (PDF, PPTX, etc.)
- Speaker information
- Session details
- Date/time information

#### Automation Approach
1. **Main Page Scraping**: Use `.event a.name` selector to get all presentation links
2. **Individual Page Scraping**: Visit each presentation URL to extract video/file links
3. **Data Structure**: Store in YAML format as specified

### Rate Limiting Considerations
- Implement 100ms delays between requests
- Total presentations: 542 events
- Estimated scraping time: ~54 seconds for all presentations
- Consider batching and progress tracking for large datasets