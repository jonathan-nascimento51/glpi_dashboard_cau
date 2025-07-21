import { type FC, useState } from 'react';

// A placeholder for an icon component
const GearIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    fill="currentColor"
    viewBox="0 0 16 16"
  >
    <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z" />
    <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z" />
  </svg>
);

/**
 * This component demonstrates fixes for several accessibility issues:
 * 1. `Buttons must have discernible text`: The icon-only settings button has an `aria-label`.
 * 2. `Select element must have an accessible name`: The <select> is linked to a <label>.
 * 3. `A form field element should have an id or name attribute`: All fields have `id` and `name`.
 * 4. `Certain ARIA roles must contain particular children`: A custom radio group is correctly structured.
 */
export const ReportOptions: FC = () => {
  const [format, setFormat] = useState('pdf');

  return (
    <form
      onSubmit={(e) => e.preventDefault()}
      className="report-options-form"
      style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '300px' }}
    >
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <label htmlFor="report-period-select">Report Period</label>
        <select id="report-period-select" name="report_period">
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      <fieldset>
        <legend id="format-group-label">File Format</legend>
        <div role="radiogroup" aria-labelledby="format-group-label">
          {['pdf', 'csv'].map((fileFormat) => (
            <label key={fileFormat} style={{ marginRight: '1rem' }}>
              <input
                type="radio"
                name="format"
                value={fileFormat}
                checked={format === fileFormat}
                onChange={() => setFormat(fileFormat)}
              />
              {fileFormat.toUpperCase()}
            </label>
          ))}
        </div>
      </fieldset>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button type="submit">Apply</button>
        <button type="button" aria-label="Advanced Settings">
          <GearIcon />
        </button>
      </div>
    </form>
  );
};
