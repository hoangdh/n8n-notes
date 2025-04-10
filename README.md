# n8n-notes

## n8n with Docker and ngrok

- Setup [ngrok](https://dashboard.ngrok.com/get-started/setup/linux)
- Create a [new sub-domain in ngrok](https://dashboard.ngrok.com/domains)

```sh
DOMAIN=baby-shark-doodoodoodoo.ngrok-free.app

docker volume create n8n-volume

docker run -d --name n8n \
-e N8N_SECURE_COOKIE=false \
-e N8N_HOST=${DOMAIN} \
-e N8N_EDITOR_BASE_URL=https://${DOMAIN} \
-e WEBHOOK_URL=https://${DOMAIN} \
-e N8N_EXECUTIONS_DATA_MAX_SIZE=1000000000 \
-e N8N_DEFAULT_BINARY_DATA_MODE=filesystem \
-e NODE_FUNCTION_ALLOW_EXTERNAL=* \
-e TZ=Asia/Ho_Chi_Minh \
-e GENERIC_TIMEZONE=Asia/Ho_Chi_Minh \
-p 5678:5678 \
-v n8n-volume:/home/node/.n8n \
docker.n8n.io/n8nio/n8n

ngrok http --url=${DOMAIN} 5678
```

## Access now:
-> https://baby-shark-doodoodoodoo.ngrok-free.app
