from playwright.sync_api import sync_playwright, TimeoutError
import yaml
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Run in non-headless mode for debugging
        page = browser.new_page()
        page.goto("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses")
        
        if page.locator("button.btn-accept").is_visible(timeout=5000):
            page.locator("button.btn-accept").click()
            print("Cookies accepted")
        
        page.wait_for_load_state("networkidle")
        print("Page loaded")

        try:
            # Access the iframe
            frame_locator = page.frame_locator("iframe[title='Sala Nacional de Arboviroses - SNA']")
            frame = frame_locator
            frame.locator("body").wait_for(state="visible", timeout=15000)
            print("Iframe accessed")

            # Select the Dengue panel
            dengue_element = frame.get_by_role("group").filter(has_text="Dengue").locator("path").first
            dengue_element.wait_for(state="visible", timeout=10000)
            dengue_element.scroll_into_view_if_needed()
            dengue_element.click(delay=100)
            print("Dengue panel selected")

            # Target the SEM_PRI_SE dropdown
            dropdown = frame.locator("div.slicer-dropdown-menu[aria-label='SEM_PRI_SE']")
            dropdown.wait_for(state="visible", timeout=10000)
            dropdown.click()
            print("SEM_PRI_SE dropdown opened")

            # Immediately select "Select all"
            select_all_locator = page.locator("iframe[title='Sala Nacional de Arboviroses - SNA']").content_frame.get_by_text("Select all")
            select_all_locator.wait_for(state="visible", timeout=10000)
            select_all_locator.click()
            print("Checked 'Select all'")
            time.sleep(1)  # Brief wait for UI to settle

            # Function to get all menu items in SEM_PRI_SE
            def get_menu_items():
                return frame.locator("div.slicer-dropdown-popup div.slicerItemContainer").all()

            # Scroll through the dropdown to find the last element
            previous_count = 0
            menu_items = get_menu_items()
            max_iterations = 10
            iteration = 0
            last_element_title = None

            while iteration < max_iterations:
                current_count = len(menu_items)
                if current_count == previous_count and current_count > 0:
                    print(f"No new items found. Total items: {current_count}")
                    last_element_title = menu_items[-1].get_attribute("title").strip()
                    print(f"Last epidemiological week identified: {last_element_title}")
                    break

                if menu_items:
                    last_item = menu_items[-1]
                    last_item.scroll_into_view_if_needed()
                    print(f"Scrolled to item {current_count}: {last_item.text_content()}")
                    time.sleep(1)  # Wait for lazy loading

                menu_items = get_menu_items()
                previous_count = current_count
                iteration += 1

            # Fetch data with "Select all" checked
            if last_element_title:
                # Wait for the UI to update with all data
                time.sleep(3)
                frame.locator("svg.card").first.wait_for(state="visible", timeout=15000)

                sem_data = {
                    "Last_Epidemiological_Week": last_element_title,
                    "All_Semanas": {}
                }
                svg_cards = frame.locator("svg.card").all()

                for card in svg_cards:
                    aria_label = card.get_attribute("aria-label")
                    value = card.locator("text.value tspan").text_content()
                    if aria_label and value:
                        sem_data["All_Semanas"][aria_label] = value

                # Save data to YAML
                with open("Semana_Epidemiologica/output/SE-Y.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(sem_data, f, allow_unicode=True, default_flow_style=False)
                print("Data saved to dengue_sem_data.yaml")

            else:
                print("No last element identified within iteration limit.")
                page.pause()

        except TimeoutError as e:
            print(f"Timeout error: {e}")
            page.pause()
        except Exception as e:
            print(f"An error occurred: {e}")
            page.pause()
        finally:
            browser.close()

if __name__ == "__main__":
    main()