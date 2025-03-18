import pandas as pd

# Load the CSV file into a pandas DataFrame
csv_file = "table_data/powerbi_data.csv"
try:
    # Read the CSV file
    df = pd.read_csv(csv_file, encoding="utf-8")

    # Filter the DataFrame to only include the required columns
    required_columns = ["UF", "ANO/SEMANA", "CASOS PROVÁVEIS DE DENGUE"]
    df = df[required_columns]

    # Optional: Display the first few rows to verify the data
    print("Preview of the filtered CSV data:")
    print(df.head())

    # Save the filtered DataFrame to an Excel file
    output_file = "powerbi_data.xlsx"
    df.to_excel(output_file, index=False, engine="openpyxl")

    print(f"Successfully converted and filtered '{csv_file}' to '{output_file}'.")

except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found. Please ensure it exists in the current directory.")
except Exception as e:
    print(f"An error occurred: {e}")