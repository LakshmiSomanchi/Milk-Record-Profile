import streamlit as st
import pandas as pd
from datetime import date

# --- Page Configuration ---
st.set_page_config(page_title="Milk Record Profile", page_icon="🐄", layout="wide")

st.title("🐄 Dairy Excellence Initiative: Milk Record Profile")
st.markdown("---")

# --- Section 1: Farmer & Cow Profile (Sidebar for clean layout) ---
st.sidebar.header("1. General Profile")

# Farmer Details
farmer_name = st.sidebar.text_input("Farmer Name")
village_name = st.sidebar.text_input("Village Name")
producer_id = st.sidebar.text_input("Producer ID")
hpc_code = st.sidebar.text_input("HPC Code")

st.sidebar.markdown("---")
st.sidebar.header("2. Cow Details")

# Cow Details
cow_id = st.sidebar.text_input("Cow Identity Number / Mark")
breed = st.sidebar.text_input("Breed")
num_calvings = st.sidebar.number_input("No. of Calvings", min_value=0, step=1)
date_calving = st.sidebar.date_input("Date of Calving", value=date.today())

# Origin (Logic to handle mutually exclusive Y/N)
cow_origin = st.sidebar.radio("Cow Origin", ["In Farm Born", "Purchased"])
cow_purchased_yn = "Yes" if cow_origin == "Purchased" else "No"
in_farm_born_yn = "Yes" if cow_origin == "In Farm Born" else "No"

st.sidebar.markdown("---")
st.sidebar.header("3. Feeding Profile")

# Feeding Details
col1, col2 = st.sidebar.columns(2)
with col1:
    cattle_feed_yn = st.selectbox("Cattle Feed?", ["Yes", "No"])
    own_feed_yn = st.selectbox("Own Feed?", ["Yes", "No"])
    green_fodder_yn = st.selectbox("Green Fodder?", ["Yes", "No"])
    silage_yn = st.selectbox("Silage?", ["Yes", "No"])
    calcium_yn = st.selectbox("Calcium?", ["Yes", "No"])

with col2:
    mineral_mix_yn = st.selectbox("Mineral Mixture?", ["Yes", "No"])
    ummb_yn = st.selectbox("UMMB?", ["Yes", "No"])
    water_247_yn = st.selectbox("24/7 Water?", ["Yes", "No"])
    dry_fodder_yn = st.selectbox("Dry Fodder?", ["Yes", "No"])

qty_fed = st.sidebar.number_input("Qty Fed (Kgs)", min_value=0.0, step=0.5)
brand_name = st.sidebar.text_input("Brand Name (if purchased)")
grazing_type = st.sidebar.selectbox("Feeding Method", ["Stall feeding", "Grazing", "Both"])

# --- Section 2: Daily Milk Record Table ---
st.header("4. Daily Milk Production Record")

# Initialize Session State to hold table data
if 'milk_data' not in st.session_state:
    st.session_state.milk_data = []

# Input Form for Daily Data
with st.form("daily_entry_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    c5, c6, c7, c8 = st.columns(4)
    
    with c1:
        entry_date = st.date_input("Date", value=date.today())
    with c2:
        morning_liters = st.number_input("Morning (Ltrs)", min_value=0.0, step=0.1)
    with c3:
        evening_liters = st.number_input("Evening (Ltrs)", min_value=0.0, step=0.1)
    with c4:
        # Internal Consumption
        household_cons = st.number_input("Consumption: Household (Ltrs)", min_value=0.0, step=0.1)
    with c5:
        calf_cons = st.number_input("Consumption: Calf (Ltrs)", min_value=0.0, step=0.1)
    with c6:
        remarks = st.text_input("Remarks")
    with c7:
        visitor_sig = st.text_input("Visitor Name/Signature")
    
    # Calculate Milk Poured automatically
    submitted = st.form_submit_button("Add Record to Table")

    if submitted:
        total_prod = morning_liters + evening_liters
        total_cons = household_cons + calf_cons
        poured_lpd = total_prod - total_cons
        
        new_entry = {
            "Date": entry_date,
            "Morning (Ltrs)": morning_liters,
            "Evening (Ltrs)": evening_liters,
            "Household Cons. (Ltrs)": household_cons,
            "Calf Cons. (Ltrs)": calf_cons,
            "Milk Poured (LPD)": poured_lpd,
            "Remarks": remarks,
            "Visitor Signature": visitor_sig
        }
        st.session_state.milk_data.append(new_entry)
        st.success("Record Added!")

# Display the Table
if len(st.session_state.milk_data) > 0:
    df_table = pd.DataFrame(st.session_state.milk_data)
    st.dataframe(df_table, use_container_width=True)

    # --- Section 3: Download Logic ---
    st.markdown("---")
    st.header("Download Final Profile")
    
    # We combine Profile Info and Table Info into one CSV for download
    # We create a summary string of the profile to add at the top
    
    # Convert Dataframe to CSV
    csv_data = df_table.to_csv(index=False)
    
    # Create a nice filename
    filename = f"Milk_Record_{farmer_name}_{date.today()}.csv"
    
    # Create a layout for the download text
    profile_text = (
        f"Farmer Name: {farmer_name}\n"
        f"Village: {village_name}\n"
        f"Producer ID: {producer_id}\n"
        f"Cow ID: {cow_id}\n"
        f"Breed: {breed}\n"
        f"Feeding Method: {grazing_type}\n"
        f"-----------------------------\n"
    )
    
    # Combine profile text and CSV data
    final_output = profile_text + csv_data

    st.download_button(
        label="📥 Download Record (CSV)",
        data=final_output,
        file_name=filename,
        mime="text/csv"
    )
else:
    st.info("Please add at least one daily record to enable downloading.")
