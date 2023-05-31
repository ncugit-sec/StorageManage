FROM nginx:1.25.0-alpine
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --chmod=755 ./static /usr/share/nginx/html/static