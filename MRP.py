import streamlit as st
import pandas as pd
from datetime import date
import io

# --- Page Configuration ---
st.set_page_config(page_title="Milk Record Profile", page_icon="🐄", layout="wide")

# --- Styling to mimic the paper form headers ---
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

# --- Title Section ---
st.title("🐄 Dairy Excellence Initiative")
st.subheader("Milk Record Profile")

# ==========================================
# SECTION 1: FARMER & COW PROFILE (Top of Form)
# ==========================================

# We use a container with a border to group this section visually
with st.container(border=True):
    st.markdown('<p class="section-header">1. General Profile</p>', unsafe_allow_html=True)
    
    # Row 1: Farmer Details
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        farmer_name = st.text_input("Farmer Name")
    with c2:
        village_name = st.text_input("Village Name")
    with c3:
        producer_id = st.text_input("Producer ID")
    with c4:
        hpc_code = st.text_input("HPC Code")

    # Row 2: Cow Details
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        cow_id = st.text_input("Cow Identity Number/Mark")
    with c6:
        breed = st.text_input("Breed")
    with c7:
        num_calvings = st.number_input("No. of Calvings", min_value=0, step=1)
    with c8:
        calving_date = st.date_input("Date of Calving", value=date.today())

    # Row 3: Origin & Basic Feed
    c9, c10, c11 = st.columns([1, 1, 2])
    with c9:
        origin = st.radio("Cow Origin", ["In Farm Born", "Purchased"], horizontal=True)
    with c10:
        feeding_method = st.radio("Feeding Method", ["Grazing", "Stall Feeding", "Both"], horizontal=True)
    with c11:
        st.write(" **Major Feed Source:**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cattle_feed = st.checkbox("Cattle Feed (Y/N)")
        with col_f2:
            own_feed = st.checkbox("Own Feed (Y/N)")

    # Row 4: Detailed Feeding (The small checkboxes)
    st.markdown("---")
    st.write("**Feeding Details & Supplements**")
    
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1:
        qty_fed = st.number_input("Qty Fed (Kgs)", min_value=0.0, step=0.5)
    with f2:
        brand_name = st.text_input("Brand Name", placeholder="e.g. Rich")
    with f3:
        green_fodder = st.checkbox("Green Fodder")
        dry_fodder = st.checkbox("Dry Fodder")
    with f4:
        silage = st.checkbox("Silage")
        water_247 = st.checkbox("24/7 Water")
    with f5:
        calcium = st.checkbox("Calcium")
        mineral_mix = st.checkbox("Mineral Mixture")
    with f6:
        ummb = st.checkbox("UMMB")

# ==========================================
# SECTION 2: DAILY MILK RECORD (Bottom of Form)
# ==========================================

st.markdown('<p class="section-header">2. Daily Milk Record Log</p>', unsafe_allow_html=True)

# Initialize Session State
if 'data_entries' not in st.session_state:
    st.session_state.data_entries = []

# --- Input Form ---
with st.form("daily_log", clear_on_submit=True):
    # Create columns to match the paper table headers
    # Date | Morning | Evening | House | Calf | Remarks | Sign
    col_d, col_m, col_e, col_h, col_c, col_rem, col_sign = st.columns([2, 1.5, 1.5, 1.5, 1.5, 3, 2])
    
    with col_d:
        entry_date = st.date_input("Date", value=date.today())
    with col_m:
        morning_milk = st.number_input("AM (Ltrs)", min_value=0.0, step=0.1)
    with col_e:
        evening_milk = st.number_input("PM (Ltrs)", min_value=0.0, step=0.1)
    with col_h:
        house_cons = st.number_input("Home (Ltrs)", min_value=0.0, step=0.1)
    with col_c:
        calf_cons = st.number_input("Calf (Ltrs)", min_value=0.0, step=0.1)
    with col_rem:
        remarks = st.text_input("Remarks", placeholder="e.g. Sick")
    with col_sign:
        visitor_sign = st.text_input("Signature/Name")
        
    # Submit Button
    submitted = st.form_submit_button("➕ Add Record Row")

    if submitted:
        # Calculations
        total_produced = morning_milk + evening_milk
        total_consumed = house_cons + calf_cons
        milk_poured_lpd = total_produced - total_consumed
        
        # Add to list
        record = {
            "Date": entry_date,
            "Morning (Ltrs)": morning_milk,
            "Evening (Ltrs)": evening_milk,
            "Household Cons.": house_cons,
            "Calf Cons.": calf_cons,
            "Milk Poured (LPD)": milk_poured_lpd,
            "Remarks": remarks,
            "Visitor Signature": visitor_sign
        }
        st.session_state.data_entries.append(record)
        st.success(f"Record added for {entry_date}")

# --- Display Table ---
if st.session_state.data_entries:
    df = pd.DataFrame(st.session_state.data_entries)
    
    # Format date for display
    df_display = df.copy()
    df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%d-%m-%Y')
    
    st.table(df_display)

    # --- Download Logic ---
    st.markdown("### 📥 Download Options")
    
    # Create text summary for the top of the CSV
    header_text = (
        f"DAIRY EXCELLENCE INITIATIVE - MILK RECORD PROFILE\n"
        f"Farmer: {farmer_name} | Village: {village_name} | Producer ID: {producer_id}\n"
        f"Cow ID: {cow_id} | Breed: {breed} | Calvings: {num_calvings}\n"
        f"Origin: {origin} | Feeding Method: {feeding_method}\n"
        f"Feed Brand: {brand_name} | Qty: {qty_fed}\n"
        f"--------------------------------------------------\n"
    )
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    csv_buffer.write(header_text)
    df.to_csv(csv_buffer, index=False)
    
    filename = f"MilkRecord_{farmer_name}_{date.today()}.csv"
    
    st.download_button(
        label="Download Record as CSV",
        data=csv_buffer.getvalue(),
        file_name=filename,
        mime="text/csv"
    )
