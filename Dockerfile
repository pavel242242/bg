# Use Apify base image
FROM apify/actor-node:18

# Install bore for tunneling (if not using cloudflare)
RUN curl -L https://github.com/ekzhang/bore/releases/download/v0.5.0/bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz | tar xz -C /usr/local/bin

# Optional: Install cloudflared for Cloudflare tunnel support
RUN wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
    dpkg -i cloudflared-linux-amd64.deb || true && \
    rm cloudflared-linux-amd64.deb

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY . ./

# Run the actor
CMD npm start
