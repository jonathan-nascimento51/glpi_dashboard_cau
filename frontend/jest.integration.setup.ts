import { execSync } from 'child_process';
import path from 'path';

export default async function globalSetup() {
  const composeFile = path.resolve(__dirname, '../tests/integration/docker-compose.yml');
  execSync(`docker compose -f ${composeFile} up -d --build`, { stdio: 'inherit' });
  process.env.API_BASE_URL = 'http://localhost:8000';
}
