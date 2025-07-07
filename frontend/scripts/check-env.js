#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
}

if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
  console.error('NEXT_PUBLIC_API_BASE_URL is not defined. Create a .env file or export the variable before starting the app.');
  process.exit(1);
}

console.log(`NEXT_PUBLIC_API_BASE_URL resolved to: ${process.env.NEXT_PUBLIC_API_BASE_URL}`);

