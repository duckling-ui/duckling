# Duckling Frontend Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for better caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --silent

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN adduser -D -g '' nginxuser \
    && chown -R nginxuser:nginxuser /usr/share/nginx/html \
    && chown -R nginxuser:nginxuser /var/cache/nginx \
    && chown -R nginxuser:nginxuser /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown -R nginxuser:nginxuser /var/run/nginx.pid

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
