import axios from 'axios';
import * as cheerio from 'cheerio';

async function testDuckDuckGo(query) {
  try {
    console.log(`Testing DuckDuckGo search for: "${query}"`);
    
    const response = await axios.get('https://html.duckduckgo.com/html/', {
      params: { q: query },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length}`);
    
    const $ = cheerio.load(response.data);
    const results = [];

    $('.result').each((i, element) => {
      if (i >= 3) return false; // Limit to 3 results for testing

      const titleElement = $(element).find('.result__title a');
      const snippetElement = $(element).find('.result__snippet');
      
      if (titleElement.length) {
        const title = titleElement.text().trim();
        const url = titleElement.attr('href');
        const description = snippetElement.text().trim();
        
        if (url && title) {
          results.push({
            title,
            url: url.startsWith('//') ? 'https:' + url : url,
            description: description || '',
          });
        }
      }
    });

    console.log(`Found ${results.length} results:`);
    results.forEach((result, i) => {
      console.log(`${i + 1}. ${result.title}`);
      console.log(`   URL: ${result.url}`);
      console.log(`   Description: ${result.description.substring(0, 100)}...`);
      console.log('');
    });

    return results;
  } catch (error) {
    console.error('DuckDuckGo search failed:', error.message);
    return [];
  }
}

// Test with our target search
testDuckDuckGo('KubeCon 2025 North America sched.com').then(() => {
  console.log('Test completed');
});