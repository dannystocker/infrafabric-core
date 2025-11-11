# Multi-stage Dockerfile for IF.swarm WebRTC Signaling Server
#
# Philosophy:
# - IF.ground: Reproducible container builds
# - IF.witness: Build metadata and logging
# - IF.TTT: Transparent build process

# ============================================
# Stage 1: Build
# ============================================
FROM node:18-alpine AS builder

LABEL maintainer="IF.swarm Team"
LABEL description="WebRTC Signaling Server for IF.swarm Agent Mesh"

WORKDIR /build

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# ============================================
# Stage 2: Production
# ============================================
FROM node:18-alpine

WORKDIR /app

# Install production dependencies only
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built artifacts from builder
COPY --from=builder /build/dist ./dist

# Create non-root user for security
RUN addgroup -g 1001 ifswarm && \
    adduser -D -u 1001 -G ifswarm ifswarm && \
    chown -R ifswarm:ifswarm /app

# Switch to non-root user
USER ifswarm

# Expose signaling server port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8443', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));"

# Environment variables (can be overridden)
ENV NODE_ENV=production
ENV PORT=8443
ENV HOST=0.0.0.0

# Start signaling server
CMD ["node", "dist/communication/webrtc-signaling-server.js"]

# Build metadata
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.title="IF.swarm WebRTC Signaling Server"
LABEL org.opencontainers.image.description="WebSocket signaling server for IF.swarm agent mesh communication"
LABEL org.opencontainers.image.vendor="IF.swarm"
