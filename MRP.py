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
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
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

# Toggle for Auto-Calculation
col_toggle, col_info = st.columns([1, 3])
with col_toggle:
    # If checked, math happens automatically. If unchecked, user can edit LPD manually.
    auto_calc = st.checkbox("Auto-calculate LPD?", value=True, help="Uncheck this to manually edit the Milk Poured column.")

# --- INITIALIZATION SECTION ---
if 'milk_data' not in st.session_state:
    st.session_state.milk_data = pd.DataFrame(
        {
            "Date": pd.Series(dtype='datetime64[ns]'),
            "Morning (Ltrs)": pd.Series(dtype='float'),
            "Evening (Ltrs)": pd.Series(dtype='float'),
            "Home Cons. (Ltrs)": pd.Series(dtype='float'),
            "Calf Cons. (Ltrs)": pd.Series(dtype='float'),
            "Milk Poured (LPD)": pd.Series(dtype='float'),
            "Remarks": pd.Series(dtype='str'),
            "Visitor Sign": pd.Series(dtype='str'),
        }
    )

# Configure column settings
# Note: We removed disabled=True from Milk Poured so you can edit it if auto_calc is off
column_config = {
    "Date": st.column_config.DateColumn("Date", default=date.today(), format="DD-MM-YYYY"),
    "Morning (Ltrs)": st.column_config.NumberColumn("Morning (Ltrs)", min_value=0, step=0.1, format="%.1f"),
    "Evening (Ltrs)": st.column_config.NumberColumn("Evening (Ltrs)", min_value=0, step=0.1, format="%.1f"),
    "Home Cons. (Ltrs)": st.column_config.NumberColumn("Home Cons.", min_value=0, step=0.1, format="%.1f"),
    "Calf Cons. (Ltrs)": st.column_config.NumberColumn("Calf Cons.", min_value=0, step=0.1, format="%.1f"),
    "Milk Poured (LPD)": st.column_config.NumberColumn("Milk Poured (LPD)", step=0.1, format="%.1f"), 
    "Remarks": st.column_config.TextColumn("Remarks"),
    "Visitor Sign": st.column_config.TextColumn("Visitor Sign"),
}

# Display the Data Editor
edited_df = st.data_editor(
    st.session_state.milk_data,
    column_config=column_config,
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# --- CALCULATION LOGIC ---
if not edited_df.equals(st.session_state.milk_data):
    # 1. Sanitize numbers (replace N/A with 0)
    numeric_cols = ["Morning (Ltrs)", "Evening (Ltrs)", "Home Cons. (Ltrs)", "Calf Cons. (Ltrs)", "Milk Poured (LPD)"]
    edited_df[numeric_cols] = edited_df[numeric_cols].fillna(0.0)
    
    # 2. Only run calculation if the Checkbox is True
    if auto_calc:
        total_prod = edited_df["Morning (Ltrs)"] + edited_df["Evening (Ltrs)"]
        total_cons = edited_df["Home Cons. (Ltrs)"] + edited_df["Calf Cons. (Ltrs)"]
        edited_df["Milk Poured (LPD)"] = total_prod - total_cons
    
    # 3. Save back to session state
    st.session_state.milk_data = edited_df
    st.rerun()

# ==========================================
# SUBMIT & DOWNLOAD SECTION
# ==========================================
st.write("###") # Spacer
st.markdown('<p class="section-header">3. Finalize & Submit</p>', unsafe_allow_html=True)

# We use session state to remember if the form has been submitted
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

col_submit, col_download = st.columns([1, 4])

with col_submit:
    # The Submit Button
    if st.button("✅ Submit Record", type="primary"):
        st.session_state.form_submitted = True

# Logic: Only show the Download button if Submit was clicked
if st.session_state.form_submitted:
    st.success("Record Finalized! You can now download the file.")
    
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
        
        # The Download Button
        st.download_button(
            label="📥 Download CSV File",
            data=csv_buffer.getvalue(),
            file_name=f"MilkRecord_{farmer_name}.csv",
            mime="text/csv"
        )
    else:
        st.warning("The table is empty. Please add data before downloading.")
else:
    # Optional: Show a greyed out message or nothing
    st.info("Please fill the table and click 'Submit Record' to generate the download file.")
