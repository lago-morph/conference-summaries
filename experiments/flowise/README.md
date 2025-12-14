# Flowise Setup

This directory contains a Flowise installation for building and experimenting with LLM applications and AI workflows using a drag-and-drop interface.

## Installation

Flowise is installed via npm in this directory. The installation is managed automatically by the startup script.

**Version:** Latest (automatically installed on first run)

### Fresh Clone Setup

If this is a fresh git clone, don't worry! The `run-flowise.sh` script will automatically:
- Check if dependencies are installed
- Install Flowise and all dependencies if needed
- Start the server bound to your network IP

Simply run:
```bash
./run-flowise.sh
```

The script handles everything, including fresh installations from a clean git clone.

## Quick Start

### Using the Convenience Script (Recommended)

The easiest way to start Flowise:

```bash
./run-flowise.sh
```

This script will:
1. Check if this is a fresh clone and install dependencies if needed
2. Use `../scripts/get-eth0-ip.sh` to get your network IP
3. Start Flowise bound to that IP address
4. Display the URL to access in your browser

**Example output:**
```
Flowise Startup Script
======================

✅ Dependencies found - skipping installation

Getting network IP address...
Network IP: 172.30.196.118

Starting Flowise...
Access the web UI at: http://172.30.196.118:3000

Press Ctrl+C to stop Flowise
```

### Manual Start

**For network access (required for browser access from host machine):**

⚠️ **IMPORTANT:** When exposing web interfaces intended for browser access, always use the `get-eth0-ip.sh` script to get the correct IP address to bind to. This is especially important in WSL or VM environments.

```bash
# Get the network IP address
HOST_IP=$(../scripts/get-eth0-ip.sh)

# Start Flowise bound to the network IP
npx flowise start --FLOWISE_HOST=$HOST_IP --PORT=3000
```

**For local access only (localhost):**
```bash
npx flowise start
```

### Access the Web UI

Open your browser and navigate to the URL displayed in the terminal (e.g., `http://172.30.196.118:3000`).

## Common Usage Patterns

### Custom Port

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
npx flowise start --FLOWISE_HOST=$HOST_IP --PORT=8080
```

### With Custom Database Path

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
npx flowise start --FLOWISE_HOST=$HOST_IP --PORT=3000 --FLOWISE_DATABASE_PATH=/path/to/database
```

### With Environment File

Create a `.env` file in this directory:

```bash
# Example .env file
PORT=3000
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=secure_password
APIKEY_PATH=/path/to/apikeys
```

Then start Flowise:
```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
npx flowise start --FLOWISE_HOST=$HOST_IP
```

### Enable Debug Mode

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
DEBUG=true npx flowise start --FLOWISE_HOST=$HOST_IP --PORT=3000
```

## Configuration

### Environment Variables

Common environment variables you can set:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `FLOWISE_HOST` | Host to bind to | localhost |
| `FLOWISE_USERNAME` | Username for authentication | - |
| `FLOWISE_PASSWORD` | Password for authentication | - |
| `FLOWISE_DATABASE_PATH` | Path to database file | `~/.flowise` |
| `APIKEY_PATH` | Path to API keys file | `~/.flowise` |
| `LOG_PATH` | Path to log files | `~/.flowise/logs` |
| `DEBUG` | Enable debug logging | false |

### Database

Flowise uses SQLite by default and stores data in `~/.flowise/database.sqlite`. You can customize this with the `FLOWISE_DATABASE_PATH` environment variable.

## Network Access Best Practices

### Why Use get-eth0-ip.sh?

In WSL and VM environments, binding to `localhost` or `127.0.0.1` makes the service only accessible from within the container/VM. To access the web UI from your host machine's browser:

1. **❌ Don't do this:** `npx flowise start --FLOWISE_HOST=127.0.0.1`
   - Only accessible within the VM

2. **❌ Don't do this:** `npx flowise start --FLOWISE_HOST=0.0.0.0`
   - Binds to all interfaces (potential security risk)

3. **✅ Do this:**
   ```bash
   HOST_IP=$(../scripts/get-eth0-ip.sh)
   npx flowise start --FLOWISE_HOST=$HOST_IP
   ```
   - Binds to your specific network interface
   - Accessible from host browser
   - More secure than 0.0.0.0

### Convenience Script

The provided `run-flowise.sh` script already implements this best practice:

```bash
#!/bin/bash
# run-flowise.sh handles fresh clones and proper IP binding

./run-flowise.sh
```

Make it executable:
```bash
chmod +x run-flowise.sh
./run-flowise.sh
```

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:
```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
npx flowise start --FLOWISE_HOST=$HOST_IP --PORT=8080
```

Or edit the `.env` file:
```bash
PORT=8080
```

### Cannot Access from Host Browser

1. Verify you're using the network IP:
   ```bash
   ../scripts/get-eth0-ip.sh
   ```

2. Check if Flowise is actually bound to that IP:
   ```bash
   netstat -tlnp | grep 3000
   ```

3. Ensure your firewall allows connections on the port

### Fresh Clone - Dependencies Not Installing

If the automatic installation fails:

```bash
# Manually initialize npm
npm init -y

# Install Flowise
npm install flowise

# Then run normally
./run-flowise.sh
```

### Database Issues

If you encounter database errors:

```bash
# Backup your current database (if you have important data)
cp ~/.flowise/database.sqlite ~/.flowise/database.sqlite.backup

# Remove the database to start fresh
rm ~/.flowise/database.sqlite

# Restart Flowise
./run-flowise.sh
```

### Missing get-eth0-ip.sh Script

If you get an error about the missing script:

```bash
# Verify the scripts directory exists
ls ../scripts/get-eth0-ip.sh

# If missing, you may need to clone the complete repository
```

## Useful Commands

### Check Flowise Version

```bash
npx flowise --version
```

### List All Available Commands

```bash
npx flowise --help
```

### Start Command Options

```bash
npx flowise start --help
```

### Update Flowise

```bash
npm update flowise
```

### Reinstall from Scratch

```bash
# Remove node_modules and package files
rm -rf node_modules package.json package-lock.json

# Run the startup script (it will reinstall everything)
./run-flowise.sh
```

## Features

Flowise provides a low-code interface for building LLM applications with:

- **Visual Flow Builder:** Drag-and-drop interface for creating LLM chains
- **LLM Support:** OpenAI, Anthropic, Azure OpenAI, HuggingFace, and more
- **Vector Stores:** Pinecone, Qdrant, Weaviate, Chroma, and others
- **Document Loaders:** PDF, CSV, JSON, web scraping, and more
- **Embeddings:** Various embedding models for semantic search
- **Memory:** Conversation buffers and summaries
- **Agents:** Tool-using agents with various strategies
- **API Endpoints:** Each flow can be exposed as an API
- **Chatbot Widget:** Embeddable chat widget for websites
- **Templates:** Pre-built templates for common use cases

## Additional Resources

- **Flowise Documentation:** https://docs.flowiseai.com/
- **GitHub Repository:** https://github.com/FlowiseAI/Flowise
- **Discord Community:** https://discord.gg/jbaHfsRVBW
- **YouTube Tutorials:** https://www.youtube.com/@FlowiseAI

## Notes

- Flowise stores flows and configurations in `~/.flowise` by default
- Database file: `~/.flowise/database.sqlite` (SQLite by default)
- Each flow can be exported/imported as JSON for sharing and version control
- API keys for various LLM providers can be stored in the UI or via environment variables
- The web UI provides real-time testing of flows with a built-in chat interface
- Fresh git clones are automatically handled by `run-flowise.sh` - no manual setup required
