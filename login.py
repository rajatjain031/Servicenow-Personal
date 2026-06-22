import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def wake_servicenow():
    instance_url = os.environ.get("SN_INSTANCE_URL")  # e.g. https://devXXXXX.service-now.com
    username     = os.environ.get("SN_USERNAME")
    password     = os.environ.get("SN_PASSWORD")

    if not all([instance_url, username, password]):
        print("❌ Missing environment variables: SN_INSTANCE_URL, SN_USERNAME, SN_PASSWORD")
        sys.exit(1)

    print(f"🔗 Connecting to: {instance_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the login page
            page.goto(instance_url, wait_until="networkidle", timeout=60000)
            print("✅ Page loaded")

            # Fill in username
            page.fill("#user_name", username)
            page.fill("#user_password", password)
            print("✅ Credentials entered")

            # Click login button
            page.click("#sysverb_login")

            # Wait for navigation after login
            page.wait_for_load_state("networkidle", timeout=60000)
            print("✅ Login submitted")

            # Check if login was successful by looking for known post-login element
            # ServiceNow redirects to the home page after successful login
            current_url = page.url
            title = page.title()
            print(f"📄 Page title: {title}")
            print(f"🌐 Current URL: {current_url}")

            if "login" in current_url.lower():
                print("❌ Still on login page — check your credentials!")
                browser.close()
                sys.exit(1)
            else:
                print("🎉 Successfully logged in and instance is awake!")

        except PlaywrightTimeoutError:
            print("❌ Timeout — instance may be hibernating or URL is wrong.")
            browser.close()
            sys.exit(1)

        finally:
            browser.close()

if __name__ == "__main__":
    wake_servicenow()
