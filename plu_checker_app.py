import pandas as pd
import streamlit as st
from collections import defaultdict
from product_class import Product  # Make sure this is in the same folder or Python path

st.title("Product Validation Checker")

# File uploads
new_product_file = st.file_uploader("Upload New Product File", type=["xlsx"])
plu_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])

# Proceed only if both files uploaded
if new_product_file and plu_file:
    df = pd.read_excel(new_product_file)
    df.columns = df.columns.str.strip()

    products = []
    for _, row in df.iterrows():
        try:
            products.append(Product(
                code=row['plu code'],
                description=row['Description'],
                subgroup=row['Sub Group'],
                supplier_code=row['3 Digit Supplier'],
                season=row['Season'],
                supplier_main=row['Main Supplier'],
                cost_price=row['cost price'],
                barcode=row['barcode'],
                vat_rate=row['Vat Rate'],
                rrp=row['RRP'],
                sell_price=row['Selling Price'],
                stg_price=row['Stg Price'],
                tarriff=row['Tarriff Code'],
                web=row['Web']
            ))
        except KeyError as e:
            st.error(f"Missing expected column: {e}")
            st.stop()

    # Get all existing PLUs
    all_df = pd.read_excel(plu_file)
    all_df.columns = all_df.columns.str.strip()
    if "PLU" not in all_df.columns:
        st.error("Missing 'PLU' column in uploaded PLU Active List.")
        st.stop()

    all_plu = all_df["PLU"].dropna().tolist()

    # Error collection
    plu_errors, desc_errors, bad_char_errors, decimal_errors, barcode_errors = [], [], [], [], []

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
    barcode_dict = defaultdict(list)
    for p in products:
        if p.barcode:
            barcode_dict[p.barcode].append(p.plu_code)
    for barcode, codes in barcode_dict.items():
        if len(codes) > 1:
            barcode_errors.append(f"Barcode {barcode} is shared by: {codes}")

    # Show results
    def display_results(title, errors):
        if errors:
            st.subheader(title)
            for e in errors:
                st.write(e)
        else:
            st.subheader(f"{title.replace(' Errors', '')} are all valid.")

    display_results("All PLU Code Length Errors", plu_errors)
    display_results("All Product Description Length Errors", desc_errors)
    display_results("All Unusable Character Errors", bad_char_errors)
    display_results("All Decimal Formatting Errors", decimal_errors)
    display_results("All Duplicate Barcode Errors", barcode_errors)

    if not any([plu_errors, desc_errors, bad_char_errors, decimal_errors, barcode_errors]):
        st.success("✅ All checks passed. File is ready for upload.")
