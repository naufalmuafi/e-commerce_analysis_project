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
all_df = pd.read_csv("dashboard/data.csv")

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
  
  st.caption('''
             Copyright (c) Naufal Muafi | 
             nmuafi1@gmail.com
             ''')

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


# ===== Q1: daily orders =====
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


# ===== Q2: Product Performance =====
st.subheader('Best and Worst Performing Product')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

for i in range(2):
  if i == 0:
    data = sum_order_df.head(5)
  elif i == 1:
    data = sum_order_df.sort_values(by="quantity", ascending=True).head(5)
  
  sns.barplot(
    x="quantity",
    y="product_category_name",
    data=data,
    palette=colors,
    ax=ax[i]
  )
  ax[i].set_ylabel(None)
  ax[i].set_xlabel("Number of Sales", fontsize=30)
  ax[i].tick_params(axis='y', labelsize=35)
  ax[i].tick_params(axis='x', labelsize=30)

ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()

ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)

st.pyplot(fig)


# ===== Q3: Customers Demographics =====
st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

# by City
with col1:
  fig, ax = plt.subplots(figsize=(20, 10))
    
  colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
  sns.barplot(
    x="customer_count",
    y="customer_city",
    data=bycity_df.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
  )
  ax.set_title("Number of Customer by City", loc="center", fontsize=50)
  ax.set_ylabel(None)
  ax.set_xlabel(None)
  ax.tick_params(axis='x', labelsize=30)
  ax.tick_params(axis='y', labelsize=35)
  
  st.pyplot(fig)

# by State
with col2:
  fig, ax = plt.subplots(figsize=(20, 10))
    
  colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
  sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
  )
  ax.set_title("Number of Customer by States", loc="center", fontsize=50)
  ax.set_ylabel(None)
  ax.set_xlabel(None)
  ax.tick_params(axis='x', labelsize=30)
  ax.tick_params(axis='y', labelsize=35)
  
  st.pyplot(fig)


# ===== Q4: Customers Payment Type =====
st.subheader('Customer Payment Type')

fig, ax = plt.subplots(figsize=(20,10))

colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
  x="order_count",
  y="payment_type",
  data=payment_type_df.sort_values(by="order_count", ascending=False),
  palette=colors_
)
ax.set_title("Customer Payment Type That's Most Preferred and Used.",
          loc="center", fontsize=30)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis="x", labelsize=15)
ax.tick_params(axis="y", labelsize=20)

st.pyplot(fig)


# ===== Q5 - Q7: Best Customers Based on RFM Parameters =====
st.subheader('Best Customers Based on RFM Parameters (customer_id)')

col1, col2, col3 = st.columns(3)

# Recency Metric
with col1:
  avg_recency = round(rfm_df.recency.mean(), 1)
  st.metric("Average Recency (days)", value=avg_recency)  

# Frequency Metric
with col2:
  avg_frequency = round(rfm_df.frequency.mean(), 2)
  st.metric("Average Frequency", value=avg_frequency)

# Monetary Metric
with col3:
  avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale="es_CO")
  st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 15))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

for i, column in enumerate(["recency", "frequency", "monetary"]):
  # the sorted data
  top_customers = rfm_df.sort_values(by=column, ascending=True if i == 0 else False).head(5)
  
  # truncate customer_id to be 8 characters
  top_customers["customer_id_short"] = top_customers["customer_id"].str[:8] + "..."
  
  sns.barplot(
    y=column,
    x="customer_id_short",
    data=top_customers,
    palette=colors,
    ax=ax[i]
  )
  ax[i].set_ylabel(None)
  ax[i].set_xlabel(None)  
  ax[i].tick_params(axis="x", labelsize=35)
  ax[i].tick_params(axis="y", labelsize=30)
  ax[i].set_xticklabels(top_customers["customer_id_short"], rotation=45)

ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[2].set_title("By Monetary", loc="center", fontsize=50)

st.pyplot(fig)