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

            # New steps: Copy selections from "/01" and "/02" columns
            page.get_by_role("columnheader", name="/01").first.click()
            page.get_by_text("/01").first.click(button="right")
            page.pause()
            page.get_by_role("menuitem", name="Copy").hover()
            page.get_by_test_id("pbimenu-item.Copy selection").click()

            page.get_by_role("columnheader", name="/02").first.click()
            page.get_by_role("columnheader", name="/02 Selected").click(button="right")
            page.get_by_test_id("pbimenu-item.Copy").hover()
            page.get_by_test_id("pbimenu-item.Copy selection").click()

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