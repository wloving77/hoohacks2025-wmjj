docker build -t apache-image -f ./Dockerfile.apache .
docker run -p 8080:80 --name apache-container apache-image