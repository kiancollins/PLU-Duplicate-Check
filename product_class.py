from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st


BAD_CHARS = set("',%")


class Product:

    def __init__(self, code, description, subgroup, supplier_code, season, 
                 supplier_main, cost_price, barcode, vat_rate, rrp, sell_price, stg_price, tarriff, web, idx=None):
        self.plu_code = code
        self.description = description
        self.subgroup = subgroup
        self.supplier_code = supplier_code
        self.season = season
        self.supplier_main = supplier_main
        self.cost = cost_price
        self.barcode = barcode
        self.vat_rate = vat_rate
        self.rrp = rrp
        self.sell_price = sell_price
        self.stg_price = stg_price
        self.tarriff = tarriff
        self.web = web
        self.excel_line = idx


    def __repr__(self):
        return f"Product {self.plu_code}: {self.description}>"


    def __str__(self):
        return f"Product: {self.plu_code} | {self.description}"


    def plu_len(self):
        """ Checks if any products have a PLU Code length over 15"""
        if len(str(self.plu_code)) > 15:
            return f"Line {self.excel_line}  |  Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15."
            # print(f"Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15.")
            # st.write(f"Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15.")

    def plu_duplicates(self):
        ...
        
    def desc_len(self):
        """ Checks if any products have a Description length over 50"""
        if len(self.description) > 50:
            return(f"Line {self.excel_line}  |  Product: {self.plu_code} has description length of {len(str(self.description))}. Must be under 50.")
            # print(f"Product: {self.plu_code} has description length of {len(str(self.description))}. Must be under 50.")
            # st.write(f"Product: {self.plu_code} has description length of {len(str(self.plu_code))}. Must be under 15.")


    def bad_char(self) -> str:
        """ The characters ',% can't be in any product variables. Check if they have any and return where."""
        bad_fields = []
        for field, value in vars(self).items():     # Grab each variable and the value for the product
                if isinstance(value, str):          # Avoid type error
                    if any(char in value for char in BAD_CHARS):    # Check if any bad chars are in the value
                        bad_fields.append(field)
        if len(bad_fields) > 0:
            return f"Line {self.excel_line}  |  Product: {self.plu_code} contains invalid character(s) {BAD_CHARS} in {bad_fields}"
            # print(f"Product: {self.plu_code} contains invalid character(s) {BAD_CHARS} in {bad_fields}")
            # st.write(f"Product: {self.plu_code} contains invalid characters {BAD_CHARS} in {bad_fields}")


    def decimal_format(self):
        """Cost price, RRP, selling price, and trade price must all be 2 decimal places or less."""
        errors = []
        fields = { # Avoid errors if the field is empty with getattr
            'cost price': self.cost,
            'rrp': getattr(self, 'rrp', None),
            'selling price': getattr(self, 'sell_price', None),
            'trade price': getattr(self, 'stg_price', None)
        }

        for key, value in fields.items():
            if value != None:
                try:
                    decimal_value = Decimal(str(value))
                    if -(decimal_value.as_tuple().exponent) > 2:
                        errors.append(key)
                except Exception as e:
                    ... # Often times trade price (stg_price) will just be empty

        if len(errors) > 0:
            return f"Line {self.excel_line}  |  Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less"
            # print(f"Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less")
            # st.write(f"Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less")

