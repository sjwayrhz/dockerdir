FROM ubuntu:24.04

# 1. Install dependencies, SSH server, and cloudflared
# We install curl to fetch the GPG key and add the repository
# We use a robust grep/cut command to determine the OS codename (e.g., 'noble' or 'bookworm')
# avoiding potential shell sourcing issues.
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    openssh-server \
    sudo \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null \
    && CODENAME=$(grep "VERSION_CODENAME=" /etc/os-release | cut -d= -f2 | tr -d '"') \
    && echo "deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared $CODENAME main" | tee /etc/apt/sources.list.d/cloudflared.list \
    && apt-get update && apt-get install -y cloudflared \
    && rm -rf /var/lib/apt/lists/*

# 2. Configure SSH
RUN mkdir /var/run/sshd
# Enable root login if requested
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# Ensure the SSH directory exists
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# 3. Add the Public Key
# We echo the key directly into authorized_keys
RUN echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFiPkGdbLCgNbJnnQ3mLRo1pSVqoCjbO0/3MIGNHKPSJ" > /root/.ssh/authorized_keys \
    && chmod 600 /root/.ssh/authorized_keys

# 4. Setup Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the SSH port
EXPOSE 22

# Start the services
CMD ["/entrypoint.sh"]
