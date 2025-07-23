import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportOptions } from '@/components/ReportOptions';

describe('ReportOptions Component', () => {
  it('should render form elements with accessible names', () => {
    render(<ReportOptions />);

    // Check if the select element is correctly associated with its label
    const periodLabel = screen.getByText('Report Period');
    const periodSelect = screen.getByLabelText('Report Period');
    expect(periodLabel).toBeInTheDocument();
    expect(periodSelect).toBeInTheDocument();
    expect(periodSelect).toHaveAttribute('id', 'report-period-select');
    expect(periodSelect).toHaveAttribute('name', 'report_period');

    // Check if the radio group has an accessible name from the legend
    const radioGroup = screen.getByRole('radiogroup');
    expect(radioGroup).toHaveAccessibleName('File Format');

    // Check individual radio buttons
    const pdfRadio = screen.getByLabelText('PDF');
    expect(pdfRadio).toBeInTheDocument();
    expect(pdfRadio).toHaveAttribute('name', 'format');
    expect(pdfRadio).toHaveAttribute('value', 'pdf');
    expect(pdfRadio).toBeChecked(); // Default value

    const csvRadio = screen.getByLabelText('CSV');
    expect(csvRadio).toBeInTheDocument();
    expect(csvRadio).toHaveAttribute('name', 'format');
    expect(csvRadio).toHaveAttribute('value', 'csv');
    expect(csvRadio).not.toBeChecked();
  });

  it('should have an accessible name for the icon-only settings button', () => {
    render(<ReportOptions />);

    // The button has no visible text, so it must have an aria-label
    const settingsButton = screen.getByRole('button', { name: /advanced settings/i });
    expect(settingsButton).toBeInTheDocument();
    expect(settingsButton).not.toHaveTextContent(); // Ensure it's an icon-only button
  });

  it('should update state when a different radio button is selected', async () => {
    const user = userEvent.setup();
    render(<ReportOptions />);

    const pdfRadio = screen.getByLabelText('PDF');
    const csvRadio = screen.getByLabelText('CSV');

    expect(pdfRadio).toBeChecked();
    expect(csvRadio).not.toBeChecked();

    await user.click(csvRadio);

    expect(pdfRadio).not.toBeChecked();
    expect(csvRadio).toBeChecked();
  });
});
