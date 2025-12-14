#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import * as cheerio from 'cheerio';

interface SearchResult {
  title: string;
  url: string;
  description: string;
}

const isValidSearchArgs = (args: any): args is { query: string; limit?: number } =>
  typeof args === 'object' &&
  args !== null &&
  typeof args.query === 'string' &&
  (args.limit === undefined || typeof args.limit === 'number');

class WebSearchServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'web-search',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'search',
          description: 'Search the web using Google (no API key required)',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query',
              },
              limit: {
                type: 'number',
                description: 'Maximum number of results to return (default: 5)',
                minimum: 1,
                maximum: 10,
              },
            },
            required: ['query'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name !== 'search') {
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${request.params.name}`
        );
      }

      if (!isValidSearchArgs(request.params.arguments)) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'Invalid search arguments'
        );
      }

      const query = request.params.arguments.query;
      const limit = Math.min(request.params.arguments.limit || 5, 10);

      try {
        const results = await this.performSearch(query, limit);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      } catch (error) {
        if (axios.isAxiosError(error)) {
          return {
            content: [
              {
                type: 'text',
                text: `Search error: ${error.message}`,
              },
            ],
            isError: true,
          };
        }
        throw error;
      }
    });
  }

  private async performSearch(query: string, limit: number): Promise<SearchResult[]> {
    // Try multiple approaches to get search results
    const approaches = [
      () => this.searchWithDuckDuckGo(query, limit),
      () => this.searchWithBing(query, limit),
      () => this.searchWithGoogleAlternative(query, limit)
    ];

    for (const approach of approaches) {
      try {
        const results = await approach();
        if (results.length > 0) {
          return results;
        }
      } catch (error) {
        console.error('Search approach failed:', error.message);
        continue;
      }
    }

    // If all approaches fail, return empty results
    return [];
  }

  private async searchWithDuckDuckGo(query: string, limit: number): Promise<SearchResult[]> {
    // DuckDuckGo HTML search (more reliable than Google)
    const response = await axios.get('https://html.duckduckgo.com/html/', {
      params: { q: query },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    const $ = cheerio.load(response.data);
    const results: SearchResult[] = [];

    $('.result').each((i, element) => {
      if (i >= limit) return false;

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

    return results;
  }

  private async searchWithBing(query: string, limit: number): Promise<SearchResult[]> {
    const response = await axios.get('https://www.bing.com/search', {
      params: { q: query },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    const $ = cheerio.load(response.data);
    const results: SearchResult[] = [];

    $('.b_algo').each((i, element) => {
      if (i >= limit) return false;

      const titleElement = $(element).find('h2 a');
      const snippetElement = $(element).find('.b_caption p');
      
      if (titleElement.length) {
        const title = titleElement.text().trim();
        const url = titleElement.attr('href');
        const description = snippetElement.text().trim();
        
        if (url && title) {
          results.push({
            title,
            url,
            description: description || '',
          });
        }
      }
    });

    return results;
  }

  private async searchWithGoogleAlternative(query: string, limit: number): Promise<SearchResult[]> {
    // Try a different approach with Google - using different parameters
    const response = await axios.get('https://www.google.com/search', {
      params: { 
        q: query,
        num: limit,
        hl: 'en'
      },
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      },
      timeout: 10000
    });

    const $ = cheerio.load(response.data);
    const results: SearchResult[] = [];

    // Try multiple selectors for Google results
    const selectors = ['.g', '.tF2Cxc', '.rc'];
    
    for (const selector of selectors) {
      $(selector).each((i, element) => {
        if (i >= limit) return false;

        const titleElement = $(element).find('h3');
        const linkElement = $(element).find('a[href^="http"]').first();
        const snippetElement = $(element).find('.VwiC3b, .s, .st');

        if (titleElement.length && linkElement.length) {
          const title = titleElement.text().trim();
          const url = linkElement.attr('href');
          const description = snippetElement.text().trim();
          
          if (url && title && !results.find(r => r.url === url)) {
            results.push({
              title,
              url,
              description: description || '',
            });
          }
        }
      });
      
      if (results.length > 0) break;
    }

    return results;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Web Search MCP server running on stdio');
  }
}

const server = new WebSearchServer();
server.run().catch(console.error);