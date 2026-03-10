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
import re

path = "src/data-gather/shpd-21-24-determinations.pdf"
# pdf = pdfplumber.open(path)
all_rows = []
header = None

# tracks the specific project we're on
current_entity = None

# set to None or some number if you want.
LIMIT_PAGES = None 

# regex for project number matching
project_id_pattern = re.compile(r'\d{4}PR\d{5}')

with pdfplumber.open(path) as pdf:
    # we limit ourselves for testing
    pages_to_process = pdf.pages[:LIMIT_PAGES] if LIMIT_PAGES else pdf.pages
    total_page = len(pages_to_process)

    # all_rows = []
    # for i in range(1, total_page):
    #     page = pdf.pages[i] #this only reads the first page
    #     print("Reading page: ", i)
    #     table = page.extract_table()

    #     if table:
    #         print(f"Page {i}: Found {len(table)} rows")
    #         # If it's the first page with data, grab the header
    #         if header is None:
    #             header = table[0]
    #             all_rows.extend(table[1:]) # Add data excluding header
    #         else:
    #             # For subsequent pages, skip the header row
    #             all_rows.extend(table[1:])
    #     else:
    #         print(f"Page {i}: No table found!")

    #     page.flush_cache()  # Critical for memory

    for i, page in enumerate(pages_to_process):
        print("Reading page: ", i)
        table = page.extract_table()
        if not table:
            continue

        # Clean None values immediately
        table = [[str(col) if col is not None else "" for col in row] for row in table]

        if header is None:
            header = [h.replace('\n', ' ').strip() for h in table[0]]
            start_index = 1
        else:
            start_index = 0

        for row in table[start_index:]:
            # Clean internal newlines in the current row cells
            row = [cell.replace('\n', ' ').strip() for cell in row]

            # Check if this is a repeated header row (common in multi-page PDFs)
            if row[0] == header[0] or "Project Number" in row[0]:
                continue

            # skip empty rows
            if not any(row):
                continue

            # LOGIC: Check if the first column contains a valid Project Number
            has_new_id = bool(project_id_pattern.search(row[0]))
            
            if has_new_id:
                # build entry, saving it with all_rows
                if current_entity:
                    all_rows.append(current_entity)
                current_entity = row
            else: 
                #overflow condition
                if current_entity:
                    for idx in range(len(row)):
                        if row[idx]:
                            separator = "; " if idx == 11 else " "
                            current_entity[idx] = f"{current_entity[idx]}{separator}{row[idx]}".strip("; ")
                else:
                    current_entry = row
        
        page.flush_cache()
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
filename = "shpd-plumb"
df.to_csv(f"raw-data/{filename}.csv", index = False)

