FROM postgres:15-alpine

COPY scripts/healthchecks/healthcheck-postgres.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK \
  --interval=10s \
  --timeout=5s \
  --retries=5 \
  CMD ["healthcheck.sh"]
