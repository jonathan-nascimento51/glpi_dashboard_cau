import { GenericContainer } from 'testcontainers'
import fs from 'fs'
import path from 'path'
import { dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default async function globalSetup() {
  const context = path.resolve(__dirname, '..')
  const container = await GenericContainer.fromDockerfile(context)
    .build()
    .then((image) => image.withExposedPorts(8000).start())
  // StartedTestContainer is returned above

  const mappedPort = container.getMappedPort(8000)
  process.env.NEXT_PUBLIC_API_BASE_URL = `http://localhost:${mappedPort}`
  fs.writeFileSync(path.join(__dirname, 'container-id'), container.getId())
}
