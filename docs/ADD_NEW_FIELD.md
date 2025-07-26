# Checklist: Adding a New GLPI Field

This guide outlines the typical steps to expose a new attribute from the GLPI REST API all the way to the user interface.

## 1. Backend

1. Extend the Pydantic models in `src/shared/dto.py`:

   ```python
   class RawTicketFromAPI(BaseModel):
       ...
       users_id_requester: Optional[int] = Field(None, alias="users_id_requester")

   class CleanTicketDTO(BaseModel):
       ...
       requester: Optional[str] = None
   ```

2. In `TicketTranslator.translate_ticket`, resolve the user name through `MappingService.get_username` and include `requester` in the returned dict.
3. If necessary, update `FIELD_ALIASES` in `backend/infrastructure/glpi/normalization.py` and include the column when returning the DataFrame.

## 2. Tests

1. Update fixtures under `tests/` with the new key.
2. Add assertions in `tests/test_clean_ticket_dto.py` and endpoint tests to verify the field is populated.

## 3. Front-end

1. Regenerate TypeScript definitions:

   ```bash
   make gen-types
   ```

2. Add the property to `src/frontend/react_app/src/types/ticket.ts` and copy it in `useTickets.ts`.
3. Render the field in `TicketTable.tsx` and related components with a fallback:

   ```tsx
   <th scope="col">Requerente</th>
   ...
   <td>{ticket.requester ?? '—'}</td>
   ```

4. Update unit tests and Storybook snapshots.

## 4. Documentation

1. Export the updated OpenAPI schema for consumers:

   ```bash
   python worker.py &
   curl http://127.0.0.1:8000/openapi.json -o openapi.json
   kill %1
   ```

2. Document the new field in `README.md` or the appropriate guide.

## 5. Continuous Integration

Run the checks below before submitting a PR so CI passes:

```bash
pre-commit run --all-files
pytest -k test_tickets
cd src/frontend/react_app && npm run test:unit -- -u && npm run build
```

## Acceptance Criteria

- All linters and type checks succeed.
- Backend and frontend tests pass.
- The React build completes without errors.
- Documentation and OpenAPI schema mention the new attribute.
