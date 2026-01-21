FROM docker.n8n.io/n8nio/n8n

USER root

RUN wget https://gitlab.alpinelinux.org/api/v4/projects/5/packages/generic/v2.14.4/x86_64/apk.static -O /tmp/apk.static \
	&& chmod +x /tmp/apk.static \
	&& /tmp/apk.static -X http://dl-cdn.alpinelinux.org/alpine/v3.22/main -U --allow-untrusted --initdb add apk-tools \
	&& apk update \
	&& apk add --no-cache ffmpeg imagemagick \
	&& rm -rf /var/cache/apk /tmp/apk.static

USER node
