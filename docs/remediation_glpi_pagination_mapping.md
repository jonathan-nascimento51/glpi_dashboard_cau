# Fixing GLPI Pagination and ID Mapping

This guide describes how to ensure the dashboard retrieves **all** ticket data and converts numeric fields into readable text.

## 1. Reliable Pagination

Use the `Content-Range` header from GLPI responses to determine the total number of records. Continue fetching pages until the amount collected matches this total. If the header is missing, fallback to checking if the current page returned fewer records than requested.

## 2. Enum Mapping

Map the numeric `status`, `priority`, `impact` and `type` values using the dictionaries in `glpi_api_client.py`. This keeps the output consistent across the async and sync clients.

## Example Patch

```python
# inside GLPISession.get_all()
page_data, headers = await self._request("GET", endpoint, params=page_params, return_headers=True)
total = int(headers.get("Content-Range", "0/0").split("/")[1])
```
