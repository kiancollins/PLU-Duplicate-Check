# import streamlit as st
# import pandas as pd
# from product_class import Product
# from parser import load_products, get_all_plu, check_duplicates, duplicate_barcodes

# st.title("Product Validation Checker")

# javado_file = st.file_uploader("Upload JAVADO Excel", type=["xlsx"])
# active_file = st.file_uploader("Upload Active Product List", type=["xlsx"])

# if javado_file and active_file:
#     products = load_products(javado_file)
#     all_products = get_all_plu(active_file)

#     # Validation outputs
#     plu_errors = []
#     desc_len_errors = []
#     bad_char_errors = []
#     decimal_errors = []

#     for product in products:
#         if (err := product.plu_len()):
#             plu_errors.append(err)
#         if (err := product.desc_len()):
#             desc_len_errors.append(err)
#         if (err := product.bad_char()):
#             bad_char_errors.append(err)
#         if (err := product.decimal_format()):
#             decimal_errors.append(err)

#     barcode_errors = duplicate_barcodes(products)

#     # Show errors
#     if plu_errors:
#         st.subheader("All PLU Code Length Errors:")
#         for e in plu_errors:
#             st.write(e)

#     if desc_len_errors:
#         st.subheader("All Product Description Length Errors:")
#         for e in desc_len_errors:
#             st.write(e)

#     if bad_char_errors:
#         st.subheader("All Unusable Character Errors:")
#         for e in bad_char_errors:
#             st.write(e)

#     if decimal_errors:
#         st.subheader("All Decimal Formatting Erors:")
#         for e in decimal_errors:
#             st.write(e)

#     if barcode_errors:
#         st.subheader("All Duplicated Barcode Errors:")
#         for e in barcode_errors:
#             st.write(e)





import pandas as pd
from product_class import Product
from collections import defaultdict
import streamlit as st

st.title("Product Validation Tool")

# File uploads
new_product_file = st.file_uploader("Upload New Product File", type=["xlsx"])
plu_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])

# Proceed only if both files uploaded
if new_product_file and plu_file:
    df = pd.read_excel(new_product_file)
    df.columns = df.columns.str.strip()

    products = []
    for _, row in df.iterrows():
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

    # Get all existing PLUs
    all_df = pd.read_excel(plu_file)
    all_df.columns = all_df.columns.str.strip()
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
    if plu_errors:
        st.subheader("All PLU Code Length Errors:")
        for e in plu_errors:
            st.write(e)
    else:
        st.subheader("\n PLU Codes are all valid.")

    if desc_errors:
        st.subheader("All Product Description Length Errors:")
        for e in desc_errors:
            st.write(e)
    else:
        st.subheader("\n Product descriptions are all valid.")

    if bad_char_errors:
        st.subheader("All Unusable Character Errors:")
        for e in bad_char_errors:
            st.write(e)
    else:
        st.subheader("\n Characters are all valid.")

    if decimal_errors:
        st.subheader("All Decimal Formatting Erors:")
        for e in decimal_errors:
            st.write(e)
    else:
        st.subheader("\n Decimal formatting is all valid.")

    if barcode_errors:
        st.subheader("All Duplicate Barcode Errors:")
        for e in barcode_errors:
            st.write(e)
    else:
        st.subheader("\n Barcodes are all valid.")


    if not (plu_errors or desc_errors or bad_char_errors or decimal_errors or barcode_errors):
        st.success("All checks passed, file is ready for upload.")
