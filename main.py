from playwright.sync_api import sync_playwright, TimeoutError
import yaml

class DropdownManager:
    def __init__(self, frame_locator, dropdown_selector):
        self.frame_locator = frame_locator
        self.dropdown = frame_locator.locator(dropdown_selector)
    
    def ensure_open(self, timeout=5000):
        """Ensure the dropdown is open, reopening if necessary."""
        if self.dropdown.get_attribute("aria-expanded") != "true":
            self.dropdown.click(delay=100)
            self.frame_locator.locator("div.slicer-dropdown-popup").wait_for(state="visible", timeout=timeout)
        print("Dropdown confirmed open")

def main():
    with sync_playwright() as p:
        # Launch browser in non-headless mode for visibility
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the target page
        page.goto("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses")
        
        # Accept cookies if present
        accept_button = page.locator("button.btn-accept")
        if accept_button.is_visible(timeout=5000):
            accept_button.click()
            print("Cookies accepted")
        
        # Wait for the page to fully load
        page.wait_for_load_state("networkidle")
        print("Page loaded")

        try:
            # Locate the iframe containing the data
            frame_locator = page.frame_locator("iframe[title='Sala Nacional de Arboviroses - SNA']")
            frame_locator.locator("body").wait_for(state="visible", timeout=15000)
            print("Iframe accessed")

            # Click the Dengue panel to display UF options
            dengue_element = frame_locator.get_by_role("group").filter(has_text="Dengue").locator("path").first
            dengue_element.wait_for(state="visible", timeout=10000)
            dengue_element.scroll_into_view_if_needed()
            dengue_element.click(delay=100)
            print("Dengue panel selected")

            # Locate and open the UF dropdown
            dropdown = frame_locator.locator("div.slicer-dropdown-menu[aria-label='UF']")
            dropdown.wait_for(state="visible", timeout=10000)
            dropdown.click()
            print("UF dropdown opened")

            # Get all UF options
            uf_items = frame_locator.locator("div.visibleGroup div.slicerItemContainer").all()
            uf_data = {}
            print(f"Found {len(uf_items)} UF options")

            # Updated UF handler with delay after opening
            dropdown_manager = DropdownManager(frame_locator, "div.slicer-dropdown-menu[aria-label='UF']")
            dropdown_manager.ensure_open()
            page.wait_for_timeout(2000)  # Wait 2 seconds for options to load
            
            # Fetch UF items after delay
            uf_items = frame_locator.locator("div.slicerItemContainer").all()
            print(f"Found {len(uf_items)} UF options with title selector")

            for i, item in enumerate(uf_items):
                # Reopen dropdown for each iteration except the first
                if i > 0:
                    dropdown_manager.ensure_open()
                    page.wait_for_timeout(2000)  # Wait 2 seconds after reopening
                
                uf_name = item.get_attribute("title").strip()
                if uf_name.lower() == "select all" or not uf_name:
                    print(f"Skipping: {uf_name or 'empty'}")
                    continue

                # Ensure item is visible and clickable
                item.scroll_into_view_if_needed()
                item.wait_for(state="visible", timeout=5000)
                
                # Check the UF by clicking
                item.click(delay=100)
                page.wait_for_timeout(1000)
                print(f"Checked UF: {uf_name}")

                # Wait for data to load and extract it
                frame_locator.locator("svg.card").first.wait_for(state="visible", timeout=10000)
                svg_cards = frame_locator.locator("svg.card").all()
                uf_data[uf_name] = {}

                for card in svg_cards:
                    aria_label = card.get_attribute("aria-label")
                    value = card.locator("text.value tspan").text_content()
                    if aria_label and value:
                        label = aria_label.replace(value, "").strip(" .").replace(" - DENV", "")
                        if "Letalidade (óbito)" not in label:
                            uf_data[uf_name][label] = value
                            print(f"  {label}: {value}")

                # Reopen dropdown and uncheck by clicking again
                dropdown_manager.ensure_open()
                page.wait_for_timeout(2000)  # Wait 2 seconds after reopening
                item.click(delay=100)
                page.wait_for_timeout(1000)
                print(f"Unchecked UF: {uf_name}")

            # Save extracted data to a YAML file
            with open("dengue_uf_data.yaml", "w", encoding="utf-8") as f:
                yaml.dump(uf_data, f, allow_unicode=True, default_flow_style=False)
            print("Data saved to dengue_uf_data.yaml")

        except TimeoutError as e:
            print(f"Timeout error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Pause for manual inspection, then close
        page.pause()
        browser.close()

if __name__ == "__main__":
    main()