# Stage 1: The Build Environment
# Use a Node image to build the React application
FROM node:18-alpine as builder

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install only the necessary production dependencies and build tools
# We use 'npm ci' for a clean install
RUN npm ci --legacy-peer-deps

# Copy the rest of the application files
COPY . .

# Build the React application. This creates the 'build' directory.
# This stage still contains all dev dependencies, which we discard later.
RUN npm run build

# ---
# Stage 2: The Production Serving Environment (Minimal Runtime)
# Start fresh with a clean, minimal Node image
FROM node:18-alpine

# Set the working directory
WORKDIR /usr/src/app

# Only install the 'serve' utility globally, which is needed for the CMD
RUN npm install -g serve

# Copy ONLY the built static files from the 'builder' stage
# The 'build' directory contains the optimized static assets (HTML, CSS, JS)
COPY --from=builder /app/build ./build

# Define environment variables
ENV NODE_ENV production
ENV PORT 3000

# Expose the port where 'serve' listens
EXPOSE 3000

# Command to run the application using 'serve'
CMD ["serve", "-s", "build", "-l", "3000"]
