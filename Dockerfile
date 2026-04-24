# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve Stage (using Vite preview for simple serving, or nginx)
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app ./
USER node
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
