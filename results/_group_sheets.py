import pandas as pd

# Load the Excel files
file1 = "results/Big_Numbers_UF.xlsx"
file2 = "results/SE_COMPLETA_2023-24.xlsx"

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Create a new Excel file with specified sheet names
output_file = "results/final_output/Epidemiology - Dengue.xlsx"
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="Big_Numbers_UF", index=False)
    df2.to_excel(writer, sheet_name="SE_COMPLETA_2023-24", index=False)

print(f"Merged file saved as '{output_file}'")

