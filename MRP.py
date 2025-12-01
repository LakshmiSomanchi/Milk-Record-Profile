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
# SECTION 1: FARMER & COW PROFILE
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

    # --- Row 3: Origins & Feeding Method ---
    st.markdown("---")
    col_orig, col_method = st.columns(2)
    with col_orig:
        origin_choice = st.radio("Cow Source:", ["In Farm Born", "Purchased"], horizontal=True)
        is_purchased = "Yes" if origin_choice == "Purchased" else "No"
        is_farm_born = "Yes" if origin_choice == "In Farm Born" else "No"
        
    with col_method:
        grazing_choice = st.radio("Feeding Method:", ["Grazing", "Stall Feeding", "Both"], horizontal=True)

    # --- Row 4: Feed Composition (Brand Name & Qty) ---
    st.markdown("---")
    st.markdown("**Feed Composition & Quantity**")
    
    f1, f2, f3, f4 = st.columns(4)
    with f1: 
        cattle_feed_yn = st.checkbox("Cattle Feed")
    with f2: 
        own_feed_yn = st.checkbox("Own Feed")
    with f3:
        qty_fed = st.number_input("Qty fed (Kgs)", min_value=0.0, step=0.5)
    with f4:
        # BRAND NAME is always visible now to ensure it's not missed
        brand_name = st.text_input("Brand Name", placeholder="e.g. Rich / Heritage")

    # --- Row 5: Fodder Names (Green & Dry) ---
    st.markdown("**Fodder Details**")
    fod1, fod2, fod3, fod4 = st.columns(4)
    
    with fod1:
        green_fodder_yn = st.checkbox("Green Fodder (Y/N)")
    with fod2:
        # Input for Green Fodder Name (Enable only if checked)
        green_fodder_name = st.text_input("Green Fodder Name", disabled=not green_fodder_yn, placeholder="e.g. Napier")
        
    with fod3:
        dry_fodder_yn = st.checkbox("Dry Fodder (Y/N)")
    with fod4:
        # Input for Dry Fodder Name (Enable only if checked)
        dry_fodder_name = st.text_input("Dry Fodder Name", disabled=not dry_fodder_yn, placeholder="e.g. Paddy")

    # --- Row 6: Other Supplements ---
    st.markdown("**Other Supplements**")
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1: water_247_yn = st.checkbox("24/7 Water")
    with s2: silage_yn = st.checkbox("Silage")
    with s3: calcium_yn = st.checkbox("Calcium")
    with s4: mineral_mix_yn = st.checkbox("Mineral Mix")
    with s5: ummb_yn = st.checkbox("UMMB")

# ==========================================
# SECTION 2: DAILY MILK RECORD (Editable)
# ==========================================
st.markdown('<p class="section-title">2. Daily Milk Record Log</p>', unsafe_allow_html=True)

auto_calc = st.checkbox("Auto-calculate LPD?", value=True, key="autocalc")

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

edited_df = st.data_editor(
    st.session_state.milk_data,
    column_config=column_config,
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True,
    key="editor"
)

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
# SUBMIT & DOWNLOAD
# ==========================================
st.write("###")
if st.button("✅ Generate Clean Record", type="primary"):
    
    if not edited_df.empty:
        # Create dictionary of ALL profile data
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
            "Brand Name": brand_name,         # <--- Included
            "Grazing Method": grazing_choice,
            "Green Fodder?": "Yes" if green_fodder_yn else "No",
            "Green Fodder Name": green_fodder_name if green_fodder_yn else "", # <--- Included
            "Dry Fodder?": "Yes" if dry_fodder_yn else "No",
            "Dry Fodder Name": dry_fodder_name if dry_fodder_yn else "",       # <--- Included
            "24/7 Water?": "Yes" if water_247_yn else "No",
            "Silage?": "Yes" if silage_yn else "No",
            "Calcium?": "Yes" if calcium_yn else "No",
            "Mineral Mix?": "Yes" if mineral_mix_yn else "No",
            "UMMB?": "Yes" if ummb_yn else "No"
        }

        # Merge Profile Data into Table Data
        export_df = edited_df.copy()
        for col_name, value in reversed(profile_data.items()):
            export_df.insert(0, col_name, value)
            
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
