import type { Meta, StoryObj } from '@storybook/react'
import { spyOn } from '@storybook/test'
import { ChamadosBarChart } from './ChamadosBarChart'
import * as useChamadosPorDataHook from '../hooks/useChamadosPorData'

const meta: Meta<typeof ChamadosBarChart> = {
  title: 'Charts/ChamadosBarChart',
  component: ChamadosBarChart,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
  // Este decorator será aplicado a todas as histórias deste componente.
  // Ele intercepta o hook `useChamadosPorData` e usa os dados fornecidos
  // nos `parameters` de cada história.
  decorators: [
    (Story, context) => {
      const { mockData } = context.parameters
      if (mockData) {
        spyOn(useChamadosPorDataHook, 'useChamadosPorData').mockReturnValue({
          ...mockData,
        } as any)
      }
      return <Story />
    },
  ],
}

export default meta
type Story = StoryObj<typeof meta>

const mockData = [
  { date: '2024-07-01', total: 12 },
  { date: '2024-07-02', total: 19 },
  { date: '2024-07-03', total: 3 },
  { date: '2024-07-04', total: 5 },
  { date: '2024-07-05', total: 8 },
  { date: '2024-07-06', total: 2 },
  { date: '2024-07-07', total: 15 },
]

export const Default: Story = {
  name: 'Com Dados',
  parameters: {
    mockData: {
      data: mockData,
      isLoading: false,
      isError: false,
      error: null,
    },
  },
}

export const Loading: Story = {
  name: 'Carregando',
  parameters: {
    mockData: {
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    },
  },
}

export const WithError: Story = {
  name: 'Com Erro',
  parameters: {
    mockData: {
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Falha ao buscar dados da API'),
    },
  },
}
