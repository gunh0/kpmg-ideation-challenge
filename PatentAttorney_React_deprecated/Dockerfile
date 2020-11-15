# Use the official Node.js image as the base image
FROM node:14-alpine as builder

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Install the dependencies
RUN npm ci --only=production

# Copy the project files to the container
COPY . .

# Build the React app
RUN npm run build

# Use a lightweight web server to serve the built React app
FROM nginx:alpine

# Copy the built app to the NGINX web server directory
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80 for the NGINX server
EXPOSE 80

# Start NGINX server when the container starts
CMD ["nginx", "-g", "daemon off;"]
