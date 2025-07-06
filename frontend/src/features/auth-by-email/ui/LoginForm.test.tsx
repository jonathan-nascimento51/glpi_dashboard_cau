import { render, screen, fireEvent } from '@testing-library/react'
import { LoginForm } from './LoginForm'
import { useUserStore } from '@/entities/user'

jest.mock('@/entities/user', () => ({
  useUserStore: jest.fn(),
}))

describe('LoginForm', () => {
  it('submits email and calls setUser', () => {
    const setUser = jest.fn()
  ;(useUserStore as unknown as jest.Mock).mockReturnValue({ setUser })
    render(<LoginForm />)
    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' },
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    expect(setUser).toHaveBeenCalledWith({ id: '1', email: 'test@example.com' })
  })
})
