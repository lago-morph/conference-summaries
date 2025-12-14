import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

async function analyzeSchedStructure() {
  try {
    console.log('Analyzing KubeCon 2025 North America Sched.com structure...');
    
    const mainUrl = 'https://kccncna2025.sched.com/list/';
    console.log(`\nFetching main schedule page: ${mainUrl}`);
    
    const response = await axios.get(mainUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length} characters`);
    
    // Save the HTML for detailed analysis
    fs.writeFileSync('sched-main-page.html', response.data);
    console.log('Saved main page HTML to sched-main-page.html');
    
    const $ = cheerio.load(response.data);
    
    // Analyze page structure
    console.log('\n=== PAGE STRUCTURE ANALYSIS ===');
    
    // Look for conference metadata
    console.log('\n--- Conference Metadata ---');
    const title = $('title').text();
    console.log(`Page title: ${title}`);
    
    const h1Elements = $('h1');
    console.log(`H1 elements (${h1Elements.length}):`);
    h1Elements.each((i, el) => {
      console.log(`  ${i + 1}. ${$(el).text().trim()}`);
    });
    
    // Look for presentation/session listings
    console.log('\n--- Presentation Listings ---');
    const sessionSelectors = [
      '.session',
      '.event',
      '.presentation',
      '[class*="session"]',
      '[class*="event"]',
      'a[href*="/event/"]',
      '.sched-event',
      '.event-item'
    ];
    
    sessionSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`\nElements with "${selector}" (${elements.length}):`);
        elements.slice(0, 5).each((i, el) => {
          const text = $(el).text().trim().substring(0, 100);
          const href = $(el).attr('href') || $(el).find('a').attr('href');
          console.log(`  ${i + 1}. ${text}${text.length >= 100 ? '...' : ''}`);
          if (href) console.log(`     Link: ${href}`);
        });
      }
    });
    
    // Look for links to individual presentations
    console.log('\n--- Individual Presentation Links ---');
    const presentationLinks = $('a[href*="/event/"]');
    console.log(`Found ${presentationLinks.length} presentation links`);
    
    const uniqueLinks = new Set();
    presentationLinks.each((i, el) => {
      const href = $(el).attr('href');
      if (href && !uniqueLinks.has(href)) {
        uniqueLinks.add(href);
        const text = $(el).text().trim();
        if (text && uniqueLinks.size <= 10) {
          console.log(`  ${uniqueLinks.size}. ${text.substring(0, 80)}${text.length > 80 ? '...' : ''}`);
          console.log(`     URL: ${href.startsWith('http') ? href : 'https://kccncna2025.sched.com' + href}`);
        }
      }
    });
    
    // Look for our specific test presentations
    console.log('\n--- Searching for Test Presentations ---');
    const testPresentations = [
      'simplifying advanced ai model serving on kubernetes using helm charts',
      'sponsored demo beyond the yaml architecting a composable secure and open source platform for the enterprise',
      'the myth of portability why your cloud native app is married to your provider'
    ];
    
    testPresentations.forEach((searchTerm, index) => {
      console.log(`\nSearching for: "${searchTerm}"`);
      const found = $('*').filter(function() {
        return $(this).text().toLowerCase().includes(searchTerm.toLowerCase());
      });
      
      if (found.length > 0) {
        console.log(`  Found ${found.length} matches`);
        found.slice(0, 3).each((i, el) => {
          const text = $(el).text().trim();
          const href = $(el).attr('href') || $(el).find('a').attr('href');
          console.log(`    Match ${i + 1}: ${text.substring(0, 100)}...`);
          if (href) console.log(`    Link: ${href}`);
        });
      } else {
        console.log(`  No matches found`);
      }
    });
    
    console.log('\n=== ANALYSIS COMPLETE ===');
    console.log('Check sched-main-page.html for detailed HTML structure');
    
  } catch (error) {
    console.error('Analysis failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
    }
  }
}

analyzeSchedStructure();