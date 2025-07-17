FROM redis:7-alpine
RUN apk add --no-cache bash

COPY scripts/healthchecks/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh
ENV HC_TARGET=redis

HEALTHCHECK \
  --interval=15s \
  --timeout=3s \
  --start-period=10s \
  --retries=3 \
  CMD ["bash", "/usr/local/bin/healthcheck.sh"]
