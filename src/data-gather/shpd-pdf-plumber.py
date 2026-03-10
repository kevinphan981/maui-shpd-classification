'''
    @purpose: to comb through PDF file of all SHPD review data of a specified date
    @output: clean csv containing everything untouched without the mess of excel
    @author: Kevin Phan

    Note: This is genuinely because Excel is ruining the project name descriptions.
    It just doesn't load correctly
'''
import pdfplumber
import pandas as pd
import gc

path = "src/data-gather/shpd-21-24-determinations.pdf"
# pdf = pdfplumber.open(path)
all_rows = []
header = None
# set to None or some number if you want.
LIMIT_PAGES = None 

# overflowing rows problem

with pdfplumber.open(path) as pdf:
    # we limit ourselves for testing
    pages_to_process = pdf.pages[:LIMIT_PAGES] if LIMIT_PAGES else pdf.pages
    total_page = len(pages_to_process)
    all_rows = []


    for i in range(1, total_page):
        page = pdf.pages[i] #this only reads the first page
        print("Reading page: ", i)
        table = page.extract_table()

        if table:
            print(f"Page {i}: Found {len(table)} rows")
            # If it's the first page with data, grab the header
            if header is None:
                header = table[0]
                all_rows.extend(table[1:]) # Add data excluding header
            else:
                # For subsequent pages, skip the header row
                all_rows.extend(table[1:])
        else:
            print(f"Page {i}: No table found!")

        page.flush_cache()  # Critical for memory
        gc.collect()  # Helps on lower-RAM systems
        print("Starting next page.")


print(table)
if all_rows:
    df = pd.DataFrame(all_rows, columns=header)
    
    # Final cleanup: Remove newlines from all text cells
    df = df.replace(r'\n', ' ', regex=True)
    
    print("\n--- Final Results ---")
    print(f"Total Rows Extracted: {len(df)}")
    print(f"DataFrame Shape: {df.shape}")
    print(df.head())
    print(df["Project Name"].head(n = 100))
else:
    print("Extraction failed: No rows were collected.")
print(f"Final Shape: {df.shape}")

