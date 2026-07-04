
import streamlit as st
import pandas as pd

# 1. Setup web layout
st.set_page_config(page_title="Price Catcher MY", layout="centered")
st.title("🇲🇾 Live Grocery Price Catcher")
st.write("Find the top 5 cheapest shops in Malaysia for any grocery item.")

# 2. Download official government market logs safely
@st.cache_data
def load_data():
    df_p = pd.read_parquet('https://storage.data.gov.my/pricecatcher/pricecatcher_2026-07.parquet')
    df_m = pd.read_parquet('https://storage.data.gov.my/pricecatcher/lookup_premise.parquet')
    df_i = pd.read_parquet('https://storage.data.gov.my/pricecatcher/lookup_item.parquet')
    return df_p, df_m, df_i

with st.spinner("Connecting to live database... Please wait."):
    df_p, df_m, df_i = load_data()

# 3. Create the item search interface
user_query = st.text_input("Enter item name (e.g., Milo, Ayam, Milk, Egg):", "")

if user_query:
    # Look up item codes while filtering out unrelated candy products
    match = df_i[df_i['item'].str.lower().str.contains(user_query.lower(), na=False) & 
                 ~df_i['item'].str.lower().str.contains('kinder|bueno|chocolate', na=False)]
    
    if not match.empty:
        target = match.iloc[0]['item_code']
        item_full_name = match.iloc[0]['item']
        
        st.subheader(f"Results for: {item_full_name}")
        
        # Match item codes with prices and physical premises, then sort by cheapest
        res = pd.merge(df_p[df_p['item_code'] == target], df_m, on='premise_code').sort_values('price').head(5)
        
        # Print results onto cards
        for i, r in res.iterrows():
            with st.container():
                st.markdown(f"### 💵 **RM {r['price']:.2f}**")
                st.markdown(f"📍 **{r['premise']}** \n🗺️ *{r['district']}, {r['state']}*")
                st.write("---")
    else:
        st.error("Item not found. Please try a different name!")
