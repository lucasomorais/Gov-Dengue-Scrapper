from playwright.sync_api import sync_playwright, TimeoutError
import yaml
import time

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
            select_all_locator = frame.get_by_text("Select all")
            select_all_locator.wait_for(state="visible", timeout=10000)
            select_all_locator.click()
            print("Checked 'Select all'")
            time.sleep(1)  # Brief wait for UI to settle

            # Function to get all menu items in SEM_PRI_SE
            def get_menu_items():
                items = frame.locator("div.slicer-dropdown-popup div.slicerItemContainer").all()
                # Filter for items with numeric titles (weeks)
                return [item for item in items if item.get_attribute("title") and item.get_attribute("title").strip().isdigit()]

            # Iterative scrolling to the last visible item
            max_iterations = 10
            iteration = 0
            previous_count = 0
            last_element_title = None

            while iteration < max_iterations:
                menu_items = get_menu_items()
                current_count = len(menu_items)

                if current_count == 0:
                    print("No items found in dropdown.")
                    break

                if current_count == previous_count and current_count > 0:
                    print(f"No new items found. Total items: {current_count}")
                    last_element_title = menu_items[-1].get_attribute("title").strip()
                    print(f"Last epidemiological week identified: {last_element_title}")
                    # Check if week 12 is visible as a final validation
                    week_12_locator = frame.locator("span").filter(has_text="12")
                    if week_12_locator.is_visible(timeout=5000):
                        print("Week 12 is visible, confirming last week.")
                        last_element_title = "12"
                    break

                if menu_items:
                    last_item = menu_items[-1]
                    last_title = last_item.get_attribute("title").strip()
                    print(f"Scrolling to item {current_count}: {last_title}")
                    last_item.scroll_into_view_if_needed()
                    time.sleep(2)  # Increased wait for lazy loading

                menu_items = get_menu_items()
                previous_count = current_count
                iteration += 1

            # Debug: Print all weeks found
            all_weeks = [item.get_attribute("title").strip() for item in menu_items]
            print(f"All weeks found: {all_weeks}")

            # Fetch data with "Select all" checked
            if last_element_title:
                time.sleep(3)  # Wait for UI to update with all data
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
                output_dir = "Informe_Semana_Epidemiologica/output"
                os.makedirs(output_dir, exist_ok=True)
                with open(f"{output_dir}/SE-Y.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(sem_data, f, allow_unicode=True, default_flow_style=False)
                print("Data saved to SE-Y.yaml")

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
    import os
    main()