#!/usr/bin/env node
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url'

// 1. Carrega .env
const __dirname = path.dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: path.join(__dirname, '..', '.env') })

// 2. Função de assert
function assertEnv(keys) {
  const defaults = {
    VITE_API_BASE_URL: 'http://localhost:8000',
  };

  keys.forEach(key => {
    if (!process.env[key]) {
      if (process.env.NODE_ENV === 'test') {
        const fallback = defaults[key]
        if (fallback) {
          console.warn(
            `⚠️  Variável "${key}" ausente. Usando valor padrão para testes: ${fallback}`
          )
          process.env[key] = fallback
          return
        }
      }
      console.error(`❌ Variável de ambiente obrigatória "${key}" não definida.`)
      process.exit(1)
    }
  })
}

// 3. Checa as variáveis
if (!process.env.VITE_API_BASE_URL && process.env.NEXT_PUBLIC_API_BASE_URL) {
  console.warn(
    '⚠️  Variável "VITE_API_BASE_URL" ausente. Usando valor de NEXT_PUBLIC_API_BASE_URL.',
  );
  process.env.VITE_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
}
assertEnv(['VITE_API_BASE_URL']);

if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
  process.env.NEXT_PUBLIC_API_BASE_URL = process.env.VITE_API_BASE_URL;
}

// 4. Log de sucesso
console.log(`VITE_API_BASE_URL resolved to: ${process.env.VITE_API_BASE_URL}`);
if (process.env.NEXT_PUBLIC_FARO_URL) {
  console.log(
    `NEXT_PUBLIC_FARO_URL resolved to: ${process.env.NEXT_PUBLIC_FARO_URL}`
  );
} else {
  console.warn('⚠️  Variável "NEXT_PUBLIC_FARO_URL" ausente. A instrumentação do Faro será desativada.');
}
