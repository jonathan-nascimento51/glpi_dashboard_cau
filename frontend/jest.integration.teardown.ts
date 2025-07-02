import { execSync } from 'child_process';
import path from 'path';

export default async function globalTeardown() {
  const composeFile = path.resolve(__dirname, '../tests/integration/docker-compose.yml');
  execSync(`docker compose -f ${composeFile} down -v`, { stdio: 'inherit' });
}
