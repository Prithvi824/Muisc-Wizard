# Stage 1: build the app
FROM node:18-alpine AS builder

# set working directory
WORKDIR /app

# copy packages
COPY package*.json ./

# install packages
RUN npm install

# copy app
COPY . .

# set environment variables from .env file
ENV VITE_API_URL=https://wizard.run.place/backend
ENV VITE_ALLOWED_HOST=*

# build the app
RUN npm run build

# Stage 2: serve the app
FROM nginx:alpine

# copy the build folder
COPY --from=builder /app/dist /usr/share/nginx/html

# set nginx config
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# expose port
EXPOSE 80

# start
CMD ["nginx", "-g", "daemon off;"]