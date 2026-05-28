/**
 * interaction_helpers.js
 * DOM-aware browser interaction helpers for ATS automation
 * Last updated: 2026-05-28
 *
 * USAGE: Inject via mcp__Claude_in_Chrome__javascript_tool when native interactions fail.
 * These are FALLBACK helpers — always try native Chrome MCP interactions first.
 * Only escalate to these when standard click/type/form_input fails visibly.
 *
 * Tier order:
 *   1. Native Chrome MCP (click, type, form_input)
 *   2. Label-aware click (clickRadioByLabel, clickButtonByText)
 *   3. Focus-and-retry (focusAndType)
 *   4. DOM-aware React helpers (setReactInputValue, selectDropdownOption)
 */

// ─────────────────────────────────────────────────────────────
// TIER 2 — LABEL-AWARE RADIO INTERACTION
// ─────────────────────────────────────────────────────────────

/**
 * Click a radio button by matching its label text.
 * Prefers clicking the label (larger target) over the input itself.
 * @param {string} text - Partial or full label text to match (case-insensitive)
 * @returns {boolean} true if found and clicked, false if not found
 */
function clickRadioByLabel(text) {
  const labels = [...document.querySelectorAll('label')];
  const match = labels.find(l =>
    l.innerText.toLowerCase().includes(text.toLowerCase())
  );
  if (match) {
    match.click();
    return verifyRadioSelected(text);
  }
  // Fallback: try input[type=radio] with adjacent text
  const radios = [...document.querySelectorAll('input[type="radio"]')];
  for (const radio of radios) {
    const parent = radio.closest('label, [role="radio"]') || radio.parentElement;
    if (parent && parent.innerText.toLowerCase().includes(text.toLowerCase())) {
      radio.click();
      return verifyRadioSelected(text);
    }
  }
  return false;
}

/**
 * Verify a radio button is actually selected after clicking.
 * @param {string} labelText - Label text of the radio to verify
 * @returns {boolean}
 */
function verifyRadioSelected(labelText) {
  const labels = [...document.querySelectorAll('label')];
  const match = labels.find(l =>
    l.innerText.toLowerCase().includes(labelText.toLowerCase())
  );
  if (!match) return false;
  const input = match.querySelector('input[type="radio"]') ||
    document.getElementById(match.htmlFor);
  return input ? input.checked : false;
}

/**
 * Click any button or clickable element by its visible text.
 * @param {string} text - Button text (case-insensitive partial match)
 * @returns {boolean}
 */
function clickButtonByText(text) {
  const els = [...document.querySelectorAll('button, [role="button"], a, input[type="submit"]')];
  const match = els.find(el =>
    el.innerText?.toLowerCase().includes(text.toLowerCase()) ||
    el.value?.toLowerCase().includes(text.toLowerCase())
  );
  if (match) { match.click(); return true; }
  return false;
}

// ─────────────────────────────────────────────────────────────
// TIER 3 — FOCUS AND TYPE (for React text inputs)
// ─────────────────────────────────────────────────────────────

/**
 * Focus a text input by label text and type a value using React-compatible events.
 * Use when form_input sets DOM value but React state doesn't update.
 * @param {string} labelText - Label text of the field
 * @param {string} value - Value to type
 * @returns {boolean}
 */
function focusAndType(labelText, value) {
  const labels = [...document.querySelectorAll('label')];
  const label = labels.find(l =>
    l.innerText.toLowerCase().includes(labelText.toLowerCase())
  );
  let input = null;
  if (label) {
    input = label.querySelector('input, textarea') ||
      document.getElementById(label.htmlFor);
  }
  if (!input) {
    // Try placeholder match
    input = document.querySelector(`input[placeholder*="${labelText}"], textarea[placeholder*="${labelText}"]`);
  }
  if (!input) return false;

  input.focus();
  input.click();
  setReactInputValue(input, value);
  return true;
}

// ─────────────────────────────────────────────────────────────
// TIER 4 — REACT-AWARE FIELD SETTERS
// ─────────────────────────────────────────────────────────────

/**
 * Set value on a React-controlled input, firing the synthetic events
 * React needs to recognize the change.
 * @param {HTMLInputElement|HTMLTextAreaElement} input - DOM input element
 * @param {string} value - Value to set
 */
function setReactInputValue(input, value) {
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  )?.set;
  const nativeTextareaSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype, 'value'
  )?.set;

  const setter = input.tagName === 'TEXTAREA' ? nativeTextareaSetter : nativeInputValueSetter;
  if (setter) {
    setter.call(input, value);
  } else {
    input.value = value;
  }

  // Fire events React listens to
  input.dispatchEvent(new Event('input',  { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent('keydown',  { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent('keypress', { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent('keyup',    { bubbles: true }));
}

/**
 * Select an option in a React/ARIA combobox dropdown by label + option text.
 * Supports both [role="combobox"] and native <select>.
 * @param {string} labelText - Label text of the dropdown field
 * @param {string} optionText - Visible text of the option to select
 * @param {number} [waitMs=600] - How long to wait for dropdown to open
 * @returns {Promise<boolean>}
 */
async function selectDropdownOption(labelText, optionText, waitMs = 600) {
  const labels = [...document.querySelectorAll('label')];
  const label = labels.find(l =>
    l.innerText.toLowerCase().includes(labelText.toLowerCase())
  );

  let trigger = null;
  if (label) {
    trigger = label.querySelector('[role="combobox"], select, input') ||
      document.getElementById(label.htmlFor);
  }
  if (!trigger) {
    // Try aria-label or placeholder
    trigger = document.querySelector(
      `[aria-label*="${labelText}"], [placeholder*="${labelText}"]`
    );
  }
  if (!trigger) return false;

  // Handle native <select>
  if (trigger.tagName === 'SELECT') {
    const opt = [...trigger.options].find(o =>
      o.text.toLowerCase().includes(optionText.toLowerCase())
    );
    if (opt) {
      trigger.value = opt.value;
      trigger.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    }
    return false;
  }

  // Handle React combobox
  trigger.click();
  trigger.focus();

  await new Promise(r => setTimeout(r, waitMs));

  const options = [...document.querySelectorAll('[role="option"], [role="listitem"], li')];
  const option = options.find(o =>
    o.innerText?.toLowerCase().includes(optionText.toLowerCase())
  );
  if (option) {
    option.click();
    // Verify after short delay
    await new Promise(r => setTimeout(r, 300));
    return verifyDropdownValue(labelText, optionText);
  }
  return false;
}

/**
 * Verify a dropdown/combobox shows the expected value after selection.
 * @param {string} labelText - Label text of the field
 * @param {string} expectedValue - Expected visible value
 * @returns {boolean}
 */
function verifyDropdownValue(labelText, expectedValue) {
  const labels = [...document.querySelectorAll('label')];
  const label = labels.find(l =>
    l.innerText.toLowerCase().includes(labelText.toLowerCase())
  );
  if (!label) return false;
  const container = label.closest('[class*="field"], [class*="form"], div') || label.parentElement;
  return container?.innerText.toLowerCase().includes(expectedValue.toLowerCase()) ?? false;
}

// ─────────────────────────────────────────────────────────────
// VERIFICATION UTILITIES
// ─────────────────────────────────────────────────────────────

/**
 * Verify a text input contains the expected value.
 * @param {string} labelText
 * @param {string} expectedValue
 * @returns {boolean}
 */
function verifyInputValue(labelText, expectedValue) {
  const labels = [...document.querySelectorAll('label')];
  const label = labels.find(l =>
    l.innerText.toLowerCase().includes(labelText.toLowerCase())
  );
  if (!label) return false;
  const input = label.querySelector('input, textarea') ||
    document.getElementById(label.htmlFor);
  return input?.value?.toLowerCase().includes(expectedValue.toLowerCase()) ?? false;
}

/**
 * Scan the current page for unfilled required fields.
 * Returns array of field labels that appear empty/unset.
 * @returns {string[]}
 */
function findEmptyRequiredFields() {
  const empty = [];
  // Required inputs
  document.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
    if (!el.value) {
      const label = document.querySelector(`label[for="${el.id}"]`);
      empty.push(label?.innerText || el.name || el.placeholder || '(unknown field)');
    }
  });
  // ARIA required
  document.querySelectorAll('[aria-required="true"]').forEach(el => {
    if (!el.value && !el.innerText?.trim()) {
      empty.push(el.getAttribute('aria-label') || el.id || '(aria-required field)');
    }
  });
  return empty;
}

// Export for reference in console
if (typeof module !== 'undefined') {
  module.exports = {
    clickRadioByLabel,
    verifyRadioSelected,
    clickButtonByText,
    focusAndType,
    setReactInputValue,
    selectDropdownOption,
    verifyDropdownValue,
    verifyInputValue,
    findEmptyRequiredFields,
  };
}
