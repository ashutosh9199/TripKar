# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve Stage (Production static server)
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --chown=node:node --from=builder /app/dist ./dist
USER node
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
