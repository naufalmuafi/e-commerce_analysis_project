# ====================

# E-Commerce Public Analysis Dashboard

# by Naufal Mu'afi
# nmuafi1@gmail.com

# ==================== '''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")


# ''' ====================

# Dataframe Preparation

# ==================== '''

# ===== Daily Orders Dataframe =====
def c_daily_orders(df):
  daily_orders = df.resample(rule="D", on="order_purchase_timestamp").agg({
    "order_id": "nunique",
    "price": "sum"
  })
  daily_orders = daily_orders.reset_index()
  daily_orders.rename(columns={
    "order_purchase_timestamp": "order_date",
    "order_id": "order_count",
    "price": "revenue"
  }, inplace=True)
  
  return daily_orders

# ===== Sum Order Dataframe =====
def c_sum_order(df):
  sum_order = df.groupby("product_category_name").order_id.nunique().sort_values(ascending=False).reset_index()
  sum_order.rename(columns={
    "order_id": "quantity"
  }, inplace=True)
  
  return sum_order

# ===== by City Dataframe =====
def c_bycity(df):
  bycity = df.groupby(by="customer_city").customer_id.nunique().reset_index()
  bycity.rename(columns={
    "customer_id": "customer_count"
  }, inplace=True)
  
  return bycity

# ===== by State Dataframe =====
def c_bystate(df):
  bystate = df.groupby(by="customer_state").customer_id.nunique().reset_index()
  bystate.rename(columns={
    "customer_id": "customer_count"
  }, inplace=True)
  
  return bystate

# ===== Payment Type Dataframe =====
def c_payment_type(df):
  payment_type = df.groupby(by="payment_type").order_id.nunique().reset_index()
  payment_type.rename(columns={
    "order_id": "order_count"
  }, inplace=True)
  
  return payment_type

# ===== RFM Dataframe =====
def c_rfm(df):
  rfm = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
  })
  rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
  
  rfm["max_order_timestamp"] = rfm["max_order_timestamp"].dt.date
  recent_date = df["order_purchase_timestamp"].dt.date.max()
  rfm["recency"] = rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
  rfm.drop("max_order_timestamp", axis=1, inplace=True)
  
  return rfm


# ''' ====================

# Load Dataframe and create a filter

# ==================== '''

# Load the Data
all_df = pd.read_csv("data.csv")

# ===== Create a Filter Component =====
datetime_columns = ["order_purchase_timestamp",
                    "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
  st.write(
    '''
    # Public Brazilian E-Commerce
    Data Analysis Project
    
    
    '''
  )
  
  start_date, end_date = st.date_input(
    label='Time Range',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
  )
  
  st.caption('Copyright (c) Naufal Muafi nmuafi1@gmail.com')

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Load the Dataframe
daily_orders_df = c_daily_orders(main_df)
sum_order_df = c_sum_order(main_df)
bycity_df = c_bycity(main_df)
bystate_df = c_bystate(main_df)
payment_type_df = c_payment_type(main_df)
rfm_df = c_rfm(main_df)


# ''' ====================

# Data Visualization

# ==================== '''
st.header('Brazilian E-Commerce Dashboard :sparkles:')

# ===== daily orders =====
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
  total_orders = daily_orders_df.order_count.sum()
  st.metric("Total Orders", value=total_orders)

with col2:
  total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='es_CO')
  st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
  daily_orders_df["order_date"],
  daily_orders_df["order_count"],
  marker='o',
  linewidth=2,
  color='#90CAF9'
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# ===== Product Performance =====
