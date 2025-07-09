import pandas as pd
from product_class import Product
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
from fix_products import update_all_products
from clothing_class import Clothing
from fix_clothing import update_all_clothing
from tools import *


NEW_PRODUCTS_GARDEN = "Spreadsheets/0107025 GARDEN FRESH.xlsx" 
NEW_PRODUCTS_JAVADO = "Spreadsheets/JAVADO UPLOAD.xlsx"
PLU_ACTIVE = "Spreadsheets/PLU-Active-List.xlsx"
CLOTHING_UPLOAD = "Spreadsheets/lothing upload example.xlsx"
FULL_CLOTHING = "Spreadsheets/full_clothing_listing.xlsx"
BAD_PROD_UPLOAD = "Spreadsheets/NG New Product 080425.xlsx"


def load_products(path: str) -> tuple[list[Product], list[tuple[str, str]]]:
    """Load the new product file into a list of Product class objects"""
    expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
    header_row = detect_header_row(path, expected_headers)
    df = pd.read_excel(path, header=header_row)
    df.columns = [normalize_header(c) for c in df.columns]


    print(df.head(5))
    print(df.columns.tolist())
    messages = []
    
    # Pre-resolve all needed column names
    col_map = {}
    for key in PRODUCT_HEADER_MAP:
        col, msg, msg_type = find_column(df, PRODUCT_HEADER_MAP[key])
        col_map[key] = col  # May be None if not found
        if msg:
            messages.append((msg, msg_type))

    # print("\n=== Final resolved columns ===")
    # for key, val in col_map.items():    
    #     print(f"{key}: {val}")


    # Build Product objects using resolved column names
    products = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get(col_map["plu_code"]),
            description = row.get(col_map["description"]),
            subgroup = row.get(col_map["subgroup"]),
            supplier_code = row.get(col_map["supplier_code"]),
            season = row.get(col_map["season"]),
            main_supplier = row.get(col_map["main_supplier"]),
            cost_price = row.get(col_map["cost_price"]),
            barcode = row.get(col_map["barcode"]),
            vat_rate = row.get(col_map["vat_rate"]),
            rrp = row.get(col_map["rrp"]),
            sell_price = row.get(col_map["sell_price"]),
            stg_price = row.get(col_map["stg_price"]),
            tarriff = row.get(col_map["tarriff"]),
            web = row.get(col_map["web"]),
            idx = line_number
        )
        products.append(product)

    return products, messages


def load_clothing(path: str) -> tuple[list[Clothing], list[tuple[str, str]]]:
    """Load the new clothing file into a list of Clothing class objects"""
    expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
    header_row = detect_header_row(df, expected_headers)  # <- use your existing detection function
    df = pd.read_excel(path, header=header_row)
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")
    df.columns = [normalize_header(col) for col in df.columns]

    messages = []
    col_map = {}

    # Step 1: Resolve headers
    for key, possible_names in CLOTHING_HEADER_MAP.items():
        col, msg, msg_type = find_column(df, possible_names)
        if msg:
            messages.append((msg, msg_type))
        col_map[key] = col

    # Step 2: Check for required columns
    for key, col in col_map.items():
        if col is None and key in ["style_code", "description"]:  # Add more keys if needed
            raise ValueError(f"Missing required column: {key}")

    # Step 3: Build clothing objects
    clothes = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        clothing = Clothing(
            code=row.get(col_map["style_code"]),
            description=row.get(col_map["description"]),
            size=row.get(col_map["size"]),
            colour=row.get(col_map["colour"]),
            subgroup=row.get(col_map["subgroup"]),
            supplier_code=row.get(col_map["supplier_code"]),
            season=row.get(col_map["season"]),
            main_supplier=row.get(col_map["main_supplier"]),
            cost_price=row.get(col_map["cost_price"]),
            barcode=row.get(col_map["barcode"]),
            vat_rate=row.get(col_map["vat_rate"]),
            rrp=row.get(col_map["rrp"]),
            sell_price=row.get(col_map["sell_price"]),
            stg_price=row.get(col_map["stg_price"]),
            tarriff=row.get(col_map["tarriff"]),
            brand=row.get(col_map["brand"]),
            product_type=row.get(col_map["product_type"]),
            web=row.get(col_map["web"]),
            country=row.get(col_map["country"]),
            country_code=row.get(col_map["country_code"]),
            idx=line_number
        )
        clothes.append(clothing)

    return clothes, messages




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



def detect_header_row(file_path, expected_headers, max_rows=10):
    preview_df = pd.read_excel(file_path, header=None, nrows=max_rows)

    best_row = 0
    best_score = 0

    # print("===== SCANNING HEADER CANDIDATES =====")
    for i in range(min(max_rows, len(preview_df))):
        row = preview_df.iloc[i].fillna("").astype(str).tolist()
        normalized_row = [normalize_header(cell) for cell in row]

        # print(f"\nRow {i}: {row}")
        # print(f"Normalized: {normalized_row}")

        matches = 0
        for header in expected_headers:
            norm_header = normalize_header(header)
            best_header_score = max(char_match(norm_header, col) for col in normalized_row)
            if best_header_score >= THRESHOLD:
                matches += 1
            # print(f"→ Checking header '{header}' (normalized: '{norm_header}') → best score: {best_header_score:.2f}")

        match_ratio = matches / len(expected_headers)
        # print(f"Match ratio for row {i}: {match_ratio:.2f}")

        if match_ratio > best_score:
            best_score = match_ratio
            best_row = i
            # print(f" \n ------------ \n {best_row}, {best_score}")

    # print(f"===== BEST ROW: {best_row} (score: {best_score:.2f}) =====")
    return (best_row) if best_score >= 0.3 else 0






# def check_types_in_column(values: list):
#     type_counts = Counter(type(v).__name__ for v in values)
#     print("Data types in list:")
#     for t, count in type_counts.items():
#         print(f"{t}: {count}")

        
# full_list = read_column("full_clothing_listing.xlsx", "PLU Code")
# check_types_in_column(full_list)




# products = load_products(BAD_PROD_UPLOAD)
# full_list = read_column(PLU_ACTIVE, "plu_code")
# # print(products[:10])
# # print(full_list[:10])

