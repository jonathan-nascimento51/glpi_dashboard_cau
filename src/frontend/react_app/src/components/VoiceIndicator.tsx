import type { FC } from 'react'

interface Props {
  isListening: boolean
}

const VoiceIndicator: FC<Props> = ({ isListening }) => (
  <div className={`voice-indicator show ${isListening ? 'listening' : ''}`}>
    <i className="fas fa-microphone" aria-hidden="true" />
  </div>
)

export default VoiceIndicator
