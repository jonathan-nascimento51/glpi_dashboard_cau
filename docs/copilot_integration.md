# Integrating Copilot Studio

This guide outlines the required steps to connect the GLPI worker API to Microsoft Copilot Studio.

## 1. Export the OpenAPI schema

Use FastAPI's built-in command to save the schema:

```bash
PYTHONPATH=$(pwd) python worker_api.py --export-openapi openapi.json
```

Upload `openapi.json` when creating the connector in Power Platform.

## 2. Create a custom connector

In the Power Platform portal select **Custom connectors** and choose the **Import an OpenAPI file** option. Provide the exported schema and specify the base URL of the worker API.

## 3. Configure authentication

Set the connector to use **OAuth 2.0** with Azure Active Directory. Store client secrets in Azure Key Vault and reference them through the portal so that credentials are not kept in plain text.

## 4. Define Copilot Studio topics

Create topics that call the connector actions. Map the fields returned by the API to user-friendly variables and confirm the conversation flow in the test chat.

## 5. Publish to Microsoft Teams

After validating the topics, publish the bot and enable the Microsoft Teams channel. The Copilot will then be available for all permitted users in your organization.
