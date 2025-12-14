# CSS Selectors Reference

This document provides a comprehensive reference of all CSS selectors discovered during the exploration phase for extracting data from Sched.com conference websites.

## Conference Metadata Selectors

### Conference Name
```css
h1                              /* Primary conference name */
title                           /* Page title (fallback) */
.conference-title               /* Alternative selector */
```

### Conference Description and Metadata
```css
meta[name="description"]        /* Primary metadata source */
meta[name="twitter:description"] /* Alternative metadata */
meta[property="og:description"] /* Open Graph description */
```

## Track/Type Discovery Selectors

### Track Filter Links
```css
a[href*="/overview/type/"]      /* Primary track filter links */
a[href*="type/"]               /* General type links */
.filter a                      /* Filter container links */
.type-filter a                 /* Type-specific filter links */
[class*="filter"] a            /* Any element with "filter" in class */
[class*="type"] a              /* Any element with "type" in class */
```

### Track Validation
```css
.sched-container               /* Validates Sched.com page */
.event-list                    /* Validates event listing page */
```

## Presentation List Selectors

### Event Containers
```css
.event                         /* Primary event container */
.event-item                    /* Alternative event container */
[class*="event"]               /* Any element with "event" in class */
```

### Presentation Links and Titles
```css
.event a.name                  /* Primary presentation link */
.event a.name[href]            /* Presentation URL */
.event-title                   /* Alternative title selector */
.session-title                 /* Session title selector */
```

### Time and Date Information
```css
h3                             /* Time section headers */
h3 span.tz                     /* Timezone information */
.time-slot                     /* Time slot containers */
[class*="time"]                /* Any element with "time" in class */
```

## Individual Presentation Page Selectors

### Basic Information
```css
h1                             /* Presentation title (primary) */
.event-title                   /* Event title (alternative) */
title                          /* Page title (fallback) */
```

### Speaker Information
```css
.speaker                       /* Primary speaker container */
.presenter                     /* Alternative presenter container */
[class*="speaker"]             /* Any element with "speaker" in class */
.speaker-name                  /* Speaker name specifically */
.speaker-company               /* Speaker company */
.speaker a[href]               /* Speaker profile links */
```

### Session Details
```css
[class*="time"]                /* Date and time information */
[class*="date"]                /* Date-specific information */
.session-time                  /* Session timing */
.session-date                  /* Session date */
[class*="location"]            /* Location information */
.session-location              /* Session location */
.venue                         /* Venue information */
```

### Track and Category Information
```css
.sched-event-type a[href*="type/"] /* Primary track links */
[class*="track"] a[href*="type/"]  /* Track container links */
.event-type                    /* Event type container */
.category                      /* Category information */
.tag                          /* Tag information */
```

### Experience Level
```css
.tip-custom-fields a[href*="/company/"] /* Experience level links */
[class*="level"]               /* Level indicators */
.difficulty                    /* Difficulty indicators */
.audience                      /* Target audience */
```

## Media and File Selectors

### Video Links
```css
iframe[src*="youtube"]         /* YouTube embedded videos */
iframe[src*="youtu.be"]        /* YouTube short URLs */
iframe[src*="vimeo"]           /* Vimeo embedded videos */
a[href*="youtube"]             /* YouTube direct links */
a[href*="youtu.be"]            /* YouTube short direct links */
a[href*="vimeo"]               /* Vimeo direct links */
.video-container               /* Video container elements */
[class*="video"]               /* Any video-related elements */
```

### Presentation Files
```css
a[href*=".pdf"]                /* PDF file links */
a[href*=".pptx"]               /* PowerPoint file links */
a[href*=".ppt"]                /* Legacy PowerPoint files */
a[href*=".doc"]                /* Word document files */
a[href*=".docx"]               /* Modern Word documents */
[class*="file"]                /* File container elements */
.download                      /* Download links */
.attachment                    /* Attachment links */
```

## Validation and Structure Selectors

### Page Structure Validation
```css
.sched-container               /* Main Sched.com container */
.event-list                    /* Event listing container */
.schedule                      /* Schedule container */
[class*="sched"]               /* Any Sched-related elements */
```

### Content Validation
```css
.event                         /* Presence of events */
.session                       /* Presence of sessions */
.presentation                  /* Presence of presentations */
```

## Special Cases and Edge Cases

### Emoji and Special Characters
- No special selectors needed - handle in text processing
- Use Unicode regex for emoji detection: `/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u`

### Sub-track Hierarchies
```css
.sched-event-type a[href*="type/"] /* Main track links */
/* Sub-tracks identified by URL pattern: type/MainTrack/SubTrack */
```

### Missing Data Scenarios
```css
.no-video                      /* Indicates no video available */
.no-files                      /* Indicates no files available */
.tbd                          /* To be determined content */
.cancelled                     /* Cancelled sessions */
```

## Selector Priority and Fallbacks

### Title Extraction Priority
1. `h1` (primary)
2. `.event-title` (secondary)
3. `title` split on ' - ' (fallback)

### Speaker Extraction Priority
1. `.speaker` (primary)
2. `.presenter` (secondary)
3. `[class*="speaker"]` (fallback)

### Time Extraction Priority
1. `[class*="time"]` (primary)
2. `.session-time` (secondary)
3. `h3` containing date patterns (fallback)

### Track Extraction Priority
1. `.sched-event-type a[href*="type/"]` (primary)
2. `[class*="track"] a[href*="type/"]` (secondary)
3. `.event-type` (fallback)

## Implementation Notes

### Selector Robustness
- Always use multiple selectors as fallbacks
- Check for element existence before accessing attributes
- Handle both absolute and relative URLs
- Normalize text content (trim whitespace)

### Performance Considerations
- Use specific selectors when possible to reduce DOM traversal
- Cache jQuery objects for repeated use
- Limit selector scope to relevant containers

### Error Handling
- Gracefully handle missing elements
- Provide meaningful fallbacks for missing data
- Log selector failures for debugging

### Cross-Conference Compatibility
These selectors were validated on KubeCon + CloudNativeCon North America 2025. They should work for other Sched.com conferences, but may need adjustment for:
- Different conference organizers
- Custom Sched.com themes
- Older or newer Sched.com versions

## Testing and Validation

### Selector Testing
```javascript
// Test selector existence
const elements = $(selector);
console.log(`Selector "${selector}" found ${elements.length} elements`);

// Test selector content
elements.each((i, el) => {
  console.log(`Element ${i}: ${$(el).text().trim()}`);
});
```

### Content Validation
```javascript
// Validate extracted data
const isValidTitle = title && title.length > 5;
const isValidUrl = url && url.startsWith('http');
const isValidDate = date && /\d{4}/.test(date);
```

This selector reference provides the foundation for reliable data extraction from Sched.com conference websites.