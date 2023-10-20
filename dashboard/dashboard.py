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

