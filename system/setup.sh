#!/usr/bin/env bash
# setup.sh — Install playwright_engine dependencies
# Run once from the applychain-workspace root:
#   bash system/playwright_engine/setup.sh

set -e
echo "==> Installing Playwright Python package..."
pip install playwright --break-system-packages 2>/dev/null || pip install playwright

echo "==> Installing Playwright browsers (Chromium only)..."
playwright install chromium

echo ""
echo "==> IMPORTANT: To use CDP mode (attach to your existing Chrome),"
echo "    Chrome must be launched with the remote debugging port."
echo ""
echo "    Quit Chrome first, then run:"
echo ""
echo '    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &'
echo ""
echo "    Or add this as a shell alias:"
echo '    alias chrome-debug="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222"'
echo ""
echo "==> Setup complete. Test with:"
echo "    python -m system.playwright_engine.cli diagnose --tab-url 'https://example.com'"
