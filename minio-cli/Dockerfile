FROM alpine:3.14 

WORKDIR /minio

RUN apk add --no-cache wget \
        && wget https://dl.min.io/client/mc/release/linux-amd64/mc \
        && chmod +x mc \
        && mv mc /usr/bin/mc
