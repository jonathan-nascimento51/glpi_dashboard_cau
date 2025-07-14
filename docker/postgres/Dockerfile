FROM postgres:15-alpine

COPY scripts/healthchecks/healthcheck-postgres.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK \
  --interval=15s \
  --timeout=5s \
  --start-period=30s \
  --retries=3 \
  CMD ["healthcheck.sh"]
