#!/usr/bin/env node
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url'

// 1. Carrega .env
const __dirname = path.dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: path.join(__dirname, '..', '.env') })

// 2. Função de assert
function assertEnv(keys) {
  keys.forEach(key => {
    if (!process.env[key]) {
      if (process.env.NODE_ENV === 'test') {
        console.warn(
          `⚠️  Variável "${key}" ausente. Usando valor padrão para testes.`
        )
        process.env[key] = 'http://localhost:8000'
        return
      }
      console.error(`❌ Variável de ambiente obrigatória "${key}" não definida.`)
      process.exit(1)
    }
  })
}

// 3. Checa as variáveis
assertEnv(['NEXT_PUBLIC_API_BASE_URL', 'NEXT_PUBLIC_FARO_URL'])

// 4. Log de sucesso
console.log(
  `NEXT_PUBLIC_API_BASE_URL resolved to: ${process.env.NEXT_PUBLIC_API_BASE_URL}`
)
console.log(
  `NEXT_PUBLIC_FARO_URL resolved to: ${process.env.NEXT_PUBLIC_FARO_URL}`
)
