docker build -t gallery-dl:v1 .
docker rm --force gallery-dl
docker run --name gallery-dl -d --restart always gallery-dl:v1