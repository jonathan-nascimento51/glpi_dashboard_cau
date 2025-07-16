# Research Backlog

This document lists topics that require additional investigation to strengthen the project architecture and documentation.

## Topics to Research

- **ESM vs. CommonJS**: Gather best practices for migrating Node.js scripts to native ES Modules. Document how to use the `.cjs` extension for legacy files and how to replace `require` with `import` using `fileURLToPath` to emulate `__dirname`.
- **Least-Privilege Database Roles**: Explore strategies for creating PostgreSQL users with minimal permissions. Document how to avoid running the application as a superuser inside Docker.
- **Secure Docker Initialization**: Review techniques for deterministic container setup using environment variables and seed scripts. Ensure the database initializes with the correct roles and passwords.
- **Next.js Environment Variables**: Confirm recommended prefixes (`NEXT_PUBLIC_*`) and loading order when running under Vite or Next.js. Provide guidelines for check-env scripts.

Update this backlog as new issues arise or existing ones are resolved.
