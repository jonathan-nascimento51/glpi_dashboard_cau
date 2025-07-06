import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))


const profilePath = path.join(__dirname, '..', '.next', 'profile-events.json')
if (!fs.existsSync(profilePath)) {
  console.error('profile-events.json not found. Build with REACT_PROFILER=true')
  process.exit(1)
}
const destDir = path.join(__dirname, '..', 'perf')
fs.mkdirSync(destDir, { recursive: true })
const dest = path.join(destDir, 'profile-events.json')
fs.copyFileSync(profilePath, dest)
console.log(`Profile saved to ${dest}`)

