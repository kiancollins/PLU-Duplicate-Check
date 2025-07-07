import pandas as pd
from product_class import Product
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
from fix_products import update_all_products
from clothing_class import Clothing
from fix_clothing import update_all_clothing
from tools import *


NEW_PRODUCTS_GARDEN = "0107025 GARDEN FRESH.xlsx" 
NEW_PRODUCTS_JAVADO = "JAVADO UPLOAD.xlsx"
PLU_ACTIVE = "PLU-Active-List.xlsx"
CLOTHING_UPLOAD = "clothing upload example.xlsx"
FULL_CLOTHING = "full_clothing_listing.xlsx"



def load_products(path: str) -> list[Product]:
    """Load the new product file into a list of Clothing class objects"""
    df = pd.read_excel(path)

    products = []
    get_col = lambda key: find_column(df, PRODUCT_HEADER_MAP[key])
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get(get_col("plu_code")),
            description = row.get(get_col("description")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),
            tarriff = row.get(get_col("tarriff")),
            web = row.get(get_col("web")),
            idx = line_number
        )
        products.append(product)
    return products


def load_clothing(path: str) -> list[Clothing]:
    """Load the new clothing file into a list of Clothing class objects"""
    df = pd.read_excel(path)
    clothes = []
    get_col = lambda key: find_column(df, CLOTHING_HEADER_MAP[key])
    for idx, row in df.iterrows():
        line_number = idx + 2
        clothing = Clothing(
            code = row.get(get_col("style_code")),
            description = row.get(get_col("description")),
            size = row.get(get_col("size")),
            colour = row.get(get_col("colour")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),  # Note: products use "cost_price"
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),  # products: "stg_price", clothing: "stgretailprice"
            tarriff = row.get(get_col("tarriff")),
            brand = row.get(get_col("brand")),
            product_type = row.get(get_col("product_type")),
            web = row.get(get_col("web")),
            country = row.get(get_col("country")),
            country_code = row.get(get_col("country_code")),
            idx = line_number
        )
        clothes.append(clothing)
    return clothes



def check_duplicates(items: list[Product | Clothing], full_list: list, attr: str) -> dict[int, int]:
    """ Returns dictionary of what item codes are already used in the full list.
        attr should be entered as the class variable name 
    """
    duplicates = {}
    for item in items:
        value = normalizer((getattr(item, attr, None)))
        if value in full_list:
            duplicates[value] = full_list.index(value)
    return duplicates



def duplicate_barcodes(items: list[Product | Clothing], attr:str) -> list[str]:
    """ Checks to see if any products in new product file has the same barcodes."""
    barcode_to_code = defaultdict(list)
    error_list = []

    for item in items:
        if item.barcode:  # Skip empty or None
            id = normalizer(getattr(item, attr, None))
            barcode_to_code[item.barcode].append((id, item.excel_line))

    for barcode, codes in barcode_to_code.items():
        if len(codes) > 1:
            detail = ", ".join([f"{code} (line {line})" for code, line in codes])
            error_list.append(f"Barcode {barcode} is shared by: {detail}")
            # print(f"Barcode {barcode} is shared by Products: {plu_list}")
            # st.write(f"Barcode {barcode} is shared by Products: {plu_list}")

    if len(error_list) > 0:
        return error_list
    return None



def check_internal_duplicates(items: list[Product | Clothing], attr:str) -> dict[int, int]:
    """ Checks if there are any duplicate codes within the new file
        attr should be entered as the class variable name """
    errors = []
    values = [normalizer(getattr(item, attr, None)) for item in items]
    counts = Counter(values)
    for code, count in counts.items():
        if count > 1:
            lines = [item.excel_line for item in items if normalizer(getattr(item, attr, None)) == code]
            errors.append(f"Code: {code} appears {count} times on lines {lines}")
    return errors


def check_clothing_duplicates(items: list[Clothing]):
    """ Check if there are duplicate clothing items within a new file. 
        Clothing is done differently since there can be multiple style codes with different sizes.
    """
    exists = set()
    errors = []

    for item in items:
        key = (item.style_code, item.size, item.colour)
        if key in exists:
            errors.append(f"Duplicate Style {item.style_code} with size {item.size} on line {item.excel_line}")
        else:
            exists.add(key)
    return errors




# def check_types_in_column(values: list):
#     type_counts = Counter(type(v).__name__ for v in values)
#     print("Data types in list:")
#     for t, count in type_counts.items():
#         print(f"{t}: {count}")

        
# full_list = read_column("full_clothing_listing.xlsx", "PLU Code")
# check_types_in_column(full_list)




# products = load_products(CLOTHING_UPLOAD)
# full_list = read_column(FULL_CLOTHING, "stylecode")
# print(products[:10])
# print(full_list[:10])

