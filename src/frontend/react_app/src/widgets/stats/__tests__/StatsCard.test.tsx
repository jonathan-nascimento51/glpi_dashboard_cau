import { render, screen } from '@testing-library/react'
import { StatsCard } from '../StatsCard'

describe('StatsCard', () => {
  it('renders label and value', () => {
    render(<StatsCard label="Total" value={5} />)
    expect(screen.getByTestId('stats-value')).toHaveTextContent('5')
    expect(screen.getByTestId('stats-label')).toHaveTextContent('Total')
  })
})
