import { useCallback, useEffect, useRef, useState } from 'react'

export function useVoiceCommands() {
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('SpeechRecognition is not supported in this browser.')
  }

  const recognitionRef = useRef<InstanceType<typeof SpeechRecognition> | null>(null)
  const [isListening, setIsListening] = useState(false)

  const processCommand = useCallback((text: string) => {
    // Placeholder for custom voice command processing logic
    console.debug('Recognized voice command:', text)
  }, [])

  useEffect(() => {
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.lang = 'pt-BR'
      recognitionRef.current.interimResults = false
      recognitionRef.current.onresult = (e: SpeechRecognitionResult) => {
        const res: SpeechRecognitionResultList = e.results as SpeechRecognitionResultList
        if (!res || typeof res[Symbol.iterator] !== 'function') return
        Array.from(res).forEach((result: SpeechRecognitionResult) => {
          if (!result || typeof result[Symbol.iterator] !== 'function') return
          Array.from(result).forEach((item: SpeechRecognitionAlternative) => {
            const transcript = item.transcript?.trim().toLowerCase()
            if (transcript) {
              processCommand(transcript)
            }
          })
        })
      }
      recognitionRef.current.onend = () => setIsListening(false)
    }
  }, [processCommand])

  const startListening = useCallback(() => {
    if (isListening || !recognitionRef.current) return
    recognitionRef.current.start()
    setIsListening(true)
  }, [isListening])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }, [setIsListening])

  useEffect(() => {
    return () => {
      const recognition = recognitionRef.current
      if (recognition) {
        // avoid updating state after unmount
        recognition.onend = null
        recognition.onresult = null
        recognition.stop()
      }
    }
  }, [])

  return { isListening, startListening, stopListening, processCommand }
}
