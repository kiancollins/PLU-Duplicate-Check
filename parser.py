import pandas as pd
from product_class import Product
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st


# # print(pd.__version__)
# JAVADO = "0107025 GARDEN FRESH.xlsx" #"JAVADO UPLOAD.xlsx"
# PLU_ACTIVE = "PLU-Active-List.xlsx"
# TEST_PLU_CODES = [123456, 543216, 483917, 391034, 320110, 481326] #last 2 are real products




def load_products(path: str) -> list[Product]:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    products = []
    for _, row in df.iterrows():
        product = Product(
            code = row.get('plu code'),
            description = row.get('Description'),
            subgroup = row.get('Sub Group'),
            supplier_code = row.get('3 Digit Supplier'),
            season = row.get('Season'),
            supplier_main = row.get('Main Supplier'),
            cost_price = row.get('cost price'),
            barcode = row.get('barcode'),
            vat_rate = row.get('Vat Rate'),
            rrp = row.get('RRP'),
            sell_price = row.get('Selling Price'),
            stg_price = row.get('Stg Price'),        # <-- safer access
            tarriff = row.get('Tarriff Code'),
            web = row.get('Web')
        )
        products.append(product)


    return products


def get_all_plu(path: str) -> list[int]:
    """ Read an excel of all AVOCA products into a list of PLU codes """
    plu_df = pd.read_excel(path)
    plu_df.columns = plu_df.columns.str.strip() #remove header
    all_plu = plu_df["PLU"].tolist()
    return all_plu


def check_duplicates(products: list[Product], all_products: list) -> dict[int, int]:
    """ Returns dictionary of duplicate products' codes and what line they are at
    """
    duplicates = {}
    for product in products:
        if product.plu_code in all_products:
            duplicates[product.plu_code] = all_products.index(product.plu_code)
    return duplicates


def duplicate_barcodes(products: list[Product]):

    barcode_to_plu = defaultdict(list)
    error_list = []
    for product in products:
        if product.barcode:  # Skip empty or None
            barcode_to_plu[product.barcode].append(product.plu_code)

    for barcode, plu_list in barcode_to_plu.items():
        if len(plu_list) > 1:
            error_list.append(f"Barcode {barcode} is shared by Products: {plu_list}")
            # print(f"Barcode {barcode} is shared by Products: {plu_list}")
            # st.write(f"Barcode {barcode} is shared by Products: {plu_list}")

    if len(error_list) > 0:
        return error_list
    return None






# def main():

#     products = load_products(JAVADO)
#     # for product in products:
#     #     print(product)
#     # #     print(product.barcode)
#     # #     print(product.tarriff)

#     all_products = get_all_plu(PLU_ACTIVE)
#     # print(all_products)

#     output = check_duplicates(products, all_products) # Output after duplicate check
#     # print(output)



#     # for i in range(5):
#     #    print(all_products[i])

#     # for key, value in output.items():
#     #    print(f"Duplicate item with PLU: {key} at line {(value)}")
   
#     plu_errors = []
#     desc_len_errors = []
#     bad_char_errors = []
#     decimal_errors = []

#     for product in products:
#         if product.plu_len() is not None:
#             plu_errors.append(product.plu_len())

#     for product in products:
#         if product.desc_len() is not None:
#             desc_len_errors.append(product.desc_len())

#     for product in products:
#         if product.bad_char() is not None:
#             bad_char_errors.append(product.bad_char())
   
#     for product in products:
#         if product.decimal_format() is not None:
#             decimal_errors.append(product.decimal_format())



#     if len(plu_errors) > 0:
#         print("\n All PLU Code Length Errors:")
#         for error in plu_errors:
#             print(error)
#             # st.write(error)
#     else:
#         print("\n PLU Codes are all valid.")

#     if len(desc_len_errors) > 0:
#         print("\n All Product Description Length Errors:")
#         for error in desc_len_errors:
#             print(error)
#             # st.write(error)
#     else:
#         print("\n Product descriptions are all valid.")

    
#     if len(bad_char_errors) > 0:
#         print("\n All Unusable Character Errors:")
#         for error in bad_char_errors:
#             print(error)
#             # st.write(error)
#     else:
#         print("\n Characters are all valid.")

#     if len(decimal_errors) > 0:
#         print("\nAll Decimal Formatting Erors:")
#         for error in decimal_errors:
#             print(error)
#             # st.write(error)
#     else:
#         print("\n Decimal formatting is all valid.")

#     if duplicate_barcodes(products) is not None:
#         print("\n All Duplicate Barcode Errors:")
#         print(duplicate_barcodes(products))
#         # st.write(duplicate_barcodes(products))
#     else:
#         print("\n Barcodes are all valid.")


# if __name__ == "__main__":
#     main()

