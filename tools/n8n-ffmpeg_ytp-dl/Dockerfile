FROM docker.n8n.io/n8nio/n8n

USER root

RUN apk update \
	&& apk add --no-cache ffmpeg yt-dlp imagemagick \
	&& yt-dlp -U \
	&& rm -rf /var/cache/apk

USER node
