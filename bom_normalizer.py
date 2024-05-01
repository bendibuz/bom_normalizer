import streamlit as st
import pandas as pd
import re


#------------------------------------------------------

def extract_integer(s):
    # Extracting integers from the string
    match = re.search(r'\d+', s)
    return int(match.group()) if match else None

def convert_bom(df, level, partno):
# Stack to keep track of parents
    parent_stack = []
    # Function to assign parents
    def assign_parent(row):
        # global parent_stack
        while len(parent_stack) <= row[level]:
            parent_stack.append(None)
        if row[level] > 0:
            row['Parent'] = parent_stack[row[level]-1]
        parent_stack[row[level]] = row[partno]
        return row

    # Applying the function to each row of the DataFrame
    df['Parent'] = ""
    df = df.apply(assign_parent, axis=1)
    return df

#------------------------------------------------------
st.set_page_config(
    page_title="BOM Converter",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'About': "Use this app to convert a BOM to the format accepted by the PDW."
    }
)

st.title("BOM Converter")
st.subheader('''Upload a :gray[.csv] or :green[.xlsx] file then follow the prompts to convert your BOM!''')


skip_rows = st.number_input("How many rows to skip when uploading BOM?", min_value=0, max_value=100, value=0)

uploaded_file = st.file_uploader("Upload a .csv or .xlsx file", type=["csv", "xlsx", "xls"])
# df = pd.DataFrame(uploaded_file)

def part_v_component(parent):
    if parent == "":
        return 'Product'
    else: return 'Component'

def load_sheet(file):
    xls = pd.ExcelFile(file)
    sheet_names = xls.sheet_names
    return sheet_names

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8-sig')


if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            user_BOM = pd.read_csv(uploaded_file, error_bad_lines=False, encoding="utf-8-sig", skiprows=skip_rows)
        else:
            sheet_names = load_sheet(uploaded_file)
            sheet = st.selectbox('Choose a sheet', sheet_names)
            if sheet:
                user_BOM = pd.read_excel(uploaded_file, sheet, skiprows=skip_rows)
    except pd.errors.EmptyDataError:
            st.error("There was a problem with the uploaded file. It may be empty, or in a format that is not parsable as a dataframe.")

    if not user_BOM.empty:
        st.dataframe(user_BOM)
        
        level = st.selectbox('Which column represents the nesting level?', options=user_BOM.columns)
        partno = st.selectbox('Which column represents the part number?', options=user_BOM.columns)
        
        if st.button("Convert"):
            user_BOM[level] = user_BOM[level].astype(str).apply(extract_integer)
            converted = convert_bom(user_BOM, level, partno)
            converted['Part Type'] = converted["Parent"].apply(part_v_component)
            st.dataframe(converted)


            csv = convert_df(converted)

            st.download_button(
            "Download CSV",
            csv,
            "Converted_BOM.csv",
            "text/csv",
            key='download-csv'
            )            


