import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

def adjust_column_widths(ws):
    """
    Adjust the width of each column in the worksheet to fit the content.
    Iterates through all cells in each column to find the maximum content length
    and sets the column width accordingly.
    """
    # Dictionary to store the maximum width for each column
    column_widths = {}

    # Iterate through all rows and columns in the worksheet
    for row in ws.rows:
        for cell in row:
            if cell.value:  # Only consider cells with content
                # Get the column letter (e.g., 'A', 'B', etc.)
                column = cell.column_letter
                # Calculate the length of the cell's content
                try:
                    # Convert the cell value to string and calculate its length
                    cell_length = len(str(cell.value))
                except:
                    cell_length = 0  # In case of conversion error, use 0

                # Update the maximum width for this column
                if column in column_widths:
                    column_widths[column] = max(column_widths[column], cell_length)
                else:
                    column_widths[column] = cell_length

    # Set the width for each column
    for column, width in column_widths.items():
        # Add a small buffer (e.g., 2) to the width for readability
        # Also ensure a minimum width (e.g., 10) to avoid overly narrow columns
        adjusted_width = max(width + 2, 10)
        ws.column_dimensions[column].width = adjusted_width

def main():
    # Get the current date for the output filename
    current_date = datetime.now().strftime("%m-%d-%y")

    # Define the paths to the Excel files
    files = [
        f"_results/Big_Numbers_DATA/Big_Numbers_UF_{current_date}.xlsx",
        f"_results/SE_COMPLETA_2023-24_DATA/SE_COMPLETA_2023-24_{current_date}.xlsx",
        f"_results/Informe_Semana_Epidemiologica_DATA/Informe_Semana_Epidemiologica_{current_date}.xlsx"
    ]

    # Create a new workbook for the merged file
    wb = Workbook()
    # Remove the default sheet created by Workbook()
    wb.remove(wb.active)

    # Copy sheets from each source file into the new workbook
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            continue

        # Load the source workbook
        source_wb = load_workbook(file_path)
        for sheet_name in source_wb.sheetnames:
            source_ws = source_wb[sheet_name]
            # Create a new sheet in the destination workbook
            dest_ws = wb.create_sheet(title=sheet_name)

            # Copy all cells from the source sheet to the destination sheet
            for row in source_ws.rows:
                for cell in row:
                    new_cell = dest_ws.cell(row=cell.row, column=cell.column, value=cell.value)
                    # Copy cell formatting (if any)
                    if cell.has_style:
                        new_cell.font = cell.font.copy()
                        new_cell.border = cell.border.copy()
                        new_cell.fill = cell.fill.copy()
                        new_cell.number_format = cell.number_format
                        new_cell.protection = cell.protection.copy()
                        new_cell.alignment = cell.alignment.copy()

            # Copy column dimensions (if any)
            for col in source_ws.column_dimensions:
                dest_ws.column_dimensions[col].width = source_ws.column_dimensions[col].width

            # Copy row dimensions (if any)
            for row in source_ws.row_dimensions:
                dest_ws.row_dimensions[row].height = source_ws.row_dimensions[row].height

            # Adjust column widths to fit content
            adjust_column_widths(dest_ws)

    # Save the merged workbook
    output_path = f"_results/_final_output/Epidemiology_Dengue_{current_date}.xlsx"
    wb.save(output_path)
    print(f"Merged file saved as: {output_path}")

if __name__ == "__main__":
    main()