import type { Meta, StoryObj } from '@storybook/react'
import { within, userEvent, expect } from '@storybook/test'
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

    await step('Verifica o estado inicial do formulário', async () => {
      const periodSelect =
        await canvas.findByLabelText<HTMLSelectElement>('Report Period')
      const pdfRadio = await canvas.findByLabelText('PDF')
      const csvRadio = await canvas.findByLabelText('CSV')

      await expect(periodSelect.value).toBe('weekly')
      await expect(pdfRadio).toBeChecked()
      await expect(csvRadio).not.toBeChecked()
    })

    await step('Muda o formato do arquivo para CSV', async () => {
      const csvRadio = await canvas.findByLabelText('CSV')
      await userEvent.click(csvRadio)

      const pdfRadio = await canvas.findByLabelText('PDF')
      await expect(csvRadio).toBeChecked()
      await expect(pdfRadio).not.toBeChecked()
    })

    await step('Muda o período do relatório para Mensal', async () => {
      const periodSelect =
        await canvas.findByLabelText<HTMLSelectElement>('Report Period')
      await userEvent.selectOptions(periodSelect, 'monthly')
      await expect(periodSelect.value).toBe('monthly')
    })
  },
}
