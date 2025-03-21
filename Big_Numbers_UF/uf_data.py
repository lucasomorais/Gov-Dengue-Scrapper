from playwright.sync_api import sync_playwright, TimeoutError
import yaml
import time

class DropdownManager:
    def __init__(self, frame_locator, dropdown_selector):
        self.frame_locator = frame_locator
        self.dropdown = frame_locator.locator(dropdown_selector)
    
    def ensure_open(self, timeout=5000):
        """Ensure the dropdown is open, reopening if necessary."""
        if self.dropdown.get_attribute("aria-expanded") != "true":
            self.dropdown.click(delay=100)
            self.frame_locator.locator("div.slicer-dropdown-popup").wait_for(state="visible", timeout=timeout)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Run in non-headless mode for debugging
        page = browser.new_page()
        page.goto("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses")
        
        if page.locator("button.btn-accept").is_visible(timeout=5000):
            page.locator("button.btn-accept").click()
            print("Cookies accepted")
        
        page.wait_for_load_state("networkidle")
        print("Page loaded")

        try:
            frame_locator = page.frame_locator("iframe[title='Sala Nacional de Arboviroses - SNA']")
            frame_locator.locator("body").wait_for(state="visible", timeout=15000)
            print("Iframe accessed")

            dengue_element = frame_locator.get_by_role("group").filter(has_text="Dengue").locator("path").first
            dengue_element.wait_for(state="visible", timeout=10000)
            dengue_element.scroll_into_view_if_needed()
            dengue_element.click(delay=100)
            print("Dengue panel selected")

            dropdown = frame_locator.locator("div.slicer-dropdown-menu[aria-label='UF']")
            dropdown.wait_for(state="visible", timeout=5000)
            dropdown.click()
            print("UF dropdown opened")

            dropdown_manager = DropdownManager(frame_locator, "div.slicer-dropdown-menu[aria-label='UF']")
            dropdown_manager.ensure_open()
            page.wait_for_timeout(500)

            uf_data = {}
            processed_ufs = set()  # Track processed UFs to avoid duplicates

            while True:
                # Get all visible UFs
                uf_items = frame_locator.locator("div.slicerItemContainer").all()
                uf_names = [item.get_attribute("title").strip() for item in uf_items if item.get_attribute("title").strip().lower() != "select all"]

                # Filter out already processed UFs
                new_ufs = [uf for uf in uf_names if uf not in processed_ufs]
                if not new_ufs:
                    break  # Exit if no new UFs are found

                for uf_name in new_ufs:
                    # Reopen dropdown to ensure it's visible
                    dropdown_manager.ensure_open()
                    page.wait_for_timeout(1000)  # Wait for dropdown to fully open

                    # Locate the UF item by its title
                    item = frame_locator.locator(f"div.slicerItemContainer[title='{uf_name}']")
                    item.scroll_into_view_if_needed()
                    item.wait_for(state="visible", timeout=5000)

                    # Ensure only this UF is selected
                    if item.get_attribute("aria-selected") != "true":
                        item.click()
                        print(f"Checked UF: {uf_name}")

                    # Wait for the UI to update
                    time.sleep(3)  # Fixed delay to ensure UI updates
                    frame_locator.locator("svg.card").first.wait_for(state="visible", timeout=15000)

                    # Fetch data
                    svg_cards = frame_locator.locator("svg.card").all()
                    uf_data[uf_name] = {}

                    for card in svg_cards:
                        aria_label = card.get_attribute("aria-label")
                        value = card.locator("text.value tspan").text_content()
                        if aria_label and value:
                            label = aria_label.replace(value, "").strip(" .").replace(" - DENV", "")
                            if "Letalidade (óbito)" not in label:
                                uf_data[uf_name][label] = value

                    # Uncheck the UF
                    dropdown_manager.ensure_open()
                    item.scroll_into_view_if_needed()
                    item.wait_for(state="visible", timeout=5000)
                    item.click()

                    # Wait for the UI to reset
                    page.wait_for_timeout(1000)

                    # Mark UF as processed
                    processed_ufs.add(uf_name)

            # Save extracted data to a YAML file
            with open("Big_Numbers_UF/output/dengue_uf_data.yaml", "w", encoding="utf-8") as f:
                yaml.dump(uf_data, f, allow_unicode=True, default_flow_style=False)
            print("Data saved to dengue_uf_data.yaml")

        except TimeoutError as e:
            print(f"Timeout error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        browser.close()

if __name__ == "__main__":
    main()