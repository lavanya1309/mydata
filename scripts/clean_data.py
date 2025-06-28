import os
import pandas as pd

# Months available in order
month_cols_full = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                   'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

start_row = 4  # row 5 in Excel is index 4

def clean_excel_file(input_path, output_path, available_months):
    try:
        # Read from 5th row onward (zero-indexed row 4)
        df = pd.read_excel(input_path, header=None, skiprows=start_row)
        
        # Drop columns that are all NaN but **do not drop all rows**
        df.dropna(axis=1, how='all', inplace=True)

        # Assign headers (truncate if fewer columns)
        headers = ['S NO', 'MAKER'] + available_months + ['TOTAL']
        df.columns = headers[:len(df.columns)]

        # Convert month data to numeric where possible
        for col in available_months:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

        # Serial Number (if no rows, this will be empty series)
        df['S NO'] = range(1, len(df) + 1)

        # Recalculate total column if months exist
        if len(df) > 0:
            df['TOTAL'] = df[available_months].sum(axis=1).astype(int)
        else:
            # Create TOTAL column with no rows (just header)
            df['TOTAL'] = pd.Series(dtype=int)

        # Ensure output folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save dataframe even if empty (just headers)
        df.to_excel(output_path, index=False)
        print(f"✅ Saved: {output_path}")

    except Exception as e:
        print(f"❌ Failed {input_path}: {e}")

if __name__ == "__main__":
    # Base paths
    base_folder_path = "../rto_wise_data"
    output_base_path = "./cleaned_rto_wise_data"
    os.makedirs(output_base_path, exist_ok=True)

    for year in ["2023"]:
        year_path = os.path.join(base_folder_path, str(year))
        if not os.path.isdir(year_path):
            continue
            
        print(f"\nProcessing year: {year}")
        
        available_months = month_cols_full[:5] if year == '2025' else month_cols_full

        # DEBUG: Print all folders in the year directory
        print(f"Files found in year {year}: {os.listdir(year_path)}")

        # Process each state
        for state_folder in os.listdir(year_path):
            state_path = os.path.join(year_path, state_folder)
            if not os.path.isdir(state_path):
                continue
                
            print(f"Processing state: {state_folder}")
            
            # Process each RTO file
            for rto_file in os.listdir(state_path):
                if not rto_file.endswith('.xlsx') or rto_file.startswith('~$'):
                    continue
                    
                # Setup input and output paths
                input_file = os.path.join(state_path, rto_file)
                output_file = os.path.join(output_base_path, year, state_folder, f"{os.path.splitext(rto_file)[0]}_cleaned.xlsx")
                
                # Clean the file
                clean_excel_file(input_file, output_file, available_months)


    # base_folder_path = "VahanData/[EV]BrandWiseRTOWiseMonthWise2024"

    # Process each year
    # for year in os.listdir(rto_folder_path):
    #     year_path = os.path.join(rto_folder_path, year)
    #     if not os.path.isdir(year_path):
    #         continue
            
    #     print(f"\nProcessing year: {year}")
        
    #     # Set available months based on year
    #     available_months = month_cols_full[:5] if year == '2025' else month_cols_full
        
    #     # Process each state
    #     for state_folder in os.listdir(year_path):
    #         state_path = os.path.join(year_path, state_folder)
    #         if not os.path.isdir(state_path):
    #             continue
                
    #         print(f"Processing state: {state_folder}")
            
    #         # Process each RTO file
    #         for rto_file in os.listdir(state_path):
    #             if not rto_file.endswith('.xlsx') or rto_file.startswith('~$'):
    #                 continue
                    
    #             # Setup input and output paths
    #             input_file = os.path.join(state_path, rto_file)
    #             output_file = os.path.join(output_base_path, year, state_folder, f"{os.path.splitext(rto_file)[0]}_cleaned.xlsx")
                
    #             # Clean the file
    #             clean_excel_file(input_file, output_file, available_months)