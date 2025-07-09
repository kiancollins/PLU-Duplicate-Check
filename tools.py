import pandas as pd
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
import doctest


BAD_CHARS = set("',%")
POSSIBLE_PLU = ["plu", "plu code", "plucode", "plu-code", "plu_code"]
POSSIBLE_STYLE_CODES = ["style code", "stylecode", "style_code", "style-code"]
THRESHOLD = 0.8 # Used in char match calls

PRODUCT_HEADER_MAP = {
    "plu_code": ["plu", "plu code", "plucode", "plu-code", "plu_code"],
    "description": ["description", "desc"],
    "subgroup": ["subgroup", "category", "sub", "subcategory"],
    "supplier_code": ["3digitsupplier", "suppliercode", "threedigitsupplier", "3digitsuppliercode", "threedigitsuppliercode"],
    "season": ["season"],
    "main_supplier": ["mainsupplier", "main-supplier", "supplier", ],
    "cost_price": ["costprice", "cost"],
    "barcode": ["barcode", "bar code"],
    "vat_rate": ["vatrate", "vat", "vatcode", "vat-code"],
    "rrp": ["rrp"],
    "sell_price": ["sellingprice", "sellprice", "priceforsell", "selling"],
    "stg_price": ["stgprice", "stgretailprice", "sterlingprice"],
    "tarriff": ["tarriffcode", "tarrif"],
    "web": ["web"]
    
}

CLOTHING_HEADER_MAP = {
    "style_code": ["stylecode", "style code", "style-code", "style_code"],
    "description": ["description", "desc"],
    "size": ["size"],
    "colour": ["colour", "color"],
    "subgroup": ["subgroup", "category", "sub group"],
    "supplier_code": ["3digitsupplier", "supplier code", "suppliercode"],
    "season": ["season"],
    "main_supplier": ["mainsupplier", "main supplier"],
    "cost_price": ["costprice", "cost price", "cost"],
    "barcode": ["barcode", "bar code"],
    "vat_rate": ["vatrate", "vat rate", "vat", "vatcode"],
    "rrp": ["rrp"],
    "sell_price": ["sellingprice", "selling price", "sellprice"],
    "stg_price": ["stgretailprice", "stg retail price", "stgprice"],
    "tarriff": ["tarriffcode", "tarriff code", "tariff", "tarrif"],
    "brand": ["brandinstore", "brand in store", "brand"],
    "product_type": ["producttype", "product type"],
    "web": ["web", "online", "website"],
    "country": ["countryoforigin", "country of origin", "origin"],
    "country_code": ["countrycode", "country code"],
}


def normalizer(value):
    """ Given value is outputted as a string."""
    return str(value)


def normalize_header(value):
    """ Given header is outputted in a normalized format"""
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def read_column(file_path, possible_names) -> list:
    """Find the given column name and return that column as a list.
    Converts all objects to strings"""
    if isinstance(possible_names, str):
        possible_names = [possible_names]
    try:
        df = pd.read_excel(file_path)
        normalized_cols = {normalize_header(col): col for col in df.columns}

    # Exact match with key map
        for name in possible_names:
            normalized = normalize_header(name)
            if normalized in normalized_cols:
                return df[normalized_cols[normalized]].dropna().apply(normalizer).tolist(), "", "skip"

    # Char match
        best_score = 0
        best_possible = None
        original_header = None
        
        for df_col_key, df_col_val in normalized_cols.items():
                for expected_name in possible_names:
                    score = char_match(expected_name, df_col_key)
                    if score > best_score:
                        best_score = score
                        best_possible = expected_name
                        original_header = df_col_val
        
        if best_score >= THRESHOLD:  # ← adjust threshold as needed
            msg = f"CHAR_MATCH updated the column header '{original_header}' to '{best_possible}' to match template spreadsheet"
            return df[best_possible].dropna().apply(normalizer).tolist(), msg, "alert"
        return [], possible_names[0], "error"

    except Exception as e:
        return [], f"Error reading {file_path}: {e}", "error"
    

def bad_char(obj, id_attr: str) -> str:
    """ The characters ',% can't be in any product variables. Check if they have any and return where.
        Input for id_attr should be the code/name of item preferred when returning an error message.
    """
    bad_fields = []
    for field, value in vars(obj).items():     # Grab each variable and the value for the product
            if isinstance(value, str):          # Avoid type error
                if any(char in value for char in BAD_CHARS):    # Check if any bad chars are in the value
                    bad_fields.append(field)

    if bad_fields:
            line = getattr(obj, "excel_line", None)
            id = getattr(obj, id_attr, None)
            return f"Line {line} \u00A0\u00A0|\u00A0\u00A0 {id} contains invalid character(s) {BAD_CHARS}"



def find_column(df: pd.DataFrame, possible_names: dict):
    """ Identify column based on a possible names reference dictionary.
        If reference dictionary doesn't work, use char match. """

    normalized_cols = {normalize_header(col): col for col in df.columns}
    for col in df.columns:
            print(f"  - '{col}' → '{normalize_header(col)}'")

    # Main: Exact match
    for name in possible_names:
        key = normalize_header(name)
        if key in normalized_cols:
            return normalized_cols[key], "", "skip"

    # Back up: Char match
    best_score = 0
    best_possible = None
    original_header = None

    for col_key in normalized_cols.keys():
            for name in possible_names:
                score = char_match(name, col_key)
                # print(f"Comparing expected: {name} vs found: {col_key} → score {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_possible = name
                    original_header = normalized_cols[col_key]
    
    if best_score >= THRESHOLD:  # ← adjust threshold as needed
        msg = f"CHAR_MATCH updated the column header '{original_header}' to '{best_possible}' to match template spreadsheet"
        return original_header, msg, "alert"
    
    print(f"No match found for key — returning None: {possible_names}")
    return None, possible_names[0], "error"


def check_missing_columns(df: pd.DataFrame, header_map: dict[str, list[str]]) -> list[str]:
    """
    Checks for missing expected headers in a DataFrame using a HEADER_MAP.
    
    Returns a list of standardized keys (like 'plu_code', 'style_code') 
    for which none of the possible column names were found.
    """
    normalized_df_cols = {normalize_header(c) for c in df.columns}
    missing = []

    for key, possibilities in header_map.items():
        found = any(normalize_header(name) in normalized_df_cols for name in possibilities)
        if not found:
            missing.append(key)
    return missing



def char_match(target: str, possible: str):
    """ Returns a score of how close two words are based on matching characters
    
    >>> char_match("costprice", "costp ricee")
    0.9

    >>> char_match("description", "descripshun")  # 2 wrong letters
    0.6363636363636364

    >>> char_match("vatcode", "vat-code")  # assuming normalize_header removes dashes
    1.0

    >>> char_match("productname", "product_id")
    0.5384615384615384

    >>> char_match("name", "nmae")  # wrong order, but same letters
    1.0

    >>> char_match("three digit supplier", "3 digit supplier")
    0.84375
    """
    target = normalize_header(target)
    possible = normalize_header(possible)
    target_list = list(target)
    possible_list = list(possible)
    unmatched_list = []

    for char in possible_list:
        if char in target_list:
            target_list.remove(char)
        else:
            unmatched_list.append(char)
        
    total_possible = len(target) + len(possible)
    total = len(unmatched_list) + len(target_list)
    score = 1 - (total / total_possible)
    return score




    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
