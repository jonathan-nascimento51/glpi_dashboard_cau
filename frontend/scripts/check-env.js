#!/usr/bin/env node
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.join(__dirname, '..', '.env');

try {
  assertEnv(['NEXT_PUBLIC_API_BASE_URL'], envPath);
  console.log(`NEXT_PUBLIC_API_BASE_URL resolved to: ${process.env.NEXT_PUBLIC_API_BASE_URL}`);
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
