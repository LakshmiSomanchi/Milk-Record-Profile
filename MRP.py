import streamlit as st
import pandas as pd
from datetime import date

# --- Page Configuration ---
st.set_page_config(page_title="Milk Record Profile", page_icon="🐄", layout="wide")

# --- CSS for Form Styling ---
st.markdown("""
    <style>
    .section-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 10px;
        margin-bottom: 5px;
        border-bottom: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐄 Dairy Excellence Initiative")
st.markdown("**Digital Milk Record Profile**")

# ==========================================
# SECTION 1: FARMER & COW PROFILE (All 22 Questions)
# ==========================================
with st.container(border=True):
    st.markdown('<p class="section-title">1. General Profile</p>', unsafe_allow_html=True)
    
    # --- Row 1: Identification ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: farmer_name = st.text_input("Farmer Name")
    with c2: village_name = st.text_input("Village Name")
    with c3: producer_id = st.text_input("Producer ID")
    with c4: hpc_code = st.text_input("HPC Code")

    # --- Row 2: Cow Details ---
    c5, c6, c7, c8 = st.columns(4)
    with c5: cow_id = st.text_input("Cow Identity Number/Mark")
    with c6: breed = st.text_input("Breed")
    with c7: num_calvings = st.number_input("No. of Calvings", min_value=0, step=1)
    with c8: calving_date = st.date_input("Date of Calving", value=date.today())

    # --- Row 3: Origins & Feeding Type ---
    st.markdown("---")
    col_orig, col_method = st.columns(2)
    with col_orig:
        # Paper form asks: Purchased (Y/N) OR In Farm Born (Y/N). This is a radio choice.
        origin_choice = st.radio("Cow Source:", ["In Farm Born", "Purchased"], horizontal=True)
        # Convert to boolean for clean data
        is_purchased = "Yes" if origin_choice == "Purchased" else "No"
        is_farm_born = "Yes" if origin_choice == "In Farm Born" else "No"
        
    with col_method:
        # Grazing / Stall / Both
        grazing_choice = st.radio("Feeding Method:", ["Grazing", "Stall Feeding", "Both"], horizontal=True)

    # --- Row 4: Feed Specifics (Strict Checkboxes) ---
    st.markdown("---")
    st.write("**Feed Composition & Quantity**")
    
    f1, f2, f3, f4 = st.columns(4)
    with f1: 
        cattle_feed_yn = st.checkbox("Cattle Feed")
    with f2: 
        own_feed_yn = st.checkbox("Own Feed")
    with f3:
        # Only relevant if feeding is happening
        qty_fed = st.number_input("Qty fed (Kgs)", min_value=0.0, step=0.5)
    with f4:
        brand_name = st.text_input("Brand Name", placeholder="e.g. Rich")

    # --- Row 5: Supplements & Fodder (All 7 checkboxes from form) ---
    st.write("**Supplements & Fodder**")
    s1, s2, s3, s4, s5, s6, s7 = st.columns(7)
    with s1: green_fodder_yn = st.checkbox("Green Fodder")
    with s2: dry_fodder_yn = st.checkbox("Dry Fodder")
    with s3: water_247_yn = st.checkbox("24/7 Water")
    with s4: silage_yn = st.checkbox("Silage")
    with s5: calcium_yn = st.checkbox("Calcium")
    with s6: mineral_mix_yn = st.checkbox("Mineral Mix")
    with s7: ummb_yn = st.checkbox("UMMB")

# ==========================================
# SECTION 2: DAILY MILK RECORD (Editable)
# ==========================================
st.markdown('<p class="section-title">2. Daily Milk Record Log</p>', unsafe_allow_html=True)

# Toggle for Auto-Calculation
auto_calc = st.checkbox("Auto-calculate LPD?", value=True, key="autocalc")

# Initialize Data
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

# Configure Columns
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

# Editor
edited_df = st.data_editor(
    st.session_state.milk_data,
    column_config=column_config,
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# Calculation Logic
if not edited_df.equals(st.session_state.milk_data):
    numeric_cols = ["Morning (Ltrs)", "Evening (Ltrs)", "Home Cons. (Ltrs)", "Calf Cons. (Ltrs)", "Milk Poured (LPD)"]
    edited_df[numeric_cols] = edited_df[numeric_cols].fillna(0.0)
    
    if auto_calc:
        total_prod = edited_df["Morning (Ltrs)"] + edited_df["Evening (Ltrs)"]
        total_cons = edited_df["Home Cons. (Ltrs)"] + edited_df["Calf Cons. (Ltrs)"]
        edited_df["Milk Poured (LPD)"] = total_prod - total_cons
    
    st.session_state.milk_data = edited_df
    st.rerun()

# ==========================================
# SUBMIT & DOWNLOAD (CLEAN FORMAT LOGIC)
# ==========================================
st.write("###")
if st.button("✅ Generate Clean Record", type="primary"):
    
    if not edited_df.empty:
        # 1. Create a Dictionary of the Profile Data (The "Questions")
        profile_data = {
            "Farmer Name": farmer_name,
            "Village Name": village_name,
            "Producer ID": producer_id,
            "HPC Code": hpc_code,
            "Cow ID": cow_id,
            "Breed": breed,
            "No. Calvings": num_calvings,
            "Date Calving": calving_date,
            "Cow Purchased?": is_purchased,
            "Farm Born?": is_farm_born,
            "Cattle Feed?": "Yes" if cattle_feed_yn else "No",
            "Own Feed?": "Yes" if own_feed_yn else "No",
            "Qty Fed (Kgs)": qty_fed,
            "Brand Name": brand_name,
            "Grazing Method": grazing_choice,
            "Green Fodder?": "Yes" if green_fodder_yn else "No",
            "Dry Fodder?": "Yes" if dry_fodder_yn else "No",
            "24/7 Water?": "Yes" if water_247_yn else "No",
            "Silage?": "Yes" if silage_yn else "No",
            "Calcium?": "Yes" if calcium_yn else "No",
            "Mineral Mix?": "Yes" if mineral_mix_yn else "No",
            "UMMB?": "Yes" if ummb_yn else "No"
        }

        # 2. Merge Profile Data into every row of the Table Data
        # We create a new dataframe for export
        export_df = edited_df.copy()
        
        # Add profile columns to the left side
        for col_name, value in reversed(profile_data.items()):
            export_df.insert(0, col_name, value)
            
        # 3. Create the clean CSV
        csv_data = export_df.to_csv(index=False)
        filename = f"MilkRecord_{farmer_name}_{date.today()}.csv"

        st.success("File Generated Successfully!")
        
        st.download_button(
            label="📥 Download Clean CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
    else:
        st.warning("Please add at least one row of milk data before generating the record.")
