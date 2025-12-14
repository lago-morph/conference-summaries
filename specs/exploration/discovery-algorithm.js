/**
 * Conference Discovery Algorithm
 * 
 * This module demonstrates how to find the Sched.com URL for a given conference
 * using web search and pattern matching.
 * 
 * Phase 1 of the extraction workflow.
 */

import axios from 'axios';

/**
 * Find the Sched.com URL for a conference using web search
 * 
 * @param {string} conferenceName - Name of the conference (e.g., "KubeCon 2025 North America")
 * @param {Function} webSearchFunction - Web search function (from MCP server)
 * @returns {Promise<Object>} Conference discovery results
 */
async function discoverConference(conferenceName, webSearchFunction) {
  console.log(`🔍 Discovering Sched.com URL for: ${conferenceName}`);
  
  // Step 1: Construct search query
  const searchQuery = `"${conferenceName}" sched.com`;
  console.log(`   Search query: ${searchQuery}`);
  
  try {
    // Step 2: Perform web search
    const searchResults = await webSearchFunction(searchQuery);
    console.log(`   Found ${searchResults.length} search results`);
    
    // Step 3: Find Sched.com URLs in results
    const schedUrls = [];
    
    for (const result of searchResults) {
      const url = result.url;
      
      // Look for Sched.com URLs with the pattern: https://[identifier].sched.com
      if (url.includes('sched.com') && url.match(/https:\/\/[^.]+\.sched\.com/)) {
        schedUrls.push({
          url: url,
          title: result.title,
          description: result.description
        });
      }
    }
    
    console.log(`   Found ${schedUrls.length} Sched.com URLs`);
    
    if (schedUrls.length === 0) {
      throw new Error(`No Sched.com URLs found for "${conferenceName}"`);
    }
    
    // Step 4: Extract the best candidate
    // Prefer URLs that end with /list/ or are root domain
    let bestCandidate = schedUrls[0];
    
    for (const candidate of schedUrls) {
      if (candidate.url.includes('/list/') || candidate.url.match(/https:\/\/[^.]+\.sched\.com\/?$/)) {
        bestCandidate = candidate;
        break;
      }
    }
    
    // Step 5: Extract identifier and construct main URL
    const urlMatch = bestCandidate.url.match(/https:\/\/([^.]+)\.sched\.com/);
    if (!urlMatch) {
      throw new Error(`Could not extract identifier from URL: ${bestCandidate.url}`);
    }
    
    const identifier = urlMatch[1];
    const mainUrl = `https://${identifier}.sched.com/list/`;
    
    console.log(`   ✅ Conference identifier: ${identifier}`);
    console.log(`   ✅ Main URL: ${mainUrl}`);
    
    // Step 6: Validate the URL is accessible
    try {
      const response = await axios.head(mainUrl, { timeout: 10000 });
      console.log(`   ✅ URL validation: ${response.status} ${response.statusText}`);
    } catch (error) {
      console.warn(`   ⚠️  URL validation failed: ${error.message}`);
      // Continue anyway - the URL might still work for GET requests
    }
    
    // Step 7: Return discovery results
    return {
      success: true,
      conference: {
        sched_identifier: identifier,
        main_url: mainUrl,
        search_query: searchQuery,
        discovered_from: bestCandidate.url,
        discovery_date: new Date().toISOString().split('T')[0]
      },
      all_candidates: schedUrls
    };
    
  } catch (error) {
    console.error(`❌ Conference discovery failed: ${error.message}`);
    return {
      success: false,
      error: error.message,
      conference: null,
      all_candidates: []
    };
  }
}

/**
 * Validate that a discovered conference URL is working
 * 
 * @param {string} mainUrl - The main conference URL to validate
 * @returns {Promise<Object>} Validation results
 */
async function validateConferenceUrl(mainUrl) {
  console.log(`🔍 Validating conference URL: ${mainUrl}`);
  
  try {
    const response = await axios.get(mainUrl, {
      timeout: 15000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    const html = response.data;
    
    // Check for expected Sched.com page elements
    const hasSchedElements = html.includes('sched-container') || 
                            html.includes('event-list') || 
                            html.includes('sched.com');
    
    const hasEvents = html.includes('class="event"') || 
                     html.includes('event-item');
    
    console.log(`   ✅ Response status: ${response.status}`);
    console.log(`   ✅ Has Sched elements: ${hasSchedElements}`);
    console.log(`   ✅ Has events: ${hasEvents}`);
    
    return {
      valid: true,
      status: response.status,
      hasSchedElements,
      hasEvents,
      contentLength: html.length
    };
    
  } catch (error) {
    console.error(`   ❌ Validation failed: ${error.message}`);
    return {
      valid: false,
      error: error.message
    };
  }
}

/**
 * Example usage of the discovery algorithm
 */
async function exampleUsage() {
  // Mock web search function for demonstration
  const mockWebSearch = async (query) => {
    // In real implementation, this would call the MCP web search server
    return [
      {
        url: "https://kccncna2025.sched.com/list/",
        title: "KubeCon + CloudNativeCon North America 2025",
        description: "Conference schedule for KubeCon 2025 in Atlanta"
      },
      {
        url: "https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/",
        title: "KubeCon + CloudNativeCon North America 2025",
        description: "Official conference website"
      }
    ];
  };
  
  // Discover conference
  const result = await discoverConference("KubeCon 2025 North America", mockWebSearch);
  
  if (result.success) {
    console.log("Discovery successful!");
    console.log("Conference data:", result.conference);
    
    // Validate the discovered URL
    const validation = await validateConferenceUrl(result.conference.main_url);
    console.log("Validation result:", validation);
  } else {
    console.log("Discovery failed:", result.error);
  }
}

// Export functions for use in other modules
export {
  discoverConference,
  validateConferenceUrl,
  exampleUsage
};

/**
 * Key Implementation Notes:
 * 
 * 1. SEARCH STRATEGY
 *    - Use exact conference name in quotes for precision
 *    - Include "sched.com" to filter results
 *    - Handle multiple search engines (DuckDuckGo, Bing, Google)
 * 
 * 2. URL PATTERN MATCHING
 *    - Look for https://[identifier].sched.com pattern
 *    - Prefer URLs ending with /list/ (main schedule page)
 *    - Extract identifier for constructing other URLs
 * 
 * 3. VALIDATION
 *    - Test URL accessibility with HEAD request first
 *    - Verify page contains expected Sched.com elements
 *    - Check for presence of event listings
 * 
 * 4. ERROR HANDLING
 *    - Graceful failure with detailed error messages
 *    - Return all candidates for manual review if needed
 *    - Continue processing even if validation fails
 * 
 * 5. RATE LIMITING
 *    - Built into web search MCP server
 *    - Add delays between validation requests if needed
 * 
 * This algorithm has been tested successfully with:
 * - KubeCon + CloudNativeCon North America 2025
 * - Returns: kccncna2025.sched.com identifier
 * - Main URL: https://kccncna2025.sched.com/list/
 */