FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./
COPY tsconfig.json ./

# Install ALL dependencies (including dev deps for building)
RUN npm install

# Copy source code
COPY src ./src

# Build TypeScript
RUN npm run build

# Remove dev dependencies and source files (keep only dist)
RUN npm prune --production && \
    rm -rf src tsconfig.json

# Expose port (optional, as this is a bot polling service)
EXPOSE 3000

# Run the application
CMD ["npm", "start"]

