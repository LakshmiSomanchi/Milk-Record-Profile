import streamlit as st
import pandas as pd
from datetime import date
import io

# --- Page Configuration ---
st.set_page_config(page_title="Milk Record Profile", page_icon="🐄", layout="wide")

# --- CSS to make it look like a form ---
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        color: #2E4053;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2em;
        color: #566573;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<p class="main-title">Dairy Excellence Initiative</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Milk Record Profile</p>', unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: The "Profile" Section (Top half of your physical form) ---
with st.sidebar:
    st.header("📋 1. Profile Details")
    
    # Farmer Identity
    st.subheader("Farmer Information")
    farmer_name = st.text_input("Farmer Name")
    village_name = st.text_input("Village Name")
    producer_id = st.text_input("Producer ID")
    hpc_code = st.text_input("HPC Code")
    
    st.markdown("---")
    
    # Cow Identity
    st.subheader("Cow Information")
    cow_id = st.text_input("Cow Identity Number/Mark")
    breed = st.text_input("Breed")
    
    col_cow1, col_cow2 = st.columns(2)
    with col_cow1:
        num_calvings = st.number_input("No. of Calvings", min_value=0, step=1)
    with col_cow2:
        calving_date = st.date_input("Date of Calving", value=date.today())

    # Logic for Purchased vs Farm Born (Mutually Exclusive)
    origin = st.radio("Source of Cow:", ["In Farm Born", "Purchased"])
    
    st.markdown("---")
    
    # Feeding Profile
    st.subheader("Feeding Profile")
    
    # Checkboxes for Feed Types
    cattle_feed = st.checkbox("Cattle Feed")
    own_feed = st.checkbox("Own Feed")
    
    if cattle_feed or own_feed:
        qty_fed = st.number_input("Qty Fed (Kgs)", min_value=0.0, step=0.5)
        brand_name = st.text_input("Brand Name")
    else:
        qty_fed = 0
        brand_name = "N/A"

    feeding_method = st.selectbox("Grazing Method", ["Grazing", "Stall Feeding", "Both"])
    
    st.markdown("**Supplements & Fodder:**")
    c1, c2 = st.columns(2)
    with c1:
        green_fodder = st.checkbox("Green Fodder")
        dry_fodder = st.checkbox("Dry Fodder")
        silage = st.checkbox("Silage")
        water_247 = st.checkbox("24/7 Water")
    with c2:
        calcium = st.checkbox("Calcium")
        mineral_mix = st.checkbox("Mineral Mixture")
        ummb = st.checkbox("UMMB")

# --- MAIN PAGE: The "Table" Section (Bottom half of your physical form) ---

st.header("📝 2. Daily Milk Record")

# Initialize Session State for the table
if 'data_entries' not in st.session_state:
    st.session_state.data_entries = []

# Input Form for Daily Data
with st.form("daily_log", clear_on_submit=True):
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        entry_date = st.date_input("Date", value=date.today())
    with col2:
        # Milk Production
        st.markdown("**Produced (Ltrs)**")
        morning_milk = st.number_input("Morning", min_value=0.0, step=0.1, key="m_milk")
        evening_milk = st.number_input("Evening", min_value=0.0, step=0.1, key="e_milk")
    with col3:
        # Consumption
        st.markdown("**Consumption**")
        house_cons = st.number_input("Household", min_value=0.0, step=0.1, key="h_cons")
        calf_cons = st.number_input("Calf", min_value=0.0, step=0.1, key="c_cons")
    with col4:
        # Extra Info
        st.markdown("**Details**")
        remarks = st.text_input("Remarks", placeholder="-")
        visitor_sign = st.text_input("Visitor Sign", placeholder="Name")
    
    with col5:
        st.write("###") # Spacer
        st.write("###") # Spacer
        submit_btn = st.form_submit_button("➕ Add Entry", type="primary")

    if submit_btn:
        # Auto-Calculation logic
        total_produced = morning_milk + evening_milk
        total_consumed = house_cons + calf_cons
        milk_poured_lpd = total_produced - total_consumed
        
        # Create record dictionary
        record = {
            "Date": entry_date,
            "Morning (Ltrs)": morning_milk,
            "Evening (Ltrs)": evening_milk,
            "Household (Ltrs)": house_cons,
            "Calf (Ltrs)": calf_cons,
            "Milk Poured (LPD)": milk_poured_lpd, # Auto-calculated
            "Remarks": remarks,
            "Visitor Signature": visitor_sign
        }
        
        st.session_state.data_entries.append(record)
        st.success("Entry Added!")

# --- Display Data Table ---
if st.session_state.data_entries:
    df = pd.DataFrame(st.session_state.data_entries)
    
    # Format the date to look nicer
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%m-%Y')
    
    st.table(df) # st.table matches the paper look better than st.dataframe

    # --- CSV Generation for Download ---
    # We need to construct a file that looks like the paper form (Header + Table)
    
    # 1. Create the Profile Header Text
    profile_info = f"""DAIRY EXCELLENCE INITIATIVE - MILK RECORD PROFILE
--------------------------------------------------
Farmer Name: {farmer_name}, Village: {village_name}
Producer ID: {producer_id}, HPC Code: {hpc_code}
Cow ID: {cow_id}, Breed: {breed}
Calvings: {num_calvings}, Calving Date: {calving_date}
Cow Origin: {origin}
Feeding: {feeding_method}, Qty: {qty_fed}kg, Brand: {brand_name}
Supplements: Green Fodder: {green_fodder}, Dry: {dry_fodder}, Silage: {silage}, Mineral: {mineral_mix}, UMMB: {ummb}
--------------------------------------------------
"""
    # 2. Convert DataFrame to CSV string
    csv_buffer = io.StringIO()
    # Write the profile info first
    csv_buffer.write(profile_info)
    # Write the table data
    df.to_csv(csv_buffer, index=False)
    
    # 3. Create Download Button
    file_name_str = f"Milk_Record_{farmer_name}_{date.today()}.csv"
    st.download_button(
        label="📥 Download Completed Form",
        data=csv_buffer.getvalue(),
        file_name=file_name_str,
        mime="text/csv"
    )

else:
    st.info("Start adding daily records using the form above to see the table.")
