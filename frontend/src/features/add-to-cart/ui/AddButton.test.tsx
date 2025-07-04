import { render, screen, fireEvent } from '@testing-library/react'
import { AddButton } from './AddButton'
import { useCartStore } from '../model/cartStore'

jest.mock('../model/cartStore', () => ({
  useCartStore: jest.fn(),
}))

describe('AddButton', () => {
  it('adds item to store on click', () => {
    const addItem = jest.fn()
    ;(useCartStore as jest.Mock).mockImplementation((sel: any) => sel({ addItem }))
    render(<AddButton item="x" />)
    fireEvent.click(screen.getByRole('button'))
    expect(addItem).toHaveBeenCalledWith('x')
  })
})
