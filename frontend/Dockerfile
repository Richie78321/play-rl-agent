FROM node:alpine as base

FROM base as deps
WORKDIR /app
COPY package*.json ./
RUN npm install

FROM base as builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM httpd:latest
COPY --from=builder /app/out/ /usr/local/apache2/htdocs/
EXPOSE 80
