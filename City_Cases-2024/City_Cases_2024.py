import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a timestamp for the filenames in the format MM-DD-YY
    timestamp = datetime.now().strftime("%m-%d-%y")  # e.g., "03-21-25"

    # Create the 'original_file' directory if it doesn't exist
    original_dir = os.path.join(script_dir, "original_file")
    os.makedirs(original_dir, exist_ok=True)

    # Create the 'output' directory if it doesn't exist
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True, slow_mo=500)  # slow_mo for visibility
        
        # Create a new browser context with download handling
        context = browser.new_context(
            accept_downloads=True  # Enable downloads
        )
        page = context.new_page()
        
        # Navigate to the target URL
        page.goto("http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def")
        print(f"Page title: {page.title()}")

        # Locate the select element by its ID
        select_element = page.locator("#L")

        # Scroll the select element into view
        select_element.scroll_into_view_if_needed()

        # Click the select element to focus it
        select_element.click()

        # Locate the specific option "Município de residência" by its value
        target_option = page.locator('option[value="Município_de_residência"]')
        
        # Scroll the option into view within the dropdown
        target_option.scroll_into_view_if_needed()

        # Click the target option to select it
        target_option.click()

        # Verify the selection (optional, for debugging)
        selected_value = select_element.input_value()
        print(f"Selected value: {selected_value}")

        # Locate the "Mostra" button using get_by_role
        mostra_button = page.get_by_role("button", name="Mostra")

        # Scroll the button into view
        mostra_button.scroll_into_view_if_needed()

        # Click the "Mostra" button, which opens a new page
        with page.expect_popup() as popup_info:
            mostra_button.click()
        
        # Switch to the new page
        new_page = popup_info.value
        print(f"New page title: {new_page.title()}")

        # Wait for the new page to fully load
        new_page.wait_for_load_state("networkidle")  # Waits until no network activity

        # Locate the "Copia como .CSV" link
        csv_link = new_page.get_by_role("link", name="Copia como .CSV")

        # Scroll the link into view
        csv_link.scroll_into_view_if_needed()

        # Handle the download
        with new_page.expect_download() as download_info:
            csv_link.click()
        
        # Get the download object
        download = download_info.value

        # Save the original downloaded file to the 'original_file' folder with date suffix
        original_filename = f"tabnet_dengue_{timestamp}.csv"
        original_path = os.path.join(original_dir, original_filename)
        download.save_as(original_path)
        print(f"Original file downloaded and saved as: {original_path}")

        # Close the browser
        browser.close()

    # Process the original CSV file using pandas
    print("Processing the CSV file...")

    try:
        # Read the CSV, skip the first 4 rows, use semicolon delimiter, and specify encoding
        df = pd.read_csv(original_path, skiprows=4, sep=';', header=None, encoding='latin1')

        # The data should have two columns after the semicolon split
        # Column 0: "Município de residência" (e.g., "110001 ALTA FLORESTA D'OESTE")
        # Column 1: "Casos_Prováveis" (e.g., "50")

        # Split Column 0 into two columns: code and name
        df['code'] = df[0].str[:6]  # First 6 characters for the code
        df['name'] = df[0].str[7:].str.strip()  # The rest, after the space, for the name

        # Keep only the desired columns: code, name, and Casos_Prováveis
        df = df[['code', 'name', 1]]
        df.columns = ['code', 'name', 'Casos_Prováveis']

        # Filter out footer rows: keep only rows where 'code' is a 6-digit number
        df = df[df['code'].str.match(r'^\d{6}$')]

        # Save the processed data to the 'output' folder with date suffix
        final_output_filename = f"City_Cases_{timestamp}.csv"
        final_output_path = os.path.join(output_dir, final_output_filename)
        df.to_csv(final_output_path, index=False, encoding='utf-8')
        print(f"Processed file saved as: {final_output_path}")

    except Exception as e:
        print(f"Error processing the CSV file: {e}")
        raise

if __name__ == "__main__":
    main()