import pandas as pd
import streamlit as st
from collections import defaultdict, Counter
from product_class import Product  # Make sure this is in the same folder or Python path
from parser import * 
from fix_products import update_all_products
from fix_clothing import update_all_clothing
import io
from tools import *


ERROR_TYPES = {
    # Product checks
    "Duplicate PLU Code Errors": "PLU Codes are all valid.", 
    "Duplicate PLUs Within Uploaded File": "No Duplicate PLU Codes.",
    "PLU Code Length Errors": "PLU Code lengths are all valid.",
    "Product Description Length Errors": "Product descriptions are all valid.",
    "Decimal Formatting Errors": "All numbers rounded correctly.",

    # Shared
    "Unusable Character Errors": "No unusable characters found.",
    "Duplicate Barcode Errors": "All barcodes are valid.",

    # Clothing checks
    "Duplicate Style Code Code Errors": "Style Codes are all valid.",
    "Duplicate Style Codes Within Uploaded File": "No Duplicate Style Codes.",
    "Style Code Length Errors": "Style Code lengths are all valid.",
    "Clothing Item Description Length Errors": "Descriptions are all valid.",
}

def display_results(title: str, errors: list[str]):
    if errors: 
        expander_title = f"{title} — {len(errors)} issue(s)"
        with st.expander(expander_title, expanded=False):
            for err in errors:
                st.markdown(f"- {err}")
    else:
        success_msg = ERROR_TYPES.get(title, f"{title} passed all checks.")
        st.success(success_msg)



st.title("New Product File Validation")
file_type = st.selectbox("Select File Type", ["Product", "Clothing"])

# File uploads
new_file = st.file_uploader(f"Upload New {file_type} File", type=["xlsx"])
full_list_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])


# Proceed only if both files uploaded
if file_type == "Product" and new_file and full_list_file:

# Step 1: Read and normalize new product file for auto fixes ---------
    try:
        df = pd.read_excel(new_file)                                            # Read in file

        expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = [normalize_header(c) for c in df.columns]

        missing = check_missing_columns(df, PRODUCT_HEADER_MAP)                         # Check missing columns
        if missing:
            st.warning(f"Columns not found in new file: {','.join(missing)}")
        else:
            st.success(f"All expected columns found in new file.")
        
        fixed_df, auto_changes = update_all_products(df)                        # Apply auto-changes

    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}")
        st.stop()

# Step 2: Load as Product class objects ----------
    try:
        products, messages = load_products(new_file) # was new file
        missing = []
        for message, type in messages:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in new file upload.")


    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}")
        st.stop()

# Step 3: Load PLU list ---------
    try:
        full_list, message, type = read_column(full_list_file, POSSIBLE_PLU)
        missing = []
        if message:
            if type == "alert":
                st.success(message)
            elif type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in full list upload.")

    except KeyError as e:
        st.error(f"Missing PLU column in full list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()
    

# Error collection ---------
# duplicate_plu_dict = check_duplicates(products, all_plu)
    duplicate_plu_dict = check_duplicates(products, full_list, "plu_code")
    duplicate_plu_errors = [
        f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Product {plu} is already in the system."  # +2 to match Excel row (header + 0-indexed)
        for plu, line in duplicate_plu_dict.items()
    ]
    internal_duplicates = check_internal_duplicates(products, "plu_code")
    plu_errors = []
    prod_desc_errors = []
    prod_bad_char_errors = []
    decimal_errors =[]
    prod_barcode_errors = duplicate_barcodes(products, "plu_code")
    

# Check all products and store in proper lists
    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
        # if (e := product.desc_len()):
        #     prod_desc_errors.append(e)
        if (e := bad_char(product, "plu_code")):
            prod_bad_char_errors.append(e)
        # if (e := product.decimal_format()):
        #     decimal_errors.append(e)
        
# Display errors
    display_results("Duplicate PLU Code Errors", duplicate_plu_errors)
    display_results("Duplicate PLUs Within Uploaded File", internal_duplicates)
    display_results("PLU Code Length Errors", plu_errors)
    # display_results("Product Description Length Errors", prod_desc_errors)
    display_results("Unusable Character Errors", prod_bad_char_errors)
    # display_results("Decimal Formatting Errors", decimal_errors)
    display_results("Duplicate Barcode Errors", prod_barcode_errors)


# If no errors
    if not any([duplicate_plu_errors, internal_duplicates, plu_errors, 
                prod_desc_errors, prod_bad_char_errors, decimal_errors, prod_barcode_errors]):
        st.success("All checks passed. File is ready for upload.")

    elif len(auto_changes.items()) > len(auto_changes.keys()):
        st.write("\n")
        st.title("Automatically Fixed Errors:")

        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")

        # Convert to Excel in memory
        buffer = io.BytesIO()
        fixed_df.to_excel(buffer, index=False)
        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name= f"Fixed-{new_file.name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.title("No Auto-fixes Found")


elif file_type == "Clothing" and new_file and full_list_file:
# Step 1: Read and normalize new clothing file for auto fixes ---------

    try:
        expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")

        missing = check_missing_columns(df, CLOTHING_HEADER_MAP)                         # Check missing columns
        if missing:
            st.warning(f"Columns not found in new file: {', '.join(missing)}")
        else:
            st.success(f"All expected columns found in new file.")
        
        fixed_df, auto_changes = update_all_clothing(df)         
    except Exception as e:
        st.error(f"Error reading or fixing new clothing file: {e}")
        st.stop()

# Step 2: Load as Product class objects ----------
    try:
        clothes, messages = load_clothing(new_file)
        for message, type, in messages:
            if type == "alert":
                st.success(message)
            elif type == "error":
                st.error(message)

    except Exception as e:
        st.error(f"Error loading new clothing file into Clothing objects: {e}")
        st.stop()

# Step 3: Load Clothing list ---------
    try:
        all_style_codes, message, type = read_column(full_list_file, CLOTHING_HEADER_MAP["style_code"])
        if message:
            if type == "alert":
                st.success(message)
            elif type == "error":
                st.error(message)

    except KeyError as e:
        st.error(f"Missing Style Code column in full items list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading full items list: {e}")
        st.stop()



# # Error collection ---------
#     print("=== Sample from clothing objects ===")
#     for c in clothes[:5]:
#         print(f"Style code: {c.style_code} → {normalizer(c.style_code)}")

#     print("\n=== Sample from full list ===")
#     for s in all_style_codes[:5]:
#         print(f"From full list: {s} → {normalizer(s)}")



    duplicate_styles = check_duplicates(clothes, all_style_codes, "style_code")
    duplicate_style_errors = [
        f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Item {style_code} is already in the system."  # +2 to match Excel row (header + 0-indexed)
        for style_code, line in duplicate_styles.items()
    ]
    internal_duplicates = check_clothing_duplicates(clothes)
    style_len_errors = []
    colour_len_errors = []
    clothing_bad_char_errors =[]
    clothing_decsc_errors =[]
    clothing_barcode_errors = duplicate_barcodes(clothes, "style_code")
    

# Check all items and store in proper lists
    for item in clothes:
        if (e := item.style_len()):
            style_len_errors.append(e)
        # if (e := item.colour_len()):
            colour_len_errors.append(e)
        if (e := bad_char(item, "style_code")):
            clothing_bad_char_errors.append(e)
        # if (e := item.desc_len()):
            clothing_decsc_errors.append(e)

            
# Display Errors
    display_results("All Duplicate Style Code Code Errors", duplicate_style_errors)
    display_results("Duplicate Style Codes Within Uploaded File", internal_duplicates)
    display_results("All Style Code Length Errors", style_len_errors)
    # display_results("All Clothing Item Description Length Errors", clothing_decsc_errors)
    # display_results("All Color Length Description Errors", colour_len_errors)
    display_results("All Unusable Character Errors", clothing_bad_char_errors)
    display_results("All Duplicate Barcode Errors", clothing_barcode_errors)


# If no errors
    if not any([duplicate_style_errors, internal_duplicates, style_len_errors, clothing_decsc_errors, 
    clothing_bad_char_errors, clothing_barcode_errors]):
        st.success("All checks passed. File is ready for upload.")

# Auto fixing ------------------
    elif len(auto_changes.items()) > len(auto_changes.keys()):
        st.write("\n")
        st.title("Automatically Fixed Errors:")

        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")

        # Convert to Excel in memory
        buffer = io.BytesIO()
        fixed_df.to_excel(buffer, index=False)
        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name= f"Fixed-{new_file.name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.title("No Auto-fixes Found")





