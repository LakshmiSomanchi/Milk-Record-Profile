import streamlit as st
import pandas as pd
from datetime import date
import io

# --- Page Configuration ---
st.set_page_config(page_title="Milk Record Profile", page_icon="🐄", layout="wide")

# --- Custom CSS for Form Look ---
st.markdown("""
    <style>
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 10px;
        margin-bottom: 10px;
        border-bottom: 2px solid #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐄 Dairy Excellence Initiative")
st.subheader("Milk Record Profile")

# ==========================================
# SECTION 1: FARMER & COW PROFILE (Static)
# ==========================================
with st.container(border=True):
    st.markdown('<p class="section-header">1. General Profile</p>', unsafe_allow_html=True)
    
    # Row 1: Farmer Details
    c1, c2, c3, c4 = st.columns(4)
    with c1: farmer_name = st.text_input("Farmer Name")
    with c2: village_name = st.text_input("Village Name")
    with c3: producer_id = st.text_input("Producer ID")
    with c4: hpc_code = st.text_input("HPC Code")

    # Row 2: Cow Details
    c5, c6, c7, c8 = st.columns(4)
    with c5: cow_id = st.text_input("Cow Identity Number/Mark")
    with c6: breed = st.text_input("Breed")
    with c7: num_calvings = st.number_input("No. of Calvings", min_value=0, step=1)
    with c8: calving_date = st.date_input("Date of Calving", value=date.today())

    # Row 3: Feed Details
    st.markdown("---")
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1: origin = st.radio("Cow Origin", ["In Farm Born", "Purchased"], horizontal=True)
    with f2: feeding_method = st.radio("Feeding Method", ["Grazing", "Stall Feeding", "Both"], horizontal=True)
    with f3: 
        c_feed = st.checkbox("Cattle Feed")
        qty_fed = st.number_input("Qty (Kgs)", value=0.0) if c_feed else 0.0

    # Supplements Checkboxes
    st.write(" **Supplements:**")
    sup1, sup2, sup3, sup4, sup5, sup6 = st.columns(6)
    with sup1: green = st.checkbox("Green Fodder")
    with sup2: dry = st.checkbox("Dry Fodder")
    with sup3: silage = st.checkbox("Silage")
    with sup4: mineral = st.checkbox("Mineral Mix")
    with sup5: ummb = st.checkbox("UMMB")
    with sup6: water = st.checkbox("24/7 Water")

# ==========================================
# SECTION 2: DAILY MILK RECORD (Editable Grid)
# ==========================================
st.markdown('<p class="section-header">2. Daily Milk Record Log</p>', unsafe_allow_html=True)
st.info("💡 Tip: You can edit the table below directly! Click on the last empty row to add a new entry.")

# 1. Setup the structure of our Dataframe
if 'milk_data' not in st.session_state:
    # Create an empty dataframe with specific columns and types
    st.session_state.milk_data = pd.DataFrame(
        columns=[
            "Date", "Morning (Ltrs)", "Evening (Ltrs)", 
            "Home Cons. (Ltrs)", "Calf Cons. (Ltrs)", 
            "Milk Poured (LPD)", "Remarks", "Visitor Sign"
        ]
    )

# 2. Configure column settings for the editor (makes it user-friendly)
column_config = {
    "Date": st.column_config.DateColumn("Date", default=date.today(), format="DD-MM-YYYY"),
    "Morning (Ltrs)": st.column_config.NumberColumn("Morning (Ltrs)", min_value=0, step=0.1, format="%.1f"),
    "Evening (Ltrs)": st.column_config.NumberColumn("Evening (Ltrs)", min_value=0, step=0.1, format="%.1f"),
    "Home Cons. (Ltrs)": st.column_config.NumberColumn("Home Cons.", min_value=0, step=0.1, format="%.1f"),
    "Calf Cons. (Ltrs)": st.column_config.NumberColumn("Calf Cons.", min_value=0, step=0.1, format="%.1f"),
    "Milk Poured (LPD)": st.column_config.NumberColumn("Milk Poured (LPD)", disabled=True, help="Auto-calculated"),
    "Remarks": st.column_config.TextColumn("Remarks"),
    "Visitor Sign": st.column_config.TextColumn("Visitor Sign"),
}

# 3. Display the Data Editor
# num_rows="dynamic" allows adding/deleting rows
edited_df = st.data_editor(
    st.session_state.milk_data,
    column_config=column_config,
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# 4. Calculation Logic & Persistence
# We recalculate "Milk Poured" every time the user changes a number
if not edited_df.equals(st.session_state.milk_data):
    # Ensure numeric columns are actually numbers (handle empty/NaN)
    numeric_cols = ["Morning (Ltrs)", "Evening (Ltrs)", "Home Cons. (Ltrs)", "Calf Cons. (Ltrs)"]
    edited_df[numeric_cols] = edited_df[numeric_cols].fillna(0.0)
    
    # Perform Calculation
    total_prod = edited_df["Morning (Ltrs)"] + edited_df["Evening (Ltrs)"]
    total_cons = edited_df["Home Cons. (Ltrs)"] + edited_df["Calf Cons. (Ltrs)"]
    edited_df["Milk Poured (LPD)"] = total_prod - total_cons
    
    # Save back to session state so it remembers
    st.session_state.milk_data = edited_df
    st.rerun() # Refresh to show the calculated numbers immediately

# ==========================================
# DOWNLOAD SECTION
# ==========================================
st.markdown("### 📥 Download Options")

if not edited_df.empty:
    # Prepare textual header
    header_text = (
        f"DAIRY EXCELLENCE INITIATIVE - MILK RECORD PROFILE\n"
        f"Farmer: {farmer_name} | Village: {village_name} | ID: {producer_id}\n"
        f"Cow: {cow_id} | Breed: {breed} | Calvings: {num_calvings}\n"
        f"Feed: {feeding_method} | Qty: {qty_fed}\n"
        f"--------------------------------------------------\n"
    )
    
    csv_buffer = io.StringIO()
    csv_buffer.write(header_text)
    edited_df.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="Download Completed Form (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"MilkRecord_{farmer_name}.csv",
        mime="text/csv"
    )
