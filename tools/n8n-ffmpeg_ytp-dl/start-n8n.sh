DOMAIN=n8n.example.com

docker build -t n8n:ffmpeg_yt-dlp .
docker rm --force n8n-auto

docker volume create n8n-auto_data
docker run -d --name n8n-auto \
	-e N8N_SECURE_COOKIE=false \
	-e N8N_HOST=${DOMAIN} \
	-e N8N_EDITOR_BASE_URL=https://${DOMAIN} \
	-e WEBHOOK_URL=https://${DOMAIN} \
	-e N8N_EXECUTIONS_DATA_MAX_SIZE=1000000000 \
	-e N8N_DEFAULT_BINARY_DATA_MODE=filesystem \
	-e NODE_FUNCTION_ALLOW_EXTERNAL=* \
	-v n8n-auto_data:/home/node/.n8n n8n:ffmpeg_yt-dlp