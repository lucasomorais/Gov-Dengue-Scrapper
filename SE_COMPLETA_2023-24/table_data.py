import pyperclip
import csv
from playwright.sync_api import sync_playwright

def parse_copied_data(header, raw_data):
    """Parse the copied data into separate columns"""
    lines = raw_data.strip().split('\n')
    parsed_data = []
    
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) >= 4:
            uf = parts[1]
            ano_semana = header
            casos = parts[3].replace(',', '')
            parsed_data.append([uf, ano_semana, casos])
    
    return parsed_data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Coloque False para depurar visualmente
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
                wait_until="networkidle"
            )

            element = page.wait_for_selector("visual-container:nth-of-type(1) g.tile > path", state="visible")
            element.click(position={"x": 241, "y": 113})
            print("Element clicked successfully!")

            page.get_by_role("columnheader", name="/01").click(button="right")
            page.get_by_test_id("pbimenu-item.Show as a table").click()

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
                    header.click(button="right")
                    
                    copy_button = page.locator('button[role="menuitem"][title="Copy"].pbi-menu-trigger')
                    copy_button.hover()
                    
                    copy_selection_button = page.locator('button[role="menuitem"][data-testid="pbimenu-item.Copy selection"][title="Copy selection"]')
                    copy_selection_button.click()

                    page.wait_for_timeout(500)  # Tempo para garantir que os dados sejam copiados

                    header_text = header.text_content()
                    processed_headers.add(header_text)
                    
                    if header_text.strip() != "Total":
                        copied_data = pyperclip.paste()  # Agora usando pyperclip
                        
                        parsed_rows = parse_copied_data(header_text, copied_data)
                        all_data.extend(parsed_rows)
                        print(f"Copied and parsed selection from header '{header_text}' (iteration {scroll_iterations + 1})")
                    else:
                        print(f"Copied selection from header '{header_text}' (iteration {scroll_iterations + 1}) - excluded from output")
                        print("Found 'Total' header. Ending application.")
                        should_break = True
                        break

                if should_break:
                    break

                box = scroll_bar.bounding_box()
                if box:
                    if last_scroll_x is None:
                        start_x = box['x'] + box['width'] / 2
                    else:
                        start_x = last_scroll_x
                    
                    page.mouse.move(start_x, box['y'] + box['height'] / 2)
                    page.mouse.down()
                    new_x = start_x + 127
                    page.mouse.move(new_x, box['y'] + box['height'] / 2)
                    page.mouse.up()
                    last_scroll_x = new_x
                    print(f"Scrolled horizontally to x={last_scroll_x} (iteration {scroll_iterations + 1})")
                
                scroll_iterations += 1
                page.wait_for_timeout(1000)

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