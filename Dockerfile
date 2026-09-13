FROM python:3.14-alpine

LABEL org.opencontainers.image.title="Gandi DDNS"
LABEL org.opencontainers.image.description="Dynamic DNS Update Client for Gandi's LiveDNS"
LABEL org.opencontainers.image.authors="Winston Astrachan"
LABEL org.opencontainers.image.source="https://github.com/wastrachan/docker-gandi-ddns/"
LABEL org.opencontainers.image.licenses="MIT"

ARG SHOUTRRR_VERSION=0.8.0
ARG TARGETARCH
ARG TARGETVARIANT

COPY app/ /
RUN set -eux; \
    pip install -r /requirements.txt; \
    case "${TARGETARCH}/${TARGETVARIANT:-}" in \
        amd64/)  SHOUTRRR_ARCH="amd64"  ;; \
        arm64/)  SHOUTRRR_ARCH="arm64"  ;; \
        arm/v7)  SHOUTRRR_ARCH="armv6"  ;; \
        *)       SHOUTRRR_ARCH="${TARGETARCH}" ;; \
    esac; \
    wget -q -O /tmp/shoutrrr.tar.gz \
        "https://github.com/containrrr/shoutrrr/releases/download/v${SHOUTRRR_VERSION}/shoutrrr_linux_${SHOUTRRR_ARCH}.tar.gz"; \
    tar -xzf /tmp/shoutrrr.tar.gz -C /usr/local/bin shoutrrr; \
    chmod +x /usr/local/bin/shoutrrr; \
    rm /tmp/shoutrrr.tar.gz

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["crond", "-f", "-c", "/etc/crontabs/"]
