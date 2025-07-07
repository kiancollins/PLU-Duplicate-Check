import pandas as pd
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
import doctest


BAD_CHARS = set("',%")


# def smart_parse(value):
#     """Converts pure numbers to int. Leaves mixed/letter/symbol codes as lowercased strings.
#         Extremely helpful for making sure all numbers continue being read as numbers and everything else is read as strings"""
#     value_str = str(value).strip()
    
#     # If it's all digits (optionally ending in .0), treat as numeric
#     if value_str.replace('.', '', 1).isdigit():
#         try:
#             return int(float(value_str))  # Handles 487170.0 or "29899.0"
#         except ValueError:
#             pass  # fall back to string below

#     # Else return cleaned, lowercased string
#     return value_str


def normalizer(value):
    """ Given value is outputted as a string."""
    return str(value).strip()



def read_column(file_path, column_name) -> list:
    """Find the given column name and return that column as a list.
    Leaves numbers as numbers; strips strings."""
    try:
        df = pd.read_excel(file_path)
        target = column_name.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

        for col in df.columns:
            normalized = col.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
            if normalized == target:
                return df[col].dropna().apply(lambda x: x.strip() if isinstance(x, str) else x).tolist()
        
        print(f"Column '{column_name}' not found.")
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

