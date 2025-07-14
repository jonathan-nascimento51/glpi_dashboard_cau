FROM redis:7-alpine

COPY scripts/healthchecks/healthcheck-redis.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK \
  --interval=5s \
  --timeout=5s \
  --retries=5 \
  CMD ["healthcheck.sh"]
