import pandas as pd

# print(pd.__version__)
JAVADO = "JAVADO_UPLOAD.xlsx"
PLU_ACTIVE = "PLU-Active-List.xlsx"
TEST_PLU_CODES = [123456, 543216, 483917, 391034, 320110, 481326] #last 2 are real products


def excel_to_dict(path: str) -> dict[int, dict]:
    """ Reads an excel file into a dictionary.
    Probably works only in the correct format. 
    Will probably need to create different functions based on different spreadsheets
    """

    products_df = pd.read_excel(path) # original name has space instead of underscore  
    # print(products_df.columns.tolist())

    # keys are from the 'plu code' column
    products_df.columns = products_df.columns.str.strip()  # Remove header
    product_dict = products_df.set_index('plu code').to_dict('index')

    return product_dict



def get_all_plu(path: str) -> list[int]:
    """ Read an excel of all AVOCA products into a list of PLU codes """
    plu_df = pd.read_excel(path)
    plu_df.columns = plu_df.columns.str.strip() #remove header
    all_plu = plu_df["PLU"].tolist()
    return all_plu


def check_duplicates(products: dict, all_products: list) -> dict[int, int]:
    """ Returns dictionary of duplicate products' codes and what line they are at
    """
    duplicates = {}
    for key in products.keys():
        if key in all_products:
            duplicates[key] = all_products.index(key)
    return duplicates





def main():

   products_dict = excel_to_dict(JAVADO) # Dictionary of products
#    print(products_dict)

   all_products = get_all_plu(PLU_ACTIVE)
#    print(all_products)

   output = check_duplicates(products_dict, all_products) # Output after duplicate check
#    print(output)



#    for i in range(5):
#        print(all_products[i])

   for key, value in output.items():
       print(f"Duplicate item with PLU: {key} at line {(value+1)}")
   

   
if __name__ == "__main__":
    main()

