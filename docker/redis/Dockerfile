FROM redis:7-alpine

COPY scripts/healthchecks/healthcheck-redis.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK \
  --interval=15s \
  --timeout=3s \
  --start-period=10s \
  --retries=3 \
  CMD ["healthcheck.sh"]
