from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
from tools import *




class Clothing:
    def __init__(self, code, description, size, colour, subgroup, supplier_code, season, 
                 main_supplier, cost_price, barcode, vat_rate, rrp, sell_price, stg_price, 
                 tarriff, brand, product_type, web, country, country_code, idx=None):
        
        self.style_code = code
        self.description = description
        self.size = size
        self.colour = colour
        self.subgroup = subgroup
        self.supplier_code = supplier_code
        self.season = season
        self.main_supplier = main_supplier
        self.cost = cost_price
        self.barcode = barcode
        self.vat_rate = vat_rate
        self.rrp = rrp
        self.sell_price = sell_price
        self.stg_price = stg_price
        self.tarriff = tarriff
        self.brand = brand
        self.product_type = product_type
        self.web = web
        self.country = country
        self.country_code = country_code
        self.excel_line = idx



    def __repr__(self):
        return f"Clothing Item: {self.style_code} | {self.description} | {self.size, self.colour}"


    def __str__(self):
        return f"Clothing Item: {self.style_code} | {self.description} | {self.size, self.colour}"


    def style_len(self):
        """ Checks if any products have a style code length over 12"""
        if len(str(self.style_code)) > 12:
            return f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Clothing item: {self.style_code} has Style Code length of {len(str(self.style_code))}. Must be under 10."
            # print(f"Product: {self.style_code} has Style Code length of {len(str(self.style_code))}. Must be under 12.")
            # st.write(f"Product: {self.style_code} has Style Code length of {len(str(self.style_code))}. Must be under 12.")


    def colour_len(self):
        """ Checks if any products have a color code length over 10"""
        if len(str(self.colour)) > 10:
            return f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Clothing item: {self.style_code} has Colour Code length of {len(str(self.colour))}. Must be under 10."
            # print(f"Product: {self.style_code} has Style Code length of {len(str(self.style_code))}. Must be under 12.")
            # st.write(f"Product: {self.style_code} has Style Code length of {len(str(self.style_code))}. Must be under 12.")



    def desc_len(self):
            """ Checks if any products have a Description length over 50"""
            if len(self.description) > 50:
                return(f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Item: {self.style_code} has description length of {len(str(self.description))}. Must be under 50.")
                # print(f"Product: {self.plu_code} has description length of {len(str(self.description))}. Must be under 50.")
                # st.write(f"Product: {self.plu_code} has description length of {len(str(self.plu_code))}. Must be under 15.")






