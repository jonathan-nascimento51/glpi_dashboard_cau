import { useCallback, useEffect, useRef, useState } from 'react'

export function useVoiceCommands() {
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const [isListening, setIsListening] = useState(false)

  const processCommand = useCallback((text: string) => {
    // Placeholder for custom voice command processing logic
    console.debug('Recognized voice command:', text)
  }, [])

  const createRecognition = useCallback(() => {
    const Speech =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!Speech) {
      alert('Reconhecimento de voz não está disponível neste navegador.');
      return null;
    }
    const recognition: SpeechRecognition = new Speech()
    recognition.lang = 'pt-BR'
    recognition.interimResults = false
    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const res: any = e.results
      if (!res || typeof res[Symbol.iterator] !== 'function') return
      Array.from(res).forEach((result: any) => {
        if (!result || typeof result[Symbol.iterator] !== 'function') return
        Array.from(result).forEach((item: any) => {
          const transcript = item?.transcript?.trim().toLowerCase()
          if (transcript) {
            processCommand(transcript)
          }
        })
      })
    }
    recognition.onend = () => setIsListening(false)
    return recognition
  }, [processCommand])

  const startListening = useCallback(() => {
    if (isListening) return
    const recognition = createRecognition()
    if (recognition) {
      recognitionRef.current = recognition
      recognition.start()
      setIsListening(true)
    }
  }, [isListening, createRecognition])

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
