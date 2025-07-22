# Diagnosing "Nenhum chamado encontrado" Issues

This guide outlines steps to troubleshoot cases where the dashboard shows **Nenhum chamado encontrado** even though the GLPI API contains tickets.

## 1. Validate API Endpoints
1. Confirm which GLPI endpoints are queried. Typical calls are:
   - `/search/Ticket`
   - `/TicketStatus`
   - `/User`
2. Use `curl` or Postman to verify the endpoints respond correctly. When using `/search/Ticket`, include `expand_dropdowns=1` to expand dropdowns.
3. Check pagination headers (`Content-Range`). If missing, request sequential pages until no new records are returned.

## 2. Verify Pagination Logic
The worker relies on `paginate_items()` inside `src/backend/utils/pagination.py` to loop over pages. Ensure each request updates the `range` parameter and continues while items are returned. Inspect logs to confirm multiple pages are fetched when more than one page of tickets exist.

## 3. Check ID Mapping
`MappingService` translates numeric IDs into readable names. If mappings fail, tickets may validate incorrectly and be discarded. Monitor backend logs for warnings like `failed to translate ticket` and verify Redis contains hash keys starting with `glpi:mappings:`.

## 4. Inspect Filters
Incorrect filters in the `criteria` parameter can hide tickets. Review query parameters built in the backend before they reach GLPI. Use server-side filtering when possible to reduce payloads.

## 5. Review Backend Logs
Run `docker compose up --build -d` and follow logs with `docker compose logs -f <service-name>`. Replace `<service-name>` with the actual name of the backend service as defined in your `docker-compose.yml` file. Look for:
- "GLPI session initiated successfully"
- Multiple GET requests with varying `range` values
- "Loaded X entries" from `MappingService`
Any errors during these steps may explain missing data.

## 6. Use Mock Data for Isolation
Set `USE_MOCK_DATA=true` to confirm the dashboard renders example tickets correctly. If mock data works but the real API does not, focus on network access and authentication.

Following this checklist will help identify whether missing tickets are due to pagination, mapping, filtering or connectivity issues.
