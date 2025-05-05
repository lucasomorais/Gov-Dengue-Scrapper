from playwright.sync_api import sync_playwright, TimeoutError, Error as PlaywrightError
import yaml
import time
import os

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(25000)

        try:
            print("Navigating to page...")
            page.goto("https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses", wait_until='load')

            cookie_button = page.locator("button.btn-accept")
            try:
                cookie_button.wait_for(state="visible", timeout=10000)
                cookie_button.click()
                print("Cookies accepted.")
            except TimeoutError:
                print("Cookie consent button not found or already accepted.")

            page.wait_for_load_state("networkidle", timeout=35000)
            print("Page loaded and network idle.")

            print("Accessing iframe...")
            frame_locator = page.frame_locator("iframe[title='Sala Nacional de Arboviroses - SNA']")
            frame = frame_locator
            frame.locator("div.visualContainerHost").first.wait_for(state="visible", timeout=35000)
            print("Iframe accessed and initial content visible.")

            print("Selecting Dengue panel...")
            dengue_element_container = frame.locator('div.themableBackgroundColor[role="group"][aria-label="Dengue"]')
            if not dengue_element_container.is_visible(timeout=5000):
                 print("Using fallback selector for Dengue panel")
                 dengue_element_container = frame.get_by_role("group").filter(has_text="Dengue")

            dengue_element_clickable = dengue_element_container.locator("path").first
            dengue_element_clickable.wait_for(state="visible", timeout=15000)
            dengue_element_clickable.scroll_into_view_if_needed()
            time.sleep(0.5)
            dengue_element_clickable.click(force=True, delay=500)
            print("Dengue panel selected.")
            time.sleep(2)

            print("Opening SEM_PRI_SE dropdown (Original Method)...")
            dropdown_button_locator = frame.locator("div.slicer-dropdown-menu[aria-label='SEM_PRI_SE']")
            dropdown_button_locator.wait_for(state="visible", timeout=15000)
            dropdown_button_locator.click()
            print("SEM_PRI_SE dropdown opened.")

            print("Locating the specific (focused) dropdown popup...")
            popup_locator = frame.locator("div.slicer-dropdown-popup.focused")
            try:
                popup_locator.wait_for(state="visible", timeout=10000)
                print("Focused dropdown popup located.")
            except TimeoutError:
                 print("Could not find the 'focused' dropdown popup. Trying generic visible popup...")
                 popup_locator = frame.locator("div.slicer-dropdown-popup:visible").first
                 popup_locator.wait_for(state="visible", timeout=5000)

            # Locate the container where items appear (might be the body or a specific scrollRegion)
            # We don't necessarily need to know if it's "scrollable" in the traditional sense now
            items_container_locator = popup_locator.locator(".slicerBody") # Target the body where items reside
            items_container_locator.wait_for(state="visible", timeout=10000)
            print("Items container within popup located.")


            print("Selecting 'Select all' (Original Method, within popup)...")
            select_all_locator = popup_locator.get_by_text("Select all", exact=True)
            select_all_locator.wait_for(state="visible", timeout=10000)
            # Check parent for 'selected' class which Power BI often uses
            is_checked = select_all_locator.evaluate("node => node.checked || node.getAttribute('aria-checked') === 'true' || node.parentElement.classList.contains('selected')")
            if not is_checked:
                 select_all_locator.click()
                 print("Checked 'Select all'.")
                 time.sleep(1)
            else:
                 print("'Select all' was already checked/selected.")


            # --- Scrolling via scroll_into_view_if_needed ---
            print("Initiating scroll sequence using scroll_into_view_if_needed...")
            last_week_number_found = None
            previous_last_item_title = None
            attempts = 0
            # Increased attempts as this method might require more steps
            max_scroll_attempts = 30 # Adjust as needed

            while attempts < max_scroll_attempts:
                attempts += 1
                print(f"Scroll attempt {attempts}/{max_scroll_attempts}...")

                # Get all currently visible items within the container
                # Using the items_container_locator ensures we search in the right place
                current_items = items_container_locator.locator("div.slicerItemContainer").all()
                numeric_items = [item for item in current_items if item.get_attribute("title") and item.get_attribute("title").strip().isdigit()]

                if not numeric_items:
                    print("No numeric items found in this attempt. Waiting briefly...")
                    # If nothing is found initially, wait a bit longer for first items to maybe appear
                    if attempts == 1: time.sleep(1)
                    # If still nothing after a few tries, something might be wrong
                    if attempts > 3:
                         print("Warning: No numeric items found after several attempts.")
                         break
                    continue # Try getting items again in the next loop iteration

                # Identify the last numeric item currently in the DOM for this container
                last_item = numeric_items[-1]
                current_last_item_title = last_item.get_attribute("title").strip()
                print(f"Current last visible week: {current_last_item_title}")

                # Check if the last item stopped changing
                if attempts > 1 and current_last_item_title == previous_last_item_title:
                    print("Last item hasn't changed after scroll. Assuming end of list.")
                    last_week_number_found = current_last_item_title
                    break # Exit loop, we've found the end

                # Update the title for the next comparison
                previous_last_item_title = current_last_item_title

                # Scroll the *last found item* into view
                # This is the action that should trigger loading more items if necessary
                print(f"Scrolling item '{current_last_item_title}' into view...")
                try:
                    last_item.scroll_into_view_if_needed(timeout=5000) # Add timeout to scroll action
                    # Crucial: Wait *after* scrolling for new items to potentially load
                    time.sleep(1.5) # Adjust sleep time if needed (1-2 seconds is typical for lazy load)
                except PlaywrightError as e:
                    print(f"Error during scroll_into_view_if_needed: {e}")
                    # Maybe the item disappeared during the scroll? Try to recover or break.
                    last_week_number_found = previous_last_item_title # Use the last known good value
                    break


            # --- End of Scrolling Logic ---

            # Final check: If loop finished by max attempts, use the last title found
            if not last_week_number_found and previous_last_item_title:
                 print(f"Max scroll attempts reached. Using last found week: {previous_last_item_title}")
                 last_week_number_found = previous_last_item_title
            elif not last_week_number_found:
                 print("Could not determine last week even after scrolling attempts.")
                 # page.pause() # Optional pause if failed

            # --- Data Fetching (remains the same) ---
            if last_week_number_found:
                print(f"Proceeding to fetch data. Identified last week: {last_week_number_found}")
                print("Waiting for data cards to potentially update...")
                time.sleep(5) # Wait after all interactions before grabbing data

                try:
                    frame.locator("svg.card").first.wait_for(state="visible", timeout=30000)
                    print("Data cards appear to be loaded.")
                except TimeoutError:
                     print("Warning: Data cards did not become visible after waiting.")
                     # page.pause()


                sem_data = {
                    "Last_Epidemiological_Week": last_week_number_found,
                    "All_Semanas_Data": {}
                }
                svg_cards = frame.locator("svg.card").all()
                print(f"Found {len(svg_cards)} svg.card elements.")

                if not svg_cards:
                    print("No svg.card elements found. Cannot extract data.")
                    # page.pause()

                for i, card in enumerate(svg_cards):
                    try:
                        value_locator = card.locator("text.value tspan")
                        label_locator = card.locator("text.label")

                        value_locator.wait_for(state='visible', timeout=5000)
                        value = value_locator.text_content(timeout=5000)

                        aria_label = card.get_attribute("aria-label")
                        card_label = aria_label
                        if not card_label or "card" in card_label.lower():
                             try:
                                label_locator.wait_for(state='visible', timeout=3000)
                                card_label = label_locator.text_content(timeout=3000)
                             except (TimeoutError, PlaywrightError):
                                card_label = f"Card_{i+1}_NoLabel"

                        if card_label and value:
                             print(f"Card {i+1}: Label='{card_label}', Value='{value}'")
                             sem_data["All_Semanas_Data"][card_label.strip()] = value.strip()
                        else:
                             print(f"Card {i+1}: Could not extract label or value reliably.")

                    except (TimeoutError, PlaywrightError) as card_e:
                        print(f"Error processing card {i+1}: {card_e}")


                output_dir = "Informe_Semana_Epidemiologica/output"
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, "SE-Y.yaml")
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(sem_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"Data saved to {file_path}")

            else:
                print("Could not identify the last epidemiological week. Data extraction skipped.")
                # page.pause()

        except TimeoutError as e:
            print(f"A timeout error occurred: {e}")
            page.pause()
        except PlaywrightError as e:
            print(f"A Playwright error occurred: {type(e).__name__} - {e}")
            page.pause()
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__} - {e}")
            page.pause()
        finally:
            print("Closing browser.")
            if 'browser' in locals() and browser.is_connected():
                 browser.close()

if __name__ == "__main__":
    main()