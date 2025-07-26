import { act, renderHook } from '@testing-library/react'
import { useVoiceCommands } from '../useVoiceCommands'

class MockRecognition {
  start = jest.fn()
  stop = jest.fn()
  onresult: ((e: any) => void) | null = null
  onend: (() => void) | null = null

  triggerResult(event: any) {
    this.onresult?.(event)
  }

  triggerEnd() {
    this.onend?.()
  }
}

let recognitionInstance: MockRecognition

beforeEach(() => {
  jest.clearAllMocks()
  recognitionInstance = new MockRecognition()
  ;(window as any).SpeechRecognition = jest
    .fn(() => recognitionInstance)
    .mockName('SpeechRecognition')
  ;(window as any).webkitSpeechRecognition = window.SpeechRecognition
})

describe('useVoiceCommands', () => {
  it('starts listening and calls recognition.start', () => {
    const { result } = renderHook(() => useVoiceCommands())

    act(() => {
      result.current.startListening()
    })

    expect(result.current.isListening).toBe(true)
    expect(recognitionInstance.start).toHaveBeenCalledTimes(1)
  })

  it('stops listening and calls recognition.stop', () => {
    const { result } = renderHook(() => useVoiceCommands())

    act(() => {
      result.current.startListening()
    })
    act(() => {
      result.current.stopListening()
    })

    expect(recognitionInstance.stop).toHaveBeenCalledTimes(1)
  })

  it('processes commands on result', () => {
    const { result } = renderHook(() => useVoiceCommands())
    const debugSpy = jest.spyOn(console, 'debug').mockImplementation(() => {})

    act(() => {
      result.current.startListening()
    })

    const event = { results: [[{ transcript: 'hello world' }]] }
    act(() => {
      recognitionInstance.triggerResult(event)
    })

    expect(debugSpy).toHaveBeenCalledWith(
      'Recognized voice command:',
      'hello world'
    )
  })

  it('sets isListening to false on end', () => {
    const { result } = renderHook(() => useVoiceCommands())

    act(() => {
      result.current.startListening()
    })

    expect(result.current.isListening).toBe(true)

    act(() => {
      recognitionInstance.triggerEnd()
    })

    expect(result.current.isListening).toBe(false)
  })
})
