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

    debugSpy.mockRestore()
  })

  it('processes multiple transcripts in results', () => {
    const { result } = renderHook(() => useVoiceCommands())
    const debugSpy = jest.spyOn(console, 'debug').mockImplementation(() => {})

    act(() => {
      result.current.startListening()
    })

    const event = { results: [[{ transcript: 'first command' }, { transcript: 'second command' }]] }
    act(() => {
      recognitionInstance.triggerResult(event)
    })

    expect(debugSpy).toHaveBeenCalledWith(
      'Recognized voice command:',
      'first command'
    )
    expect(debugSpy).toHaveBeenCalledWith(
      'Recognized voice command:',
      'second command'
    )

    debugSpy.mockRestore()
  })

  it('handles empty results gracefully', () => {
    const { result } = renderHook(() => useVoiceCommands())
    const debugSpy = jest.spyOn(console, 'debug').mockImplementation(() => {})

    act(() => {
      result.current.startListening()
    })

    const event = { results: [] }
    act(() => {
      recognitionInstance.triggerResult(event)
    })

    expect(debugSpy).not.toHaveBeenCalled()

    debugSpy.mockRestore()
  })

  it('handles unexpected result structures gracefully', () => {
    const { result } = renderHook(() => useVoiceCommands())
    const debugSpy = jest.spyOn(console, 'debug').mockImplementation(() => {})

    act(() => {
      result.current.startListening()
    })

    // results is undefined
    const event1 = {}
    act(() => {
      recognitionInstance.triggerResult(event1)
    })

    // results is not an array
    const event2 = { results: null }
    act(() => {
      recognitionInstance.triggerResult(event2)
    })

    // results is array but contains non-array
    const event3 = { results: [null] }
    act(() => {
      recognitionInstance.triggerResult(event3)
    })

    expect(debugSpy).not.toHaveBeenCalled()

    debugSpy.mockRestore()
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

  it('cleans up recognition handlers on unmount', () => {
    const { result, unmount } = renderHook(() => useVoiceCommands())

    act(() => {
      result.current.startListening()
    })

    expect(recognitionInstance.onend).toBeDefined()
    expect(recognitionInstance.onresult).toBeDefined()

    unmount()

    expect(recognitionInstance.stop).toHaveBeenCalledTimes(1)
    expect(recognitionInstance.onend).toBeNull()
    expect(recognitionInstance.onresult).toBeNull()
  })
})
