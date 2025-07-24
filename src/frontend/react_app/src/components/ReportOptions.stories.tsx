import type { Meta, StoryObj } from '@storybook/react'
import { userEvent, within, expect } from '@storybook/test'
import { ReportOptions } from './ReportOptions'

const meta: Meta<typeof ReportOptions> = {
  title: 'Components/ReportOptions',
  component: ReportOptions,
  parameters: {
    // Opcional: centraliza o componente na tela do Storybook.
    layout: 'centered',
  },
  tags: ['autodocs'], // Habilita a geração automática de documentação.
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: 'Default View & Interactions',
  play: async ({ canvasElement, step }) => {
    const canvas = within(canvasElement)

    // É uma boa prática buscar todos os elementos no início da função `play`.
    const periodSelect =
      await canvas.findByLabelText<HTMLSelectElement>('Report Period')
    const pdfRadio = await canvas.findByLabelText('PDF')
    const csvRadio = await canvas.findByLabelText('CSV')
    const settingsButton = await canvas.findByRole('button', {
      name: /advanced settings/i,
    })

    await step('Verifica o estado inicial e a acessibilidade', async () => {
      // Garante que o componente renderiza com os valores padrão corretos.
      await expect(periodSelect.value).toBe('weekly')
      await expect(pdfRadio).toBeChecked()
      await expect(csvRadio).not.toBeChecked()
      // Garante que o botão de ícone tem um nome acessível.
      await expect(settingsButton).toBeInTheDocument()
    })

    await step('Muda o formato do arquivo para CSV', async () => {
      await userEvent.click(csvRadio)
      await expect(csvRadio).toBeChecked()
      await expect(pdfRadio).not.toBeChecked()
    })

    await step('Muda o período do relatório para Mensal', async () => {
      await userEvent.selectOptions(periodSelect, 'monthly')
      await expect(periodSelect.value).toBe('monthly')
    })
  },
}
