# Use official Apache HTTPD base image
FROM httpd:2.4

WORKDIR /apache

# Copy all files from current dir into the Apache document root
COPY ./html /usr/local/apache2/htdocs/

COPY custom-conf.conf /usr/local/apache2/conf/conf.d/
    
# Expose port 80 (optional, for documentation)
EXPOSE 80
