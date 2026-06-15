import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Material Composition Explorer", layout="wide")
st.title("📊 Product Material Composition Explorer")

# -----------------------------
# LOAD DATA (STATIC FILE)
# -----------------------------

@st.cache_data
def load_excel():
    # Decode the Excel file from secrets
    file_bytes = base64.b64decode(st.secrets["EXCEL_FILE"])
    
    # Create a file-like object
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    
    # Load all sheets into a dictionary
    sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    
    return sheets

# Load your data
data = load_excel()

UNU_TO_PRODUCT = {
    "0108": "Fridges (incl. combi-fridges)",
    "0109": "Freezers",
    "0111": "Air Conditioners (household installed and portable)",
    "0112": "Other Cooling equipment (e.g. dehumidifiers, heat pump dryers)",
    "0113": "Professional Cooling equipment (e.g. large air conditioners, cooling displays)",
    "1002": "Cooled Dispensers (e.g. for vending, cold drinks)",
    "0303": "Laptops (incl. tablets)",
    "0308": "Cathode Ray Tube Monitors",
    "0309": "Flat Display Panel Monitors (LCD, LED)",
    "0407": "Cathode Ray Tube TVs",
    "0408": "Flat Display Panel TVs (LCD, LED, Plasma)",
    "0501": "Small lighting equipment (excl. LED & incandescent)",
    "0502": "Compact Fluorescent Lamps (incl. retrofit & non-retrofit)",
    "0503": "Straight Tube Fluorescent Lamps",
    "0504": "Special Lamps (e.g. professional mercury, high & low pressure sodium)",
    "0505": "LED Lamps (incl. retrofit LED lamps)",
    "0001": "Central Heating (household installed)",
    "0002": "Photovoltaic Panels (incl. inverters)",
    "0101": "Professional Heating & Ventilation (excl. cooling equipment)",
    "0102": "Dishwashers",
    "0103": "Kitchen equipment (e.g. large furnaces, ovens, cooking equipment)",
    "0104": "Washing Machines (incl. combined dryers)",
    "0105": "Dryers (wash dryers, centrifuges)",
    "0106": "Household Heating & Ventilation (e.g. hoods, ventilators, space heaters)",
    "0307": "Professional IT equipment (e.g. servers, routers, data storage, copiers)",
    "0602": "Professional Tools (e.g. for welding, soldering, milling)",
    "0703": "Leisure equipment (e.g. sports equipment, electric bikes, juke boxes)",
    "0802": "Professional Medical equipment (e.g. hospital, dentist, diagnostics)",
    "0902": "Professional Monitoring & Control equipment (e.g. laboratory, control panels)",
    "1001": "Non-cooled Dispensers (e.g. for vending, hot drinks, tickets, money)",
    "0114": "Microwaves (incl. combined, excl. grills)",
    "0201": "Other small household equipment (e.g. small ventilators, irons, clocks, adapters)",
    "0202": "Equipment for food preparation (e.g. toaster, grills, food processing, frying pans)",
    "0203": "Small household equipment for hot water preparation (e.g. coffee, tea, water cookers)",
    "0204": "Vacuum Cleaners (excl. professional)",
    "0205": "Personal Care equipment (e.g. tooth brushes, hair dryers, razors)",
    "0401": "Small Consumer Electronics (e.g. headphones, remote controls)",
    "0402": "Portable Audio & Video (e.g. MP3, e-readers, car navigation)",
    "0403": "Music Instruments, Radio, Hi-Fi (incl. audio sets)",
    "0404": "Video (e.g. Video recorders, DVD, Blue Ray, set-top boxes) and projectors",
    "0405": "Speakers",
    "0406": "Cameras (e.g. camcorders, photo & digital still cameras)",
    "0506": "Household Luminaires (incl. household incandescent fittings & household LED luminaires)",
    "0507": "Professional Luminaires (offices, public space, industry)",
    "0601": "Household Tools (e.g. drills, saws, high pressure cleaners, lawn mowers)",
    "0701": "Toys (e.g. car racing sets, electric trains, music toys, biking computers, drones)",
    "0801": "Household Medical equipment (e.g. thermometers, blood pressure meters)",
    "0901": "Household Monitoring & Control equipment (alarm, heat, smoke, excl. screens)",
    "0301": "Small IT equipment (e.g. routers, mice, keyboards, external drives & accessories)",
    "0302": "Desktop PCs (excl. monitors, accessoires)",
    "0304": "Printers (e.g. scanners, multi functionals, faxes)",
    "0305": "Telecommunication equipment (e.g. (cordless) phones, answering machines)",
    "0306": "Mobile Phones (incl. smartphones, pagers)",
    "0702": "Game Consoles"
}

UNU_to_name = {
    UNU_TO_PRODUCT.get(k, k): k for k in data.keys()
}

name_to_UNU = {v: k for k, v in UNU_to_name.items()}

# -----------------------------
# PRODUCT SELECTION
# -----------------------------
product = st.selectbox("Select a product", list(UNU_to_name.keys()))
UNU_key = UNU_to_name[product]
df = data[UNU_key]

# -----------------------------
# CLEAN DATA
# -----------------------------
element_column = df.columns[0]
df = df.rename(columns={element_column: "Element"})
df = df.set_index("Element")

df.columns = df.columns.astype(int)

# -----------------------------
# YEAR SELECTION
# -----------------------------
year = st.slider(
    "Select year",
    min_value=int(df.columns.min()),
    max_value=int(df.columns.max()),
    value=int(df.columns.max())
)

year_data = df[year].dropna()
year_data = year_data[year_data > 0]

# -----------------------------
# FULL MATERIAL BAR CHART
# -----------------------------
st.subheader(f"Material composition ({year})")

fig1, ax1 = plt.subplots(figsize=(12, 6))
year_data.sort_values(ascending=False).plot(kind="bar", ax=ax1)
ax1.set_ylabel("kg per kg product")
ax1.set_xlabel("Element")
ax1.set_title(f"{UNU_key} — Material Breakdown ({year})")
plt.xticks(rotation=90)

st.pyplot(fig1)

# -----------------------------
# CRM LIST (SYMBOLS)
# -----------------------------
EU_CRMS = [
    "Sb","Ba","Al","Be","Bi","B","Co","C","F","Ga","Ge","Hf",
    "He","In","Li","Mg","Nb","P","REE","Sc","Si","Ta","Ti","W","V",
    "Pt","Pd","Rh","Ru","Ir","Os"
]

# -----------------------------
# CRM FILTER
# -----------------------------
crm_data = year_data[
    year_data.index.str.upper().isin([e.upper() for e in EU_CRMS])
]

# -----------------------------
# CRM BAR CHART
# -----------------------------
st.subheader(f"Critical Raw Materials ({year})")

if not crm_data.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    crm_data.sort_values(ascending=False).plot(kind="bar", ax=ax2, color="orange")
    ax2.set_ylabel("kg per kg product")
    ax2.set_xlabel("CRM Element")
    ax2.set_title(f"{UNU_key} — CRM Breakdown ({year})")
    plt.xticks(rotation=90)

    st.pyplot(fig2)
else:
    st.info("No CRM elements found for this product/year.")
