import csv
from playwright.sync_api import sync_playwright, TimeoutError

def parse_column_data(header, column_cells):
    """Parse the column data directly from DOM elements"""
    parsed_data = []
    for cell in column_cells:
        parts = cell.split('\t') if '\t' in cell else [cell]  # Fallback for single-value cells
        if len(parts) >= 1:  # Adjust based on actual cell content structure
            uf = parts[0] if parts[0] else "N/A"  # Assuming UF is in the first column
            ano_semana = header
            casos = parts[-1].replace(',', '') if len(parts) > 1 else "0"  # Last value as casos
            parsed_data.append([uf, ano_semana, casos])
    return parsed_data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1912, "height": 920},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False
        )
        page = context.new_page()

        all_data = []

        try:
            page.goto(
                "https://app.powerbi.com/view?r=eyJrIjoiYzQyOTI4M2ItZTQwMC00ODg4LWJiNTQtODc5MzljNWIzYzg3IiwidCI6IjlhNTU0YWQzLWI1MmItNDg2Mi1hMzZmLTg0ZDg5MWU1YzcwNSJ9&pageName=ReportSectionbd7616200acb303571fc",
                wait_until="domcontentloaded",
                timeout=60000
            )

            element = page.wait_for_selector(
                "visual-container:nth-of-type(1) g.tile > path",
                state="visible",
                timeout=30000
            )
            element.click(position={"x": 241, "y": 113})
            print("Element clicked successfully!")

            # Show data as table
            page.get_by_role("columnheader", name="/01").first.click(button="right")
            page.get_by_test_id("pbimenu-item.Show as a table").click()
            page.wait_for_timeout(3000)  # Wait for table to fully render

            scroll_bar = page.locator(".pivotTable > div:nth-child(7) > .scroll-bar-part-bar").first
            scroll_bar.scroll_into_view_if_needed()

            column_headers = page.get_by_role("columnheader")
            processed_headers = set()
            scroll_iterations = 0
            last_scroll_x = None

            while True:
                headers = column_headers.all()
                if not headers:
                    print("No headers found.")
                    break

                new_headers = [h for i, h in enumerate(headers) if i > 0 and h.text_content() not in processed_headers]
                if not new_headers:
                    print("No new headers to process after scrolling. Reached the end of the table.")
                    break

                should_break = False
                for i, header in enumerate(new_headers[:5]):
                    try:
                        header_text = header.text_content().strip()
                        print(f"Processing header: '{header_text}' (iteration {scroll_iterations + 1})")

                        if header_text != "Total":
                            # Click the header to ensure the column is active (optional)
                            header.click()
                            page.wait_for_timeout(1000)

                            # Locate the column cells under this header
                            header_index = processed_headers.__len__() + i + 1  # Adjust for 1-based index
                            column_cells = page.locator(
                                f'.pivotTable div[role="gridcell"][aria-colindex="{header_index + 1}"]'
                            ).all_text_contents()

                            if column_cells:
                                parsed_rows = parse_column_data(header_text, column_cells)
                                all_data.extend(parsed_rows)
                                print(f"Extracted {len(parsed_rows)} rows from header '{header_text}'")
                            else:
                                print(f"No data found under header '{header_text}'")

                            processed_headers.add(header_text)
                        else:
                            print(f"Encountered 'Total' header - excluded from output")
                            should_break = True
                            break

                    except TimeoutError as e:
                        print(f"Timeout occurred while processing header '{header_text}': {e}")
                        continue
                    except Exception as e:
                        print(f"Error occurred while processing header '{header_text}': {e}")
                        continue

                if should_break:
                    break

                # Scroll logic
                box = scroll_bar.bounding_box()
                if box:
                    if last_scroll_x is None:
                        start_x = box['x'] + box['width'] / 2
                    else:
                        start_x = last_scroll_x
                    
                    page.mouse.move(start_x, box['y'] + box['height'] / 2)
                    page.mouse.down()
                    new_x = start_x + 142
                    page.mouse.move(new_x, box['y'] + box['height'] / 2)
                    page.mouse.up()
                    last_scroll_x = new_x
                    print(f"Scrolled horizontally to x={last_scroll_x} (iteration {scroll_iterations + 1})")
                
                scroll_iterations += 1
                page.wait_for_timeout(2000)

            print(f"Completed: Processed {len(processed_headers)} headers across {scroll_iterations} scrolls (excluded 'Total' from output).")

            with open("SE_COMPLETA_2023-24/output/SE_COMPLETA_2023-24.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["UF", "Ano/Semana", "Casos prováveis de Dengue"])
                writer.writerows(all_data)

            print("Data saved to 'SE_COMPLETA_2023-24' with separate columns.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    main()