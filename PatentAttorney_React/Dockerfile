# Use the official Node.js 14 LTS image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the project files to the working directory
COPY . .

# Build the React project
RUN npm run build

# Expose the desired port
EXPOSE 3000

# Define the command to run your app
CMD ["npm", "start"]
