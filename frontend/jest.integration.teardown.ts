import { Docker } from 'testcontainers'
import fs from 'fs'
import path from 'path'

export default async function globalTeardown() {
  const idFile = path.join(__dirname, 'container-id')
  if (fs.existsSync(idFile)) {
    const id = fs.readFileSync(idFile, 'utf-8').trim()
    const docker = new Docker()
    await docker.getContainer(id).stop()
    fs.unlinkSync(idFile)
  }
}
