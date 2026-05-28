/**
 * interaction_helpers.js
 * DOM-aware browser interaction helpers for ATS automation
 * Last updated: 2026-05-29
 *
 * ══════════════════════════════════════════════════════════════
 * PRIME DIRECTIVE — READ THIS FIRST
 * ══════════════════════════════════════════════════════════════
 * Act like a human. Use these helpers ONLY when human-style
 * interaction has visibly failed (wrong value shown on screen,
 * field still empty, dropdown still closed).
 *
 * ALWAYS try first:
 *   1. find() → form_input / computer left_click / computer type
 *   2. scroll_to element → click → type
 *   3. Take a screenshot and verify the result visually
 *
 * ONLY fall back to JS helpers when the page doesn't respond to
 * direct interaction (e.g. React state not updating, Select2
 * autocomplete fields, ARIA-only components).
 *
 * Tier order:
 *   1. Native Chrome MCP (find, form_input, left_click, type)   ← ALWAYS FIRST
 *   2. Label-aware click (clickRadioByLabel, clickButtonByText)
 *   3. Focus-and-retry (focusAndType)
 *   4. DOM-aware React helpers (setReactInputValue, selectDropdownOption)
 *   5. Select2 autocomplete helper (fillSelect2Field)           ← last resort for autocomplete
 * ══════════════════════════════════════════════════════════════
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

// ─────────────────────────────────────────────────────────────
// "ADD ANOTHER" BUTTON DETECTION AND CLICKING
// ─────────────────────────────────────────────────────────────

/**
 * Find all "Add Another" / "Add More" buttons on the current page.
 * Returns a list of {text, element} objects so the caller can decide
 * which section to expand.
 * @returns {{ text: string, el: Element }[]}
 */
function findAddAnotherButtons() {
  const keywords = ['add another', 'add more', 'add a', '+ add', 'add entry', 'add education', 'add experience', 'add work'];
  const candidates = [...document.querySelectorAll(
    'button, [role="button"], a, input[type="button"], input[type="submit"], span[tabindex]'
  )];
  return candidates
    .filter(el => {
      const txt = (el.innerText || el.value || '').trim().toLowerCase();
      return keywords.some(k => txt.includes(k));
    })
    .map(el => ({ text: (el.innerText || el.value || '').trim(), el }));
}

/**
 * Click an "Add Another" button for a specific section.
 * @param {string} sectionHint - Partial keyword like "education", "experience", "work"
 * @returns {boolean} true if button found and clicked
 */
function clickAddAnother(sectionHint) {
  const buttons = findAddAnotherButtons();
  if (buttons.length === 0) return false;

  // If hint given, prefer matching button
  if (sectionHint) {
    const match = buttons.find(b =>
      b.text.toLowerCase().includes(sectionHint.toLowerCase())
    );
    if (match) { match.el.click(); return true; }
  }

  // Fall back to first available
  buttons[0].el.click();
  return true;
}

/**
 * Count how many entry rows currently exist in a repeating section.
 * Useful for verifying that "Add Another" created a new row.
 * @param {string} sectionHint - CSS class fragment or label text to scope the count
 * @returns {number}
 */
function countSectionRows(sectionHint) {
  // Try common patterns: fieldset groups, repeated container divs
  const patterns = [
    `[class*="${sectionHint}"]`,
    `[id*="${sectionHint}"]`,
    `[data-section*="${sectionHint}"]`
  ];
  for (const pattern of patterns) {
    try {
      const els = document.querySelectorAll(pattern);
      if (els.length > 0) return els.length;
    } catch {}
  }
  return -1; // unknown
}

/**
 * Scan the page for ALL "Add Another" style buttons and return a
 * plain-text summary. Use this at the start of each form section
 * to avoid missing expandable rows.
 * @returns {string}
 */
function auditAddAnotherButtons() {
  const found = findAddAnotherButtons();
  if (found.length === 0) return 'No "Add Another" buttons found on this page.';
  return 'Found ' + found.length + ' Add Another button(s): ' +
    found.map(b => '"' + b.text + '"').join(', ');
}

// ─────────────────────────────────────────────────────────────
// SELECT2 AUTOCOMPLETE HELPER (last resort — Taleo and similar)
// ─────────────────────────────────────────────────────────────

/**
 * Fill a Select2 autocomplete field by container class suffix.
 * Only use this when clicking directly on the field and typing
 * does not open the autocomplete dropdown.
 *
 * How to find containerId:
 *   document.querySelectorAll('[role="combobox"]') → look at className
 *   for "select2Container{id}" → id is the containerId
 *
 * @param {string} containerId - e.g. "6074-1-sample" from class "select2Container6074-1-sample"
 * @param {string} searchText  - text to search for (e.g. "Miami University")
 * @returns {boolean} true if option was selected
 */
function fillSelect2Field(containerId, searchText) {
  // 1. Open the dropdown
  const span = document.querySelector(`.select2Container${containerId}`);
  if (!span) return false;
  span.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));

  // 2. Type into the search box
  const searchInput = document.querySelector('.select2-search__field');
  if (!searchInput) return false;
  searchInput.focus();
  searchInput.value = searchText;
  searchInput.dispatchEvent(new Event('input', { bubbles: true }));
  searchInput.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));

  // 3. Click the first matching option (synchronous — Taleo list loads immediately)
  const option = document.querySelector('.select2-results__option');
  if (!option) return false;
  option.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true, view: window }));
  option.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, isPrimary: true, view: window }));
  option.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, button: 0, buttons: 1, view: window }));
  option.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, isPrimary: true, view: window }));
  option.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, button: 0, view: window }));
  option.dispatchEvent(new MouseEvent('click', { bubbles: true, button: 0, view: window }));

  // 4. Verify
  const rendered = document.querySelector(`#select2-${containerId}-container`);
  const selected = rendered ? rendered.textContent.replace('×', '').trim() : '';
  return selected.toLowerCase().includes(searchText.toLowerCase());
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
    findAddAnotherButtons,
    clickAddAnother,
    countSectionRows,
    auditAddAnotherButtons,
    fillSelect2Field,
  };
}
