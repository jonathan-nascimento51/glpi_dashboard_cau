This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

Before starting the server copy the example environment file and configure the API endpoint:

```bash
cp .env.example .env
```

Ensure `NEXT_PUBLIC_API_BASE_URL` points to the worker API (defaults to `http://localhost:8000`).

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

### Docker Compose

When running the dashboard via Docker Compose, `node_modules` is mounted as a
volume to avoid permission issues:

```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
```

This setup ensures `npm run dev` works inside the container and that the `next`
CLI is available.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

### Streaming Tickets

The worker API exposes `/tickets/stream` which returns progress updates while
ticket data is being fetched and processed. Example usage with `httpx`:

```python
import httpx

resp = httpx.get("http://localhost:8000/tickets/stream")
for line in resp.text.splitlines():
    print(line)
```

This will print:

```
fetching...
processing...
[{"id": 1}]
```

### Performance: List Virtualization

Very large ticket lists can hurt rendering performance if every row is mounted at
once. The `VirtualizedTicketTable` component automatically enables
`react-window` when the data set contains **100 rows or more**. For smaller
lists you may still use the component and tweak the threshold inside
`VirtualizedTicketTable.tsx`.

Example usage:

```tsx
<VirtualizedTicketTable rows={tickets} onRowClick={handleRowClick} />
```

During unit tests the virtualization layer is mocked so snapshots remain stable.
`jest.setup.ts` registers the mock:

```ts
jest.mock('react-window', () => {
  const React = require('react')
  const MockedList = (props: any) => <div>{props.children}</div>
  return {
    FixedSizeList: MockedList,
    VariableSizeList: MockedList,
  }
}, { virtual: true })
```

Make sure your Jest configuration includes this setup file via `setupFilesAfterEnv`.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
