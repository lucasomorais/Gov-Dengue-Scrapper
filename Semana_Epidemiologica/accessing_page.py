# accessing_page.py

from playwright.sync_api import TimeoutError
import time

def accept_cookies(page):
    """Accept cookies if the button is visible."""
    if page.locator("button.btn-accept").is_visible(timeout=5000):
        page.locator("button.btn-accept").click()
        print("Cookies accepted")
    else:
        print("No cookies banner found")

def wait_for_page_load(page):
    """Wait for the page to fully load."""
    page.wait_for_load_state("networkidle")
    print("Page loaded")

def scroll_down(page, pixels=200):
    """Scroll down the page by a specified number of pixels."""
    page.mouse.wheel(0, pixels)
    print(f"Scrolled down by {pixels} pixels")

def access_iframe(page, iframe_selector="iframe[title='Sala Nacional de Arboviroses - SNA']"):
    """Access the iframe and return the frame locator."""
    frame_locator = page.frame_locator(iframe_selector)
    frame_locator.locator("body").wait_for(state="visible", timeout=15000)
    print("Iframe accessed")
    return frame_locator

def select_dengue_panel(frame_locator):
    """Select the Dengue panel within the iframe."""
    dengue_element = frame_locator.get_by_role("group", name="Page navigation . Exibir painel de Dengue").locator("path").first
    dengue_element.wait_for(state="visible", timeout=10000)
    dengue_element.scroll_into_view_if_needed()
    dengue_element.click(delay=100)
    print("Dengue panel selected")
    time.sleep(2)  # Wait for the UI to update