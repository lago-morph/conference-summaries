# Setup Flowise in This Directory

Please set up Flowise in this directory with the following requirements:

## Tasks

1. **Install Flowise**
   - Install the latest version of Flowise
   - Use npm/npx for installation
   - Ensure all dependencies are properly installed

2. **Create README.md**
   - Create a comprehensive README.md file with:
     - Installation information and version
     - Quick start guide
     - Instructions for starting Flowise
     - **IMPORTANT**: Emphasize using `../scripts/get-eth0-ip.sh` to get the IP address when exposing the web UI for browser access
     - Explain why this is important in WSL/VM environments (similar to the langflow README in ../langflow/README.md)
     - Common usage patterns (custom port, environment variables, etc.)
     - Configuration options
     - Troubleshooting section
     - Network access best practices with clear ✅ correct and ❌ incorrect examples

3. **Create Startup Script**
   - Create a convenient startup script (e.g., `run-flowise.sh`) that:
     - Uses `../scripts/get-eth0-ip.sh` to get the network IP
     - Starts Flowise bound to that IP address
     - Is executable and ready for the user to run manually
     - Includes helpful comments

## Reference Materials

- Check `../langflow/README.md` for a similar example of how to structure the README
- Check `../scripts/README.md` for information about `get-eth0-ip.sh`
- The get-eth0-ip.sh script outputs just the IP address (e.g., "172.30.196.118")

## Network Access Requirements

When exposing web interfaces for browser access from the host machine:
- ❌ Don't bind to localhost/127.0.0.1 (only accessible within VM)
- ❌ Don't bind to 0.0.0.0 (security risk)
- ✅ Use: `HOST_IP=$(../scripts/get-eth0-ip.sh)` and bind to that IP

## Expected Outcome

After completion, the user should be able to:
1. Run `./run-flowise.sh` to start Flowise
2. Access Flowise web UI from their host browser
3. Reference the README.md for detailed usage instructions
