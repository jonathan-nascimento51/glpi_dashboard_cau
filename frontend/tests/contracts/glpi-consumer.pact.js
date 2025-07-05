import path from 'node:path'
import { PactV3, MatchersV3 } from '@pact-foundation/pact/v3'

const { like } = MatchersV3
const pactDir = path.resolve(process.cwd(), 'pacts')

function createProvider() {
  return new PactV3({
    consumer: 'NextDashboard',
    provider: 'GLPI API',
    dir: pactDir,
    logLevel: 'warn',
  })
}

describe('POST /initSession', () => {
  test('returns session token on success', async () => {
    const provider = createProvider()

    provider
      .given('valid credentials')
      .uponReceiving('a valid initSession request')
      .withRequest({
        method: 'POST',
        path: '/initSession',
        headers: { 'Content-Type': 'application/json' },
        body: { user_token: 'USER', app_token: 'APP' },
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: { session_token: like('123e4567-e89b-12d3-a456-426614174000') },
      })

    await provider.executeTest(async mockServer => {
      const res = await fetch(`${mockServer.url}/initSession`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_token: 'USER', app_token: 'APP' }),
      })

      expect(res.status).toBe(200)
      const json = await res.json()
      expect(json).toHaveProperty('session_token')
    })
  })

  test('returns 401 for invalid tokens', async () => {
    const provider = createProvider()

    provider
      .given('invalid credentials')
      .uponReceiving('a request with invalid tokens')
      .withRequest({
        method: 'POST',
        path: '/initSession',
        headers: { 'Content-Type': 'application/json' },
        body: { user_token: 'BAD', app_token: 'BAD' },
      })
      .willRespondWith({ status: 401 })

    await provider.executeTest(async mockServer => {
      const res = await fetch(`${mockServer.url}/initSession`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_token: 'BAD', app_token: 'BAD' }),
      })

      expect(res.status).toBe(401)
    })
  })

  test('returns 503 when service unavailable', async () => {
    const provider = createProvider()

    provider
      .given('service unavailable')
      .uponReceiving('a request when service is down')
      .withRequest({
        method: 'POST',
        path: '/initSession',
        headers: { 'Content-Type': 'application/json' },
        body: { user_token: 'ANY', app_token: 'ANY' },
      })
      .willRespondWith({ status: 503 })

    await provider.executeTest(async mockServer => {
      const res = await fetch(`${mockServer.url}/initSession`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_token: 'ANY', app_token: 'ANY' }),
      })

      expect(res.status).toBe(503)
    })
  })
})
