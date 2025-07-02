import pandas as pd
from product_class import Product
from decimal import Decimal
from collections import Counter, defaultdict
import streamlit as st
from fixes import update_all


NEW_PRODUCTS = "0107025 GARDEN FRESH.xlsx" 
NEW_PRODUCTS_2 = "JAVADO UPLOAD.xlsx"
PLU_ACTIVE = "PLU-Active-List.xlsx"
# TEST_PLU_CODES = [123456, 543216, 483917, 391034, 320110, 481326] #last 2 are real products



def load_products(path: str) -> list[Product]:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

    products = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get('plucode'),
            description = row.get('description'),
            subgroup = row.get('subgroup'),
            supplier_code = row.get('3digitsupplier'),
            season = row.get('season'),
            supplier_main = row.get('mainsupplier'),
            cost_price = row.get('costprice'),
            barcode = row.get('barcode'),
            vat_rate = row.get('vatrate'),
            rrp = row.get('rrp'),
            sell_price = row.get('sellingprice'),
            stg_price = row.get('stgprice'),   
            tarriff = row.get('tarriffcode'),
            web = row.get('web'),
            idx = line_number
        )
        products.append(product)

    return products


def get_all_plu(path: str) -> list[int]:
    """ Read an excel of all AVOCA products into a list of PLU codes """
    # plu_df = pd.read_excel(path)
    # plu_df.columns = plu_df.columns.str.lower().str.strip().str.replace(" ", "")
    # # print("Columns after normalization:", plu_df.columns.tolist())
    # return plu_df["plu"].tolist()

    plu_df = pd.read_excel(path)
    print("Raw columns:", plu_df.columns.tolist())  # <-- print raw header
    plu_df.columns = plu_df.columns.str.lower().str.strip().str.replace(" ", "")
    print("Normalized columns:", plu_df.columns.tolist())  # <-- print normalized header

    if "plu" not in plu_df.columns:
        raise KeyError("Missing 'plu' column after normalization.")

    return plu_df["plu"].tolist()


def check_duplicates(products: list[Product], all_products: list) -> dict[int, int]:
    """ Returns dictionary of duplicate products' codes and what line they are at.
    """
    duplicates = {}
    for product in products:
        if product.plu_code in all_products:
            duplicates[product.plu_code] = all_products.index(product.plu_code)
    return duplicates


def duplicate_barcodes(products: list[Product]) -> list[str]:
    """ Checks to see if any products in new product file has the same barcodes."""
    barcode_to_plu = defaultdict(list)
    error_list = []

    for product in products:
        if product.barcode:  # Skip empty or None
            barcode_to_plu[product.barcode].append((product.plu_code, product.excel_line))

    for barcode, plu_list in barcode_to_plu.items():
        if len(plu_list) > 1:
            detail = ", ".join([f"{plu} (line {line})" for plu, line in plu_list])
            error_list.append(f"Barcode {barcode} is shared by: {detail}")
            # print(f"Barcode {barcode} is shared by Products: {plu_list}")
            # st.write(f"Barcode {barcode} is shared by Products: {plu_list}")

    if len(error_list) > 0:
        return error_list
    return None


def find_internal_duplicates(products: list[Product]) -> list[str]:
    """Checks for duplicate PLU codes within the new product file."""
    counts = Counter(product.plu_code for product in products)
    errors = []
    for plu, count in counts.items():
        if count > 1:
            lines = [product.excel_line for product in products if product.plu_code == plu]
            errors.append(f"PLU Code: {plu} appears {count} times on lines {lines}")
    return errors


# df = get_all_plu(PLU_ACTIVE)


# products = load_products(NEW_PRODUCTS_2)
# for product in products:
#     print(product.excel_line)


# df = pd.read_excel(NEW_PRODUCTS_2)

# df.columns = df.columns.str.lower().str.replace(" ", "")
# fixed_df, changes = update_all(df)

# print("\n=== All Fixes ===")
# for change in changes:
#     print(change)






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

