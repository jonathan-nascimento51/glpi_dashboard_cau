# Fixing GLPI Pagination and ID Mapping

This remediation guide explains how to retrieve every ticket from the GLPI API and translate numeric fields into readable labels.

## 1. Reliable Pagination

Do **not** depend solely on the `Content-Range` header. Community reports show this header may be missing or inaccurate. The safest approach is to keep requesting pages until the API stops returning new items. When available, the `totalcount` field can be used to sanity-check the number of results.

```python
offset = 0
page_size = 100
while True:
    params["range"] = f"{offset}-{offset + page_size - 1}"
    data, headers = await self._request("GET", endpoint, params=params, return_headers=True)
    items = data.get("data", data)
    results.extend(items)
    if len(items) < page_size:
        break
    offset += page_size
```

## 2. Enum Mapping

The API parameter `expand_dropdowns` only expands configurable dropdowns. Fields such as `status`, `priority`, `impact` and `type` still arrive as numbers. Use the dictionaries defined in `glpi_session.py` (`STATUS_MAP`, `PRIORITY_MAP`, `IMPACT_MAP`, `TYPE_MAP`) to convert these values.
