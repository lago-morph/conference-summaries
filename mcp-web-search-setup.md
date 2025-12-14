# Web Search MCP Server Setup Guide

This guide explains how to install and configure the web search MCP server for Kiro, enabling free web searching capabilities without API keys.

## Prerequisites

- Node.js installed on your system
- Git installed
- Kiro IDE with MCP support

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/pskill9/web-search.git
```

### 2. Install Dependencies and Build

```bash
cd web-search
npm install
```

**Note**: The build process happens automatically during `npm install` via the prepare script. This will:
- Run TypeScript compilation (`tsc`)
- Make the build/index.js file executable
- Create the `build/` directory with the compiled server

### 3. Verify Build

Check that the build was successful:
```bash
ls build/
# Should show: index.js
```

### 4. Configure MCP in Kiro

Create the MCP configuration file at `.kiro/settings/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "web-search": {
      "command": "node",
      "args": ["/full/path/to/web-search/build/index.js"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Important**: Replace `/full/path/to/web-search/build/index.js` with the actual absolute path to your built server.

#### Example for Windows:
```json
{
  "mcpServers": {
    "web-search": {
      "command": "node",
      "args": ["C:\\Users\\YourName\\Documents\\project\\web-search\\build\\index.js"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### Example for macOS/Linux:
```json
{
  "mcpServers": {
    "web-search": {
      "command": "node",
      "args": ["/Users/yourname/project/web-search/build/index.js"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 5. Restart Kiro

After creating the MCP configuration:
1. **Restart Kiro completely** to load the new MCP server
2. Alternatively, you can reconnect MCP servers from the MCP Server view in the Kiro feature panel

### 6. Verify Installation

Once Kiro restarts, the AI assistant should have access to web search capabilities. You can verify by asking it to search for something.

## Usage

The web search server provides a `search` tool with these parameters:

- `query` (required): The search query string
- `limit` (optional): Number of results to return (default: 5, max: 10)

## Troubleshooting

### Common Issues

1. **Server not connecting**: 
   - Verify the path in `mcp.json` is correct and absolute
   - Check that `build/index.js` exists and is executable
   - Restart Kiro completely

2. **Build failures**:
   - Ensure Node.js is installed and up to date
   - Try running `npm run build` manually
   - Check for any error messages during `npm install`

3. **Permission issues** (macOS/Linux):
   - The build process should make the file executable automatically
   - If needed, run: `chmod +x build/index.js`

### Rate Limiting

The server uses Google search scraping, so be mindful of:
- Keep searches to reasonable frequency
- Use appropriate `limit` values
- Consider delays between searches for heavy usage

## Repository Information

- **Source**: https://github.com/pskill9/web-search
- **License**: Check repository for current license
- **Features**: Free web search, no API keys required, structured JSON results

## Alternative Setup Locations

If you need to set this up in different locations:

1. **User-level MCP config**: `~/.kiro/settings/mcp.json` (affects all workspaces)
2. **Workspace-level MCP config**: `.kiro/settings/mcp.json` (workspace-specific)

The workspace-level config takes precedence over user-level config.