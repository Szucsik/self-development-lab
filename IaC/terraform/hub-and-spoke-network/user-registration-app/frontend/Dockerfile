FROM nginx:1.27-alpine

# Replace default nginx config with our minimal SPA-style config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static site files
COPY index.html style.css app.js config.js /usr/share/nginx/html/

# Entrypoint injects the backend URL into config.js before starting nginx
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
