# Langflow Setup

This directory contains a Langflow installation for building and experimenting with AI workflows and agents.

## Installation

Langflow has been installed in a virtual environment. The installation includes:
- **Version:** 1.6.9
- Multiple LLM providers (OpenAI, Anthropic, Cohere, Google, AWS Bedrock, etc.)
- Vector databases (Pinecone, Qdrant, Chroma, Weaviate, etc.)
- Document processing and OCR capabilities
- Web scraping and search tools
- And many more integrations

## Quick Start

### 1. Activate the Virtual Environment

```bash
source venv/bin/activate
```

### 2. Start Langflow

**For local access only (localhost):**
```bash
langflow run
```

**For network access (required for browser access from host machine):**

⚠️ **IMPORTANT:** When exposing web interfaces intended for browser access, always use the `get-eth0-ip.sh` script to get the correct IP address to bind to. This is especially important in WSL or VM environments.

```bash
# Get the network IP address
HOST_IP=$(../scripts/get-eth0-ip.sh)

# Start langflow bound to the network IP
langflow run --host $HOST_IP
```

**Example output:**
```
Starting Langflow...
╭───────────────────────────────────────────────────╮
│ Welcome to ⛓ Langflow                             │
│                                                   │
│ Access http://172.30.196.118:7860                │
│                                                   │
│ Collaborate, and contribute at our GitHub Repo   │
╰───────────────────────────────────────────────────╯
```

### 3. Access the Web UI

Open your browser and navigate to the URL displayed in the terminal (e.g., `http://172.30.196.118:7860`).

## Common Usage Patterns

### Custom Port

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --port 8080
```

### Disable Browser Auto-Open

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --no-open-browser
```

### Development Mode

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --dev
```

### Backend Only (No Frontend)

Useful when developing custom frontends or using Langflow as an API:

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --backend-only
```

### Custom Components Directory

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --components-path ./custom_components
```

### With Environment File

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --env-file .env
```

## Configuration

### Environment Variables

Create a `.env` file in this directory to configure Langflow:

```bash
# Example .env file
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
LANGFLOW_CONFIG_DIR=~/.langflow
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Log Levels

Available log levels: `debug`, `info`, `warning`, `error`, `critical`

```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --log-level debug
```

## Network Access Best Practices

### Why Use get-eth0-ip.sh?

In WSL and VM environments, binding to `localhost` or `127.0.0.1` makes the service only accessible from within the container/VM. To access the web UI from your host machine's browser:

1. **❌ Don't do this:** `langflow run --host 127.0.0.1`
   - Only accessible within the VM

2. **❌ Don't do this:** `langflow run --host 0.0.0.0`
   - Binds to all interfaces (potential security risk)

3. **✅ Do this:**
   ```bash
   HOST_IP=$(../scripts/get-eth0-ip.sh)
   langflow run --host $HOST_IP
   ```
   - Binds to your specific network interface
   - Accessible from host browser
   - More secure than 0.0.0.0

### Convenience Script

Create a launch script for easy startup:

```bash
#!/bin/bash
# run-langflow.sh

# Activate virtual environment
source venv/bin/activate

# Get network IP
HOST_IP=$(../scripts/get-eth0-ip.sh)

# Start Langflow
langflow run --host $HOST_IP --port 7860 --no-open-browser

# Or with custom options:
# langflow run --host $HOST_IP --port 7860 --dev --log-level debug
```

Make it executable:
```bash
chmod +x run-langflow.sh
./run-langflow.sh
```

## Troubleshooting

### Port Already in Use

If port 7860 is already in use:
```bash
HOST_IP=$(../scripts/get-eth0-ip.sh)
langflow run --host $HOST_IP --port 8080
```

### Cannot Access from Host Browser

1. Verify you're using the network IP:
   ```bash
   ../scripts/get-eth0-ip.sh
   ```

2. Check if langflow is actually bound to that IP:
   ```bash
   netstat -tlnp | grep 7860
   ```

3. Ensure your firewall allows connections on the port

### Virtual Environment Issues

If you encounter issues with the virtual environment:
```bash
# Deactivate current environment
deactivate

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install langflow
```

## Useful Commands

### Check Langflow Version
```bash
langflow --version
```

### List All Available Commands
```bash
langflow --help
```

### View Run Options
```bash
langflow run --help
```

### Update Langflow
```bash
source venv/bin/activate
pip install --upgrade langflow
```

## Additional Resources

- **Langflow Documentation:** https://docs.langflow.org/
- **GitHub Repository:** https://github.com/logspace-ai/langflow
- **Community Discord:** https://discord.gg/langflow

## Notes

- Langflow stores flows and configurations in `~/.langflow` by default
- Database file: `langflow.db` (SQLite by default)
- Logs can be configured with `--log-file` option
- The web UI provides a visual flow builder for creating AI workflows
- Flows can be exported/imported as JSON files for sharing and version control
