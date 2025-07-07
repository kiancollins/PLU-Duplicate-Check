import pandas as pd
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
import doctest


BAD_CHARS = set("',%")
POSSIBLE_PLU = ["plu", "plu code", "plucode", "plu-code", "plu_code"]
POSSIBLE_STYLE_CODES = ["style code", "stylecode", "style_code", "style-code"]

PRODUCT_HEADER_MAP = {
    "plu_code": ["plu", "plu code", "plucode", "plu-code", "plu_code"],
    "description": ["description", "desc"],
    "subgroup": ["subgroup", "category"],
    "supplier_code": ["3digitsupplier", "suppliercode"],
    "season": ["season"],
    "main_supplier": ["mainsupplier", "main supplier"],
    "cost_price": ["costprice", "cost"],
    "barcode": ["barcode", "bar code"],
    "vat_rate": ["vatrate", "vat"],
    "rrp": ["rrp"],
    "sell_price": ["sellingprice", "sellprice"],
    "stg_price": ["stgprice", "stgretailprice"],
    "tarriff": ["tarriffcode", "tarrif"],
    "web": ["web"],
    
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
    "vat_rate": ["vatrate", "vat rate", "vat"],
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
    try:
        df = pd.read_excel(file_path)
        normalized_cols = {normalize_header(col): col for col in df.columns}

        for name in possible_names:
            normalized = normalize_header(name)
            if normalized in normalized_cols:
                return df[normalized_cols[normalized]].dropna().apply(normalizer).tolist()
        
        print(f"Column Name not found: Looking in {possible_names}")
        return []

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    

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
    """ Identify column based on a possible names reference dictionary """

    normalized_cols = {normalize_header(col): col for col in df.columns}
    for name in possible_names:
        key = normalize_header(name)
        if key in normalized_cols:
            return normalized_cols[key]
    return None


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

