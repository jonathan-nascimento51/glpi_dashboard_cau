import { dockerClient } from 'testcontainers'
import fs from 'fs'
import path from 'path'

export default async function globalTeardown() {
  const idFile = path.join(__dirname, 'container-id')
  if (fs.existsSync(idFile)) {
    const id = fs.readFileSync(idFile, 'utf-8').trim()
    const { dockerode } = await dockerClient()
    await dockerode.getContainer(id).stop()
    fs.unlinkSync(idFile)
  }
}
