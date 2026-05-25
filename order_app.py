import streamlit as st
import pandas as pd
import os
import random

from datetime import datetime

import gspread

from oauth2client.service_account import (
    ServiceAccountCredentials
)

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(

    page_title="KFC Order Collector",

    page_icon="  ",

    layout="wide"
)

# =========================================
# GOOGLE SHEET CONNECT
# =========================================

scope = [

    "https://spreadsheets.google.com/feeds",

    "https://www.googleapis.com/auth/drive"
]

# =========================================
# STREAMLIT CLOUD SECRETS
# =========================================

creds_dict = dict(
    st.secrets["gcp_service_account"]
)

creds = ServiceAccountCredentials.from_json_keyfile_dict(

    creds_dict,

    scope
)

client = gspread.authorize(
    creds
)

sheet = client.open(
    "KFC_Orders"
).sheet1

# =========================================
# CREATE FOLDER
# =========================================

os.makedirs(
    "orders",
    exist_ok=True
)

# =========================================
# MENU
# =========================================

MENU_PRICES = {

    "Gà Rán": 80000,
    "Pepsi": 20000,
    "Khoai Tây Chiên": 45000,
    "Burger Bò": 70000,
    "Cơm Gà": 65000,
    "Trà Chanh": 25000,
    "Mì Ý": 60000,
    "Phô Mai Viên": 35000,
    "Salad": 30000,
    "7Up": 20000
}

# =========================================
# TITLE
# =========================================

st.title(
    "HỆ THỐNG KFC ORDER"
)

st.write("""
CÁC BẠN GIÚP TÔI LÀM PHIẾU MUA HÀNG NÀY NHÉ 
CẢM ƠN CÁC BẠN !
""")

# =========================================
# CUSTOMER ID
# =========================================

customer_id = st.text_input(

    " Customer ID",

    value=f"CUS_{random.randint(1000,9999)}"
)

# =========================================
# FOOD SELECT
# =========================================

st.header(
    "Hãy chọn món ăn"
)

selected_items = {}

bill_data = []

total_bill = 0

col1, col2 = st.columns(2)

foods = list(MENU_PRICES.items())

half = len(foods) // 2

# =========================================
# LEFT COLUMN
# =========================================

with col1:

    for food, price in foods[:half]:

        quantity = st.number_input(

            f"{food} - {price:,.0f} VNĐ",

            min_value=0,

            max_value=20,

            step=1,

            key=food
        )

        selected_items[food] = quantity

# =========================================
# RIGHT COLUMN
# =========================================

with col2:

    for food, price in foods[half:]:

        quantity = st.number_input(

            f"{food} - {price:,.0f} VNĐ",

            min_value=0,

            max_value=20,

            step=1,

            key=food
        )

        selected_items[food] = quantity

# =========================================
# BILL
# =========================================

for food, quantity in selected_items.items():

    if quantity > 0:

        price = MENU_PRICES[food]

        total_price = (
            quantity * price
        )

        total_bill += total_price

        bill_data.append({

            "Món ăn": food,

            "Số lượng": quantity,

            "Đơn giá":
            f"{price:,.0f} VNĐ",

            "Thành tiền":
            f"{total_price:,.0f} VNĐ"
        })

# =========================================
# SHOW BILL
# =========================================

st.subheader(
    "🧾 Hóa đơn"
)

if len(bill_data) > 0:

    st.dataframe(

        pd.DataFrame(bill_data),

        use_container_width=True
    )

else:

    st.info(
        "Chưa có món ăn nào được chọn"
    )

# =========================================
# TOTAL BILL
# =========================================

st.success(
    f"Tổng bill: {total_bill:,.0f} VNĐ"
)

# =========================================
# BUY BUTTON
# =========================================

if st.button(
    "Mua hàng"
):

    if total_bill == 0:

        st.warning(
            "! Vui lòng chọn món ăn"
        )

    else:

        order_id = random.randint(
            100000,
            999999
        )

        order_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        order_data = []

        # =================================
        # CREATE ORDER DATA
        # =================================

        for food, quantity in selected_items.items():

            if quantity > 0:

                price = MENU_PRICES[food]

                total_price = (
                    quantity * price
                )

                order_data.append({

                    "order_id": order_id,

                    "customer_id":
                    customer_id,

                    "food": food,

                    "quantity":
                    quantity,

                    "price":
                    price,

                    "total_price":
                    total_price,

                    "order_time":
                    order_time
                })

        df_new = pd.DataFrame(
            order_data
        )

        # =================================
        # SAVE CSV
        # =================================

        csv_path = (
            "orders/real_orders.csv"
        )

        try:

            if os.path.exists(csv_path):

                df_old = pd.read_csv(
                    csv_path
                )

                df_all = pd.concat(

                    [df_old, df_new],

                    ignore_index=True
                )

            else:

                df_all = df_new

            df_all.to_csv(

                csv_path,

                index=False
            )

        except PermissionError:

            st.error("""
            !File CSV đang được mở
            
            Hãy đóng file rồi thử lại
            """)

        # =================================
        # SAVE EXCEL
        # =================================

        excel_path = (
            "orders/real_orders.xlsx"
        )

        try:

            df_all.to_excel(

                excel_path,

                index=False
            )

        except PermissionError:

            st.error("""
            ! File Excel đang được mở
            
            Hãy đóng file rồi thử lại
            """)

        # =================================
        # SAVE GOOGLE SHEET
        # =================================

        try:

            for row in order_data:

                sheet.append_row([

                    row["order_id"],

                    row["customer_id"],

                    row["food"],

                    row["quantity"],

                    row["price"],

                    row["total_price"],

                    row["order_time"]
                ])

            st.success("""
            Mua hàng thành công
            
            Đã lưu Google Sheet
           
            """)

        except Exception as e:

            st.error(f"""
            !Lỗi Google Sheet
            
            {e}
            """)

        # =================================
        # SHOW SAVED DATA
        # =================================

        st.subheader(
            "📄 Dữ liệu vừa lưu"
        )

        st.dataframe(
            df_new,
            use_container_width=True
        )

        st.balloons()

        # =================================
        # RESET APP
        # =================================

        st.rerun()
