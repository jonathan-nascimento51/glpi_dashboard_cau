import type { FC, InputHTMLAttributes } from 'react'

export const Input: FC<InputHTMLAttributes<HTMLInputElement>> = (props) => (
  <input {...props} />
)
