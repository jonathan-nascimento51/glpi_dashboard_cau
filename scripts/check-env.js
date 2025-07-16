#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

function loadEnv(envPath) {
  if (!fs.existsSync(envPath)) return;
  const content = fs.readFileSync(envPath, 'utf8');
  for (const line of content.split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z0-9_]+)\s*=\s*(.*)\s*$/);
    if (match) {
      const [, key, val] = match;
      if (process.env[key] === undefined) {
        process.env[key] = val.replace(/^['"]|['"]$/g, '');
      }
    }
  }
}

export function assertEnv(required = [], envPath = path.join(rootDir, '.env')) {
  loadEnv(envPath);
  const missing = required.filter((name) => !process.env[name]);
  if (missing.length) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  try {
    assertEnv(['GLPI_BASE_URL', 'GLPI_APP_TOKEN', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']);
    if (!process.env.GLPI_USER_TOKEN && !(process.env.GLPI_USERNAME && process.env.GLPI_PASSWORD)) {
      throw new Error('Define GLPI_USER_TOKEN or both GLPI_USERNAME and GLPI_PASSWORD');
    }
    console.log('All required environment variables are set.');
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
