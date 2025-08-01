// filepath: src/frontend/react_app/src/global.d.ts
declare module '*.module.css';
declare module 'react-calendar-heatmap';
declare module 'react-window' {
  export interface ListChildComponentProps<T> {
    index: number
    style: React.CSSProperties
    data: T
  }
  export const FixedSizeList: React.ComponentType<unknown>
}

interface Window {
  webkitSpeechRecognition: typeof SpeechRecognition
  SpeechRecognition: typeof SpeechRecognition
}
