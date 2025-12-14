import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

async function analyzeContribFest() {
  try {
    const url = 'https://kccncna2025.sched.com/event/27Nko/contribfest-argo-configure-your-local-setup-and-contribute-alexandre-gaudreault-peter-jiang-codey-jenkins-intuit-nitish-kumar-akuity';
    console.log(`Analyzing ContribFest presentation: ${url}`);
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length} characters`);
    
    // Save HTML for analysis
    fs.writeFileSync('presentation-27Nko.html', response.data);
    console.log('Saved HTML to presentation-27Nko.html');
    
    const $ = cheerio.load(response.data);
    
    // Extract basic info
    console.log('\n--- Basic Information ---');
    const title = $('title').text();
    console.log(`Page title: ${title}`);
    
    const h1 = $('h1').text().trim();
    console.log(`H1: ${h1}`);
    
    // Look for the actual presentation title in the page content
    console.log('\n--- Presentation Title ---');
    const presentationTitle = $('.event-title, .sched-event-title, h2, h3').first().text().trim();
    console.log(`Presentation title: ${presentationTitle}`);
    
    // Look for speaker information
    console.log('\n--- Speaker Information ---');
    const speakerSelectors = ['.speaker', '.presenter', '[class*="speaker"]', '[class*="presenter"]', '.avatar'];
    speakerSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`Speaker elements with "${selector}" (${elements.length}):`);
        elements.each((i, el) => {
          const text = $(el).text().trim();
          if (text && text.length > 0) {
            console.log(`  ${i + 1}. ${text}`);
          }
        });
      }
    });
    
    // Look for track/type information (including sub-types)
    console.log('\n--- Track/Type Information ---');
    const trackLinks = $('.sched-event-type a[href*="type/"]');
    if (trackLinks.length > 0) {
      console.log(`Found ${trackLinks.length} track links`);
      
      let mainType = null;
      let subType = null;
      let mainTypeUrl = null;
      let subTypeUrl = null;
      
      trackLinks.each((i, el) => {
        const linkText = $(el).text().trim();
        const linkHref = $(el).attr('href');
        console.log(`  Link ${i + 1}: "${linkText}" -> ${linkHref}`);
        
        if (linkHref.includes('type/')) {
          const typePart = linkHref.split('type/')[1];
          const parts = typePart.split('/');
          
          if (parts.length === 1) {
            // Main type only
            mainType = decodeURIComponent(parts[0]).replace(/\+/g, ' ');
            mainTypeUrl = linkHref.startsWith('http') ? linkHref : 'https://kccncna2025.sched.com/' + linkHref;
          } else if (parts.length === 2) {
            // Sub-type (includes main type in URL)
            subType = decodeURIComponent(parts[1]).replace(/\+/g, ' ');
            subTypeUrl = linkHref.startsWith('http') ? linkHref : 'https://kccncna2025.sched.com/' + linkHref;
            // Also extract main type from sub-type URL if not already found
            if (!mainType) {
              mainType = decodeURIComponent(parts[0]).replace(/\+/g, ' ');
              mainTypeUrl = `https://kccncna2025.sched.com/type/${parts[0]}`;
            }
          }
        }
      });
      
      console.log(`Track: ${mainType}`);
      console.log(`Track URL: ${mainTypeUrl}`);
      if (subType) {
        console.log(`Sub-track: ${subType}`);
        console.log(`Sub-track URL: ${subTypeUrl}`);
      } else {
        console.log(`Sub-track: None`);
      }
      
    } else {
      console.log('No track information found');
    }
    
    // Look for experience level
    console.log('\n--- Experience Level ---');
    const experienceLink = $('.tip-custom-fields a[href*="/company/"]');
    if (experienceLink.length > 0) {
      const experienceLevel = experienceLink.text().trim();
      console.log(`Experience Level: ${experienceLevel}`);
    } else {
      console.log('No experience level found');
    }
    
    // Look for time/date info
    console.log('\n--- Date/Time Information ---');
    const timeElements = $('[class*="time"], [class*="date"]');
    timeElements.slice(0, 2).each((i, el) => {
      const text = $(el).text().trim();
      if (text && text.length > 0) {
        console.log(`  ${i + 1}. ${text}`);
      }
    });
    
    // Look for video links
    console.log('\n--- Video Links ---');
    const videoIframes = $('iframe[src*="youtube"]');
    if (videoIframes.length > 0) {
      videoIframes.each((i, el) => {
        console.log(`  YouTube video: ${$(el).attr('src')}`);
      });
    } else {
      console.log('No YouTube videos found');
    }
    
    // Look for presentation files
    console.log('\n--- Presentation Files ---');
    const pdfLinks = $('a[href*=".pdf"]');
    const pptLinks = $('a[href*=".ppt"]');
    
    if (pdfLinks.length > 0) {
      pdfLinks.each((i, el) => {
        console.log(`  PDF: ${$(el).attr('href')}`);
      });
    }
    
    if (pptLinks.length > 0) {
      pptLinks.each((i, el) => {
        console.log(`  PPT/PPTX: ${$(el).attr('href')}`);
      });
    }
    
    if (pdfLinks.length === 0 && pptLinks.length === 0) {
      console.log('No presentation files found');
    }
    
    // Look for special characters in title
    console.log('\n--- Special Character Analysis ---');
    const fullTitle = $('title').text();
    const hasSpecialChars = /[^\x00-\x7F]/.test(fullTitle);
    console.log(`Title contains special characters: ${hasSpecialChars}`);
    if (hasSpecialChars) {
      console.log(`Special characters found in: "${fullTitle}"`);
      // Find the specific special characters
      const specialChars = fullTitle.match(/[^\x00-\x7F]/g);
      if (specialChars) {
        console.log(`Special characters: ${[...new Set(specialChars)].join(', ')}`);
      }
    }
    
  } catch (error) {
    console.error('Analysis failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
    }
  }
}

analyzeContribFest();