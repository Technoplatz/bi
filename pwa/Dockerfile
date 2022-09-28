FROM node:16-alpine as build
WORKDIR /app
RUN npm install -g npm
RUN npm install -g @ionic/cli
COPY package*.json /app/
RUN npm install --force
COPY . /app/
RUN ionic build --prod
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/www /usr/share/nginx/html
EXPOSE 80