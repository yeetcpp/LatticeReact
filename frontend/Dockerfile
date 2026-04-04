# Frontend Service (React/Vue/Angular - Ready for Integration)
# This will be activated when frontend is ready

FROM node:18-alpine as frontend-builder

WORKDIR /app

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# =====================================
# Production Frontend
# =====================================
FROM nginx:alpine as frontend-production

# Copy built assets
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]