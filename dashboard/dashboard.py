''' ====================

E-Commerce Public Analysis Dashboard

by Naufal Mu'afi
nmuafi1@gmail.com

==================== '''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")


''' ====================

Dataframe Preparation

==================== '''

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

