import pandas as pd
import streamlit as st

st.title("PLU Duplicate Checker")

# Upload section
javado_file = st.file_uploader("Upload JAVADO Excel", type=["xlsx"])
active_file = st.file_uploader("Upload PLU Active List", type=["xlsx"])

if javado_file and active_file:
    # Read files
    javado_df = pd.read_excel(javado_file)
    active_df = pd.read_excel(active_file)

    # Clean headers
    javado_df.columns = javado_df.columns.str.strip()
    active_df.columns = active_df.columns.str.strip()

    # Extract product dict
    product_dict = javado_df.set_index("plu code").to_dict("index")
    all_plu = active_df["PLU"].dropna().tolist()

    # Check duplicates
    duplicates = {
        key: all_plu.index(key) for key in product_dict if key in all_plu
    }

    # Show results
    if duplicates:
        st.success(f"{len(duplicates)} duplicate(s) found.")
        st.write("### Duplicate PLUs:")
        st.dataframe(pd.DataFrame({
            "PLU Code": list(duplicates.keys()),
            "Line Number in PLU Active": [i + 1 for i in duplicates.values()]
        }))
    else:
        st.info("No duplicates found.")
