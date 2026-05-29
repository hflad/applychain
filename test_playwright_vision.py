from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "http://localhost:9222"
    )

    for context in browser.contexts:
        for page in context.pages:
            print(page.title())
            print(page.url)

            page.screenshot(path="playwright_test.png")

            print("Screenshot saved")
            raise SystemExit
