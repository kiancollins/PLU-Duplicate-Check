import pandas as pd
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
import doctest


BAD_CHARS = set("',%")
POSSIBLE_PLU = ["plu", "plu code", "plucode", "plu-code", "plu_code"]
HEADER_MAP = {
    "plu_code": ["plu", "plu code", "plucode", "plu-code"],
    "style_code": ["stylecode, style code, style-code, style_code"],
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




