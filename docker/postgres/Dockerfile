FROM postgres:15-alpine
RUN apk add --no-cache bash

COPY scripts/healthchecks/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh
ENV HC_TARGET=db

HEALTHCHECK \
  --interval=15s \
  --timeout=5s \
  --start-period=30s \
  --retries=3 \
  CMD ["bash", "/usr/local/bin/healthcheck.sh"]
