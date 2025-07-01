import streamlit as st
import pandas as pd
from product_class import Product
from parser import load_products, get_all_plu, check_duplicates, duplicate_barcodes

st.title("Product Validation Checker")

javado_file = st.file_uploader("Upload JAVADO Excel", type=["xlsx"])
active_file = st.file_uploader("Upload Active Product List", type=["xlsx"])

if javado_file and active_file:
    products = load_products(javado_file)
    all_products = get_all_plu(active_file)

    # Validation outputs
    plu_errors = []
    desc_len_errors = []
    bad_char_errors = []
    decimal_errors = []

    for product in products:
        if (err := product.plu_len()):
            plu_errors.append(err)
        if (err := product.desc_len()):
            desc_len_errors.append(err)
        if (err := product.bad_char()):
            bad_char_errors.append(err)
        if (err := product.decimal_format()):
            decimal_errors.append(err)

    barcode_errors = duplicate_barcodes(products)

    # Show errors
    if plu_errors:
        st.subheader("All PLU Code Length Errors:")
        for e in plu_errors:
            st.write(e)

    if desc_len_errors:
        st.subheader("All Product Description Length Errors:")
        for e in desc_len_errors:
            st.write(e)

    if bad_char_errors:
        st.subheader("All Unusable Character Errors:")
        for e in bad_char_errors:
            st.write(e)

    if decimal_errors:
        st.subheader("All Decimal Formatting Erors:")
        for e in decimal_errors:
            st.write(e)

    if barcode_errors:
        st.subheader("All Duplicated Barcode Errors:")
        for e in barcode_errors:
            st.write(e)
