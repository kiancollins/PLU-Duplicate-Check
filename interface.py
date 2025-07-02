import pandas as pd
import streamlit as st
from collections import defaultdict, Counter
from product_class import Product  # Make sure this is in the same folder or Python path
from parser import load_products, get_all_plu, duplicate_barcodes, check_duplicates, find_internal_duplicates
from fixes import update_all
import io


st.title("New Product File Validation")

# File uploads
new_product_file = st.file_uploader("Upload New Product File", type=["xlsx"])
plu_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])

# # Proceed only if both files uploaded
if new_product_file and plu_file:

    # Step 1: Read and normalize new product file for auto fixes ---------
    try:
        df = pd.read_excel(new_product_file)
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")
        fixed_df, auto_changes = update_all(df)
    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}")
        st.stop()

    # Step 2: Load as Product class objects ----------
    try:
        products = load_products(new_product_file)
    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}")
        st.stop()

    # Step 3: Load PLU list ---------
    try:
        all_plu = get_all_plu(plu_file)
    except KeyError as e:
        st.error(f"Missing PLU column in PLU Active List: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()
    


    # Error collection ---------
    duplicate_plu_dict = check_duplicates(products, all_plu)
    duplicate_plu_errors = [
        f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Product {plu} is already in the system."  # +2 to match Excel row (header + 0-indexed)
        for plu, line in duplicate_plu_dict.items()
    ]
    internal_duplicates = find_internal_duplicates(products)
    plu_errors = []
    desc_errors = []
    bad_char_errors =[]
    decimal_errors =[]
    barcode_errors = duplicate_barcodes(products)
    

    # Check all products and store in proper lists
    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
        if (e := product.desc_len()):
            desc_errors.append(e)
        if (e := product.bad_char()):
            bad_char_errors.append(e)
        if (e := product.decimal_format()):
            decimal_errors.append(e)
        

    # Show results
    def display_results(title, errors):
        if errors:
            st.subheader(title)
            for e in errors:
                st.write(e)
        else:
            st.subheader(f"{title.replace(' Errors', '')} are all valid.")

    display_results("All Duplicate PLU Code Errors", duplicate_plu_errors)
    display_results("Duplicate PLUs Within Uploaded File", internal_duplicates)
    display_results("All PLU Code Length Errors", plu_errors)
    display_results("All Product Description Length Errors", desc_errors)
    display_results("All Unusable Character Errors", bad_char_errors)
    display_results("All Decimal Formatting Errors", decimal_errors)
    display_results("All Duplicate Barcode Errors", barcode_errors)


    # If no errors
    if not any([duplicate_plu_errors, internal_duplicates, plu_errors, 
                desc_errors, bad_char_errors, decimal_errors, barcode_errors]):
        st.success("All checks passed. File is ready for upload.")


    # Auto fixing ------------------
    if auto_changes:
        st.write("\n")
        st.title("Automatically fixed Errors:")
        for change in auto_changes:
            st.write(change)

        # Convert to Excel in memory
        buffer = io.BytesIO()
        fixed_df.to_excel(buffer, index=False)
        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name="Fixed_Product_File.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )





