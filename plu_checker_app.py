import pandas as pd
import streamlit as st
from collections import defaultdict, Counter
from product_class import Product  # Make sure this is in the same folder or Python path
from parser import load_products, get_all_plu, duplicate_barcodes, check_duplicates, find_internal_duplicates


st.title("Product Validation Checker")

# File uploads
new_product_file = st.file_uploader("Upload New Product File", type=["xlsx"])
plu_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])

# Proceed only if both files uploaded
if new_product_file and plu_file:
    try:
        products = load_products(new_product_file)
        all_plu = get_all_plu(plu_file)
    except KeyError:
        st.error("Missing 'PLU' column in uploaded PLU Active List.")
        st.stop()
    except ValueError:
        st.error('One of the uploaded files is an invalid excel file or not an excel file')


    


    # Error collection
    duplicate_plu_dict = check_duplicates(products, all_plu)
    duplicate_plu_errors = [
        f"PLU {plu} is already in the system (line {line + 2})"  # +2 to match Excel row (header + 0-indexed)
        for plu, line in duplicate_plu_dict.items()
    ]
    internal_duplicates = find_internal_duplicates(products)
    plu_errors = []
    desc_errors = []
    bad_char_errors =[]
    decimal_errors =[]
    barcode_errors = duplicate_barcodes(products)
    

    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
        if (e := product.desc_len()):
            desc_errors.append(e)
        if (e := product.bad_char()):
            bad_char_errors.append(e)
        if (e := product.decimal_format()):
            decimal_errors.append(e)
        

    # Barcode duplicates
    # barcode_dict = defaultdict(list)
    # for p in products:
    #     if p.barcode:
    #         barcode_dict[p.barcode].append(p.plu_code)
    # for barcode, codes in barcode_dict.items():
    #     if len(codes) > 1:
    #         barcode_errors.append(f"Barcode {barcode} is shared by: {codes}")

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



    if not any([plu_errors, desc_errors, bad_char_errors, decimal_errors, barcode_errors]):
        st.success("All checks passed. File is ready for upload.")
