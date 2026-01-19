import React from 'react';
import './ParameterForm.css';

const COLORS = [
  { name: 'Blue', value: '#3498db' },
  { name: 'Red', value: '#e74c3c' },
  { name: 'Green', value: '#2ecc71' },
  { name: 'Orange', value: '#f39c12' },
  { name: 'Purple', value: '#9b59b6' }
];

function ParameterForm({ parameters, onChange, onGenerate, loading }) {
  const handleNumberChange = (e) => {
    const { name, value } = e.target;
    onChange(name, parseFloat(value) || 0);
  };

  const handleColorChange = (name, color) => {
    onChange(name, color);
  };

  const handleSelectChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
  };

  return (
    <div className="parameter-form">
      <h2>Design Parameters</h2>

      <div className="form-section">
        <h3>Box Dimensions (mm)</h3>

        <div className="form-group">
          <label htmlFor="boxLength">Length</label>
          <input
            type="number"
            id="boxLength"
            name="boxLength"
            value={parameters.boxLength}
            onChange={handleNumberChange}
            min="50"
            max="400"
            step="10"
          />
        </div>

        <div className="form-group">
          <label htmlFor="boxWidth">Width</label>
          <input
            type="number"
            id="boxWidth"
            name="boxWidth"
            value={parameters.boxWidth}
            onChange={handleNumberChange}
            min="50"
            max="400"
            step="10"
          />
        </div>

        <div className="form-group">
          <label htmlFor="boxHeight">Height</label>
          <input
            type="number"
            id="boxHeight"
            name="boxHeight"
            value={parameters.boxHeight}
            onChange={handleNumberChange}
            min="50"
            max="400"
            step="10"
          />
        </div>
      </div>

      <div className="form-section">
        <h3>Technical Parameters</h3>

        <div className="form-group">
          <label htmlFor="wallThickness">Wall Thickness (mm)</label>
          <input
            type="number"
            id="wallThickness"
            name="wallThickness"
            value={parameters.wallThickness}
            onChange={handleNumberChange}
            min="2"
            max="10"
            step="0.5"
          />
        </div>

        <div className="form-group">
          <label htmlFor="threadDiameter">Thread Diameter (mm)</label>
          <input
            type="number"
            id="threadDiameter"
            name="threadDiameter"
            value={parameters.threadDiameter}
            onChange={handleNumberChange}
            min="10"
            max="25"
            step="1"
          />
        </div>

        <div className="form-group">
          <label htmlFor="scraperBaseSize">Scraper Base Size (mm)</label>
          <input
            type="number"
            id="scraperBaseSize"
            name="scraperBaseSize"
            value={parameters.scraperBaseSize}
            onChange={handleNumberChange}
            min="20"
            max="40"
            step="0.1"
          />
        </div>

        <div className="form-group">
          <label htmlFor="spoutPosition">Drain Spout Position</label>
          <select
            id="spoutPosition"
            name="spoutPosition"
            value={parameters.spoutPosition}
            onChange={handleSelectChange}
            className="position-select"
          >
            <option value="left">Left Side</option>
            <option value="right">Right Side</option>
            <option value="rear">Rear</option>
          </select>
        </div>
      </div>

      <div className="form-section">
        <h3>Colors</h3>

        <div className="form-group">
          <label>Box Color</label>
          <div className="color-picker">
            {COLORS.map(color => (
              <button
                key={`box-${color.value}`}
                className={`color-swatch ${parameters.boxColor === color.value ? 'selected' : ''}`}
                style={{ backgroundColor: color.value }}
                onClick={() => handleColorChange('boxColor', color.value)}
                title={color.name}
                type="button"
              />
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Lid Color</label>
          <div className="color-picker">
            {COLORS.map(color => (
              <button
                key={`lid-${color.value}`}
                className={`color-swatch ${parameters.lidColor === color.value ? 'selected' : ''}`}
                style={{ backgroundColor: color.value }}
                onClick={() => handleColorChange('lidColor', color.value)}
                title={color.name}
                type="button"
              />
            ))}
          </div>
        </div>
      </div>

      <button
        className="generate-button"
        onClick={onGenerate}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Create'}
      </button>
    </div>
  );
}

export default ParameterForm;
