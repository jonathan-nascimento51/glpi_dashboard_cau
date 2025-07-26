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
      const transcript = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join(' ')
      processCommand(transcript.trim().toLowerCase())
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
      recognitionRef.current?.stop()
    }
  }, [])

  return { isListening, startListening, stopListening, processCommand }
}
