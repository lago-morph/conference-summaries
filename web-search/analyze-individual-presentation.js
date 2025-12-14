import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

async function analyzeIndividualPresentation(eventUrl, presentationName) {
  try {
    console.log(`\n=== Analyzing: ${presentationName} ===`);
    console.log(`URL: ${eventUrl}`);
    
    const response = await axios.get(eventUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length} characters`);
    
    // Save HTML for analysis
    const filename = `presentation-${eventUrl.split('/')[4]}.html`;
    fs.writeFileSync(filename, response.data);
    console.log(`Saved HTML to ${filename}`);
    
    const $ = cheerio.load(response.data);
    
    // Extract basic presentation info
    console.log('\n--- Basic Information ---');
    const title = $('title').text();
    console.log(`Page title: ${title}`);
    
    const h1 = $('h1').text().trim();
    console.log(`H1: ${h1}`);
    
    // Look for speaker information
    console.log('\n--- Speaker Information ---');
    const speakerSelectors = ['.speaker', '.presenter', '[class*="speaker"]', '[class*="presenter"]'];
    speakerSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`Speaker elements with "${selector}" (${elements.length}):`);
        elements.each((i, el) => {
          console.log(`  ${i + 1}. ${$(el).text().trim()}`);
        });
      }
    });
    
    // Look for video links
    console.log('\n--- Video Links ---');
    const videoSelectors = [
      'a[href*="youtube"]',
      'a[href*="youtu.be"]',
      'a[href*="vimeo"]',
      'a[href*="video"]',
      'iframe[src*="youtube"]',
      'iframe[src*="vimeo"]',
      '[class*="video"]'
    ];
    
    videoSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`Video elements with "${selector}" (${elements.length}):`);
        elements.each((i, el) => {
          const href = $(el).attr('href') || $(el).attr('src');
          const text = $(el).text().trim();
          console.log(`  ${i + 1}. ${text || '[No text]'}`);
          if (href) console.log(`     Link: ${href}`);
        });
      }
    });
    
    // Look for presentation file links
    console.log('\n--- Presentation Files ---');
    const fileSelectors = [
      'a[href*=".pdf"]',
      'a[href*=".ppt"]',
      'a[href*=".pptx"]',
      'a[href*=".doc"]',
      'a[href*=".docx"]',
      'a[href*="slides"]',
      'a[href*="presentation"]',
      '[class*="download"]',
      '[class*="file"]',
      '[class*="attachment"]'
    ];
    
    fileSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`File elements with "${selector}" (${elements.length}):`);
        elements.each((i, el) => {
          const href = $(el).attr('href');
          const text = $(el).text().trim();
          console.log(`  ${i + 1}. ${text || '[No text]'}`);
          if (href) console.log(`     Link: ${href}`);
        });
      }
    });
    
    // Look for date/time information
    console.log('\n--- Date/Time Information ---');
    const timeSelectors = ['.time', '.date', '.schedule', '[class*="time"]', '[class*="date"]'];
    timeSelectors.forEach(selector => {
      const elements = $(selector);
      if (elements.length > 0) {
        console.log(`Time elements with "${selector}" (${elements.length}):`);
        elements.slice(0, 3).each((i, el) => {
          console.log(`  ${i + 1}. ${$(el).text().trim()}`);
        });
      }
    });
    
    // Look for track/type information
    console.log('\n--- Track/Type Information ---');
    const trackLink = $('.sched-event-type a[href*="type/"]');
    if (trackLink.length > 0) {
      const track = trackLink.text().trim();
      const trackUrl = trackLink.attr('href');
      console.log(`Track: ${track}`);
      console.log(`Track URL: ${trackUrl.startsWith('http') ? trackUrl : 'https://kccncna2025.sched.com/' + trackUrl}`);
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
    
    // Look for all links to understand what's available
    console.log('\n--- All Links Analysis ---');
    const allLinks = $('a[href]');
    const linkTypes = {
      youtube: [],
      files: [],
      external: [],
      internal: []
    };
    
    allLinks.each((i, el) => {
      const href = $(el).attr('href');
      const text = $(el).text().trim();
      
      if (href.includes('youtube') || href.includes('youtu.be')) {
        linkTypes.youtube.push({ text, href });
      } else if (href.match(/\.(pdf|ppt|pptx|doc|docx)$/i)) {
        linkTypes.files.push({ text, href });
      } else if (href.startsWith('http') && !href.includes('sched.com')) {
        linkTypes.external.push({ text, href });
      } else {
        linkTypes.internal.push({ text, href });
      }
    });
    
    console.log(`YouTube links: ${linkTypes.youtube.length}`);
    linkTypes.youtube.forEach((link, i) => {
      console.log(`  ${i + 1}. ${link.text} -> ${link.href}`);
    });
    
    console.log(`File links: ${linkTypes.files.length}`);
    linkTypes.files.forEach((link, i) => {
      console.log(`  ${i + 1}. ${link.text} -> ${link.href}`);
    });
    
    console.log(`External links: ${linkTypes.external.length}`);
    linkTypes.external.slice(0, 5).forEach((link, i) => {
      console.log(`  ${i + 1}. ${link.text} -> ${link.href}`);
    });
    
    return {
      title,
      speakers: [], // Will be populated based on findings
      videoLinks: linkTypes.youtube,
      fileLinks: linkTypes.files,
      externalLinks: linkTypes.external
    };
    
  } catch (error) {
    console.error(`Analysis failed for ${presentationName}:`, error.message);
    return null;
  }
}

async function analyzeTestPresentations() {
  const presentations = [
    {
      name: "Simplifying Advanced AI Model Serving on Kubernetes Using Helm Charts",
      url: "https://kccncna2025.sched.com/event/27FVb/simplifying-advanced-ai-model-serving-on-kubernetes-using-helm-charts-ajay-vohra-amazon-tianlu-caron-zhang-apple",
      expectedContent: "YouTube video + presentation files (PPTX + PDF)"
    },
    {
      name: "The Myth of Portability: Why Your Cloud Native App Is Married To Your Provider",
      url: "https://kccncna2025.sched.com/event/27FVz/the-myth-of-portability-why-your-cloud-native-app-is-married-to-your-provider-corey-quinn-the-duckbill-group",
      expectedContent: "YouTube video only (no presentation files)"
    }
  ];
  
  for (const presentation of presentations) {
    await analyzeIndividualPresentation(presentation.url, presentation.name);
    console.log(`\nExpected content: ${presentation.expectedContent}`);
    console.log('\n' + '='.repeat(80));
    
    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }
}

analyzeTestPresentations();