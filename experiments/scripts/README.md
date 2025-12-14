# Scripts Directory

## Instructions for AI Agents

When adding a new script to this directory, update this README.md by:
1. Adding a new entry in the **Available Scripts** section below
2. Following the existing format: script name as h3 heading, description, usage example, and tips
3. Keep entries in alphabetical order
4. Ensure all code examples use proper markdown code blocks
5. Include practical usage examples, especially for integration with Docker, Git, or other common tools

---

## Available Scripts

### get-eth0-ip.sh

**Description:** Extracts and returns the IP address of the eth0 network interface. Useful when developing in WSL or VMs where you need to expose Docker containers to your host machine's real IP address instead of localhost.

**Usage:**
```bash
./get-eth0-ip.sh
```

**Output:**
```
172.30.196.118
```

**Tips:**
- Use with Docker to bind container ports to your actual network IP:
  ```bash
  docker run -p $(./get-eth0-ip.sh):8080:8080 your-image
  ```
- Store in a variable for repeated use:
  ```bash
  HOST_IP=$(./get-eth0-ip.sh)
  docker run -p $HOST_IP:8080:8080 image1
  docker run -p $HOST_IP:3000:3000 image2
  ```
- Useful in docker-compose.yml environment variables:
  ```bash
  HOST_IP=$(./get-eth0-ip.sh) docker-compose up
  ```
