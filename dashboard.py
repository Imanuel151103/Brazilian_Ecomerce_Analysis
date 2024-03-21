import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style = 'dark')
#Menyiapkan dataframe untuk menggambarkan visualisasi data di dashboard
df_order_items_products_english_orders = pd.read_csv("order_items_products_english_orders.csv")
df_order_payments_orders_customers = pd.read_csv("order_payments_orders_customers.csv")
df_orders_delivered = pd.read_csv("orders_delivered.csv")

def yearly_order(df_orders_delivered):
    df_yearly_order = df_orders_delivered.resample(rule='Y',on='order_purchase_timestamp').agg({
    "order_id":"nunique"
    })
    df_yearly_order.reset_index(inplace=True)
    df_yearly_order["order_purchase_timestamp"]=df_yearly_order["order_purchase_timestamp"].dt.year
    df_yearly_order.rename(columns={
    "order_purchase_timestamp":"order_purchase_year",
    "order_id":"order_count"
    },inplace=True)
    return df_yearly_order
def product_category_count(df_order_items_products_english_orders):
    df_product_category_count = df_order_items_products_english_orders.groupby(by="product_category_name_english").size().sort_values(ascending=False).reset_index(name="quantity")
    return df_product_category_count
def RFM(df_order_payments_orders_customers):
    df_RFM = df_order_payments_orders_customers.groupby(by="customer_unique_id").agg({
    "order_purchase_timestamp":"max",#Menghitung kapan terakhir pelanggan melakukan transaksi
    "order_id":"nunique", #menghitung berapa kali pelanggan melakukan transaksi
    "payment_value":"sum" #menghitung berapa besar pendapatan perusahaan yang dihasilkan dari pelanggan tersebut
    })
    df_RFM.reset_index(inplace=True)
    df_RFM.rename(columns={
    "order_purchase_timestamp":"max_order_purchase_timestamp",
    "order_id":"frequency",
    "payment_value" : "monetary"
    },inplace=True)
    recent_date = df_order_payments_orders_customers["order_purchase_timestamp"].max()
    df_RFM["recency_days"]=df_RFM["max_order_purchase_timestamp"].apply(lambda x : (recent_date-x).days)
    df_RFM.drop("max_order_purchase_timestamp",axis=1,inplace=True)
    return df_RFM
df_orders_delivered["order_purchase_timestamp"] = pd.to_datetime( df_orders_delivered["order_purchase_timestamp"])
df_order_items_products_english_orders["shipping_limit_date"]=pd.to_datetime(df_order_items_products_english_orders["shipping_limit_date"])
df_order_payments_orders_customers["order_purchase_timestamp"]=pd.to_datetime(df_order_payments_orders_customers["order_purchase_timestamp"])
min_date = df_order_payments_orders_customers["order_purchase_timestamp"].min()
max_date = df_order_payments_orders_customers["order_purchase_timestamp"].max()
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.png")
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
df_orders_delivered = df_orders_delivered[(df_orders_delivered["order_purchase_timestamp"]>=str(start_date))&
                                         (df_orders_delivered["order_purchase_timestamp"]<= str(end_date)) ]
df_order_items_products_english_orders = df_order_items_products_english_orders[(df_order_items_products_english_orders["shipping_limit_date"]>=str(start_date))&
                                         (df_order_items_products_english_orders["shipping_limit_date"]<= str(end_date)) ]
df_order_payments_orders_customers = df_order_payments_orders_customers[(df_order_payments_orders_customers["order_purchase_timestamp"]>=str(start_date))&
                                         (df_order_payments_orders_customers["order_purchase_timestamp"]<= str(end_date)) ]
df_yearly_order = yearly_order(df_orders_delivered)
df_product_category_count = product_category_count(df_order_items_products_english_orders)
df_RFM = RFM(df_order_payments_orders_customers)
st.header('Olist Store Dashboard :sparkles:')
st.subheader('Yearly Orders')
fig = plt.figure(figsize=(10,5))
plt.bar(df_yearly_order["order_purchase_year"], df_yearly_order["order_count"], color="#72BCD4")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Order Count", fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

st.subheader("Best & Worst Performing Category Product")
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
fig,ax =plt.subplots(nrows=1,ncols=2,figsize=(24,6))
sns.barplot(x="quantity", y="product_category_name_english", data=df_product_category_count.head(5), palette=colors,ax=ax[0])
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("Best Performing Product Category", loc="center", fontsize=15)
ax[0].tick_params(axis="y", labelsize=12)
sns.barplot(x="quantity", y="product_category_name_english", data=df_product_category_count.sort_values(by="quantity",ascending=True).head(5), palette=colors,ax=ax[1])
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title("Worst Performing Product Category", loc="center", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis="y", labelsize=12)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(24,6))
color = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="customer_unique_id",y="recency_days",data=df_RFM.sort_values(by="recency_days",ascending=True).head(5),palette=color,ax=ax[0])
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("by Recency (days)",loc="center",fontsize=18)
ax[0].tick_params(axis="x",labelsize=10,labelrotation=45)

sns.barplot(x="customer_unique_id",y="frequency",data=df_RFM.sort_values(by="frequency",ascending=False).head(5),palette=color,ax=ax[1])
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title("by Frequency",loc="center",fontsize=18)
ax[1].tick_params(axis="x",labelsize=10,labelrotation=45)

sns.barplot(x="customer_unique_id",y="monetary",data=df_RFM.sort_values(by="monetary",ascending=False).head(5),palette=color,ax=ax[2])
ax[2].set_xlabel(None)
ax[2].set_ylabel(None)
ax[2].set_title("by Monetary",loc="center",fontsize=18)
ax[2].tick_params(axis="x",labelsize=10,labelrotation=45)
st.pyplot(fig)
