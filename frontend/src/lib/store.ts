import { create } from 'zustand'

interface State {
  apiUrl: string
}

export const useAppStore = create<State>(() => ({
  apiUrl: '',
}))
