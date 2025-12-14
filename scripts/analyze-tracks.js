import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

async function analyzeTracks() {
  try {
    const url = 'https://kccncna2025.sched.com/list/';
    console.log(`Analyzing main conference page for tracks: ${url}`);
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length} characters`);
    
    const $ = cheerio.load(response.data);
    
    // Look for track/type filters
    console.log('\n--- Looking for Track Filters ---');
    
    // Common selectors for filters
    const filterSelectors = [
      'a[href*="/overview/type/"]',
      'a[href*="type/"]',
      '.filter a',
      '.type-filter a',
      '[class*="filter"] a',
      '[class*="type"] a'
    ];
    
    const tracks = new Set();
    const trackData = [];
    
    filterSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`\nFound ${elements.length} elements with selector "${selector}"`);
        elements.each((i, el) => {
          const href = $(el).attr('href');
          const text = $(el).text().trim();
          
          if (href && href.includes('type/') && text && text.length > 0) {
            console.log(`  ${i + 1}. "${text}" -> ${href}`);
            
            // Extract track name from URL
            let trackName = null;
            let trackUrl = null;
            
            if (href.includes('/overview/type/')) {
              const typePart = href.split('/overview/type/')[1];
              trackName = decodeURIComponent(typePart).replace(/\+/g, ' ');
              trackUrl = href.startsWith('http') ? href : 'https://kccncna2025.sched.com' + href;
            } else if (href.includes('type/')) {
              const typePart = href.split('type/')[1];
              // Handle sub-types
              const parts = typePart.split('/');
              trackName = decodeURIComponent(parts[0]).replace(/\+/g, ' ');
              trackUrl = href.startsWith('http') ? href : 'https://kccncna2025.sched.com/' + href;
            }
            
            if (trackName && !tracks.has(trackName)) {
              tracks.add(trackName);
              trackData.push({
                name: trackName,
                display_text: text,
                url: trackUrl,
                overview_url: `https://kccncna2025.sched.com/overview/type/${encodeURIComponent(trackName).replace(/ /g, '+')}`
              });
            }
          }
        });
      }
    });
    
    // Also look for any dropdown or select options
    console.log('\n--- Looking for Dropdown/Select Options ---');
    const selectOptions = $('select option, .dropdown option, [class*="select"] option');
    if (selectOptions.length > 0) {
      console.log(`Found ${selectOptions.length} select options`);
      selectOptions.each((i, el) => {
        const value = $(el).attr('value');
        const text = $(el).text().trim();
        if (value && text && (value.includes('type') || text.toLowerCase().includes('track'))) {
          console.log(`  Option ${i + 1}: "${text}" -> ${value}`);
        }
      });
    }
    
    // Look for filter buttons or links
    console.log('\n--- Looking for Filter Buttons/Links ---');
    const filterButtons = $('button, .btn, .filter-btn, [class*="filter"]');
    filterButtons.each((i, el) => {
      const text = $(el).text().trim();
      const onclick = $(el).attr('onclick');
      const dataFilter = $(el).attr('data-filter');
      
      if (text && (text.toLowerCase().includes('type') || text.toLowerCase().includes('track') || text.toLowerCase().includes('filter'))) {
        console.log(`  Button ${i + 1}: "${text}"`);
        if (onclick) console.log(`    onclick: ${onclick}`);
        if (dataFilter) console.log(`    data-filter: ${dataFilter}`);
      }
    });
    
    // Sort tracks alphabetically
    trackData.sort((a, b) => a.name.localeCompare(b.name));
    
    console.log('\n--- Final Track List ---');
    console.log(`Found ${trackData.length} unique tracks:`);
    trackData.forEach((track, i) => {
      console.log(`${i + 1}. ${track.name}`);
      console.log(`   Display: "${track.display_text}"`);
      console.log(`   URL: ${track.url}`);
      console.log(`   Overview: ${track.overview_url}`);
      console.log('');
    });
    
    // Save track data to JSON for easy processing
    fs.writeFileSync('tracks-data.json', JSON.stringify(trackData, null, 2));
    console.log('Saved track data to tracks-data.json');
    
    return trackData;
    
  } catch (error) {
    console.error('Analysis failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
    }
    return [];
  }
}

analyzeTracks();