import { act, renderHook } from '@testing-library/react'
import { useVoiceCommands } from '../useVoiceCommands'

declare global {
  interface Window {
    webkitSpeechRecognition: typeof SpeechRecognition
    SpeechRecognition: typeof SpeechRecognition
  }
}

class MockRecognition {
  start = jest.fn()
  stop = jest.fn()
  onresult: ((e: any) => void) | null = null
  onend: (() => void) | null = null
}

beforeEach(() => {
  ;(window as any).SpeechRecognition = MockRecognition as any
  ;(window as any).webkitSpeechRecognition = MockRecognition as any
})

test('starts and stops listening', () => {
  const { result } = renderHook(() => useVoiceCommands())
  act(() => {
    result.current.startListening()
  })
  expect(result.current.isListening).toBe(true)

  act(() => {
    result.current.stopListening()
  })
  expect(result.current.isListening).toBe(false)
})
