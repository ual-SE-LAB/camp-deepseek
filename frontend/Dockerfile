# Using super light Nginx
FROM nginx:alpine

# Delete default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy our web files
COPY index.html /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

# Set permissions
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]