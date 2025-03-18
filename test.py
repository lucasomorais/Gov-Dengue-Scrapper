from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1912, "height": 920},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False
        )
        page = context.new_page()

        try:
            # Navigate to the Power BI URL
            page.goto(
                "https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc",
                wait_until="networkidle"
            )

            # Wait for the element to be present and click it
            element = page.wait_for_selector("visual-container:nth-of-type(1) g.tile > path", state="visible")
            element.click(position={"x": 241, "y": 113})

            print("Element clicked successfully!")

            # Right-click on the column header "/01" and select "Show as a table"
            page.get_by_role("columnheader", name="/01").click(button="right")
            page.get_by_test_id("pbimenu-item.Show as a table").click()

            # Target the correct horizontal scroll bar
            scroll_bar = page.locator(".pivotTable > div:nth-child(7) > .scroll-bar-part-bar").first
            scroll_bar.scroll_into_view_if_needed()

            # Initialize tracking variables
            column_headers = page.get_by_role("columnheader")
            processed_headers = set()  # Track processed headers by text content
            scroll_iterations = 0
            last_scroll_x = None  # Track scroll bar position

            while True:
                # Get all currently visible headers
                headers = column_headers.all()
                if not headers:
                    print("No headers found.")
                    break

                # Skip the first header ("REGIÃO") and process up to 5 new headers
                new_headers = [h for i, h in enumerate(headers) if i > 0 and h.text_content() not in processed_headers]
                if not new_headers:
                    print("No new headers to process after scrolling. Reached the end of the table.")
                    break

                # Process up to 5 new headers
                for i, header in enumerate(new_headers[:5]):
                    header.click(button="right")
                    
                    # Hover over "Copy" button
                    copy_button = page.locator('button[role="menuitem"][title="Copy"].pbi-menu-trigger')
                    copy_button.hover()
                    
                    # Click "Copy Selection"
                    copy_selection_button = page.locator('button[role="menuitem"][data-testid="pbimenu-item.Copy selection"][title="Copy selection"]')
                    copy_selection_button.click()
                    
                    header_text = header.text_content()
                    processed_headers.add(header_text)
                    print(f"Copied selection from header '{header_text}' (iteration {scroll_iterations + 1})")

                    # Check if we just processed "Total"
                    if header_text.strip() == "Total":
                        print("Found 'Total' header. Ending application.")
                        break  # Exit the inner loop

                # If we broke out of the inner loop due to "Total", exit the outer loop too
                if "Total" in processed_headers:
                    break

                # Move the horizontal scroll bar to the right
                box = scroll_bar.bounding_box()
                if box:
                    if last_scroll_x is None:
                        # First scroll: start from center
                        start_x = box['x'] + box['width'] / 2
                    else:
                        # Continue from last position
                        start_x = last_scroll_x
                    
                    page.mouse.move(start_x, box['y'] + box['height'] / 2)
                    page.mouse.down()
                    new_x = start_x + 145  # Move 100 pixels right
                    page.mouse.move(new_x, box['y'] + box['height'] / 2)
                    page.mouse.up()
                    last_scroll_x = new_x  # Update last scroll position
                    print(f"Scrolled horizontally to x={last_scroll_x} (iteration {scroll_iterations + 1})")
                
                scroll_iterations += 1

                # Small delay to allow UI to update
                page.wait_for_timeout(1000)

            print(f"Completed: Processed {len(processed_headers)} headers across {scroll_iterations} scrolls.")

            # Pause for debugging (optional)
            page.pause()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the browser
            context.close()
            browser.close()

if __name__ == "__main__":
    main()