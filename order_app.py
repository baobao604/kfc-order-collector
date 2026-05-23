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

    layout="wide"
)

# =========================================
# CREATE FOLDER
# =========================================

os.makedirs(
    "orders",
    exist_ok=True
)

# =========================================
# GOOGLE SHEET CONNECTION
# =========================================

scope = [

    "https://spreadsheets.google.com/feeds",

    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(

    "credentials.json",

    scope
)

client = gspread.authorize(
    creds
)

sheet = client.open(
    "KFC_Orders"
).sheet1

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
    "🍗 KFC ORDER COLLECTOR"
)

st.write("""
Hệ thống thu thập dữ liệu order online realtime
""")

# =========================================
# CUSTOMER ID
# =========================================

customer_id = st.text_input(

    "Customer ID",

    value=f"CUS_{random.randint(1000,9999)}"
)

# =========================================
# FOOD SELECTION
# =========================================

st.header(
    "🍔 Chọn món ăn"
)

selected_items = {}

bill_data = []

total_bill = 0

for food, price in MENU_PRICES.items():

    quantity = st.number_input(

        f"{food} - {price:,.0f} VNĐ",

        min_value=0,

        max_value=20,

        step=1,

        key=food
    )

    selected_items[food] = quantity

    if quantity > 0:

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
# BILL
# =========================================

st.subheader(
    "🧾 Hóa đơn"
)

if len(bill_data) > 0:

    st.dataframe(

        pd.DataFrame(bill_data),

        use_container_width=True
    )

st.success(
    f"💰 Tổng bill: {total_bill:,.0f} VNĐ"
)

# =========================================
# BUY BUTTON
# =========================================

if st.button(
    "✅ Mua hàng"
):

    if total_bill == 0:

        st.warning(
            "⚠️ Vui lòng chọn món ăn"
        )

    else:

        # =================================
        # CREATE ORDER
        # =================================

        order_id = random.randint(
            100000,
            999999
        )

        order_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        order_data = []

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
            ❌ Không thể ghi file CSV
            
            Hãy đóng file CSV trước
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
            ❌ Không thể ghi file Excel
            
            Hãy đóng file Excel trước
            """)

        # =================================
        # SAVE TO GOOGLE SHEET
        # =================================

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

        # =================================
        # SUCCESS
        # =================================

        st.success("""
        🎉 Mua hàng thành công
        
        ✅ Đã lưu Google Sheet
        ✅ Đã lưu CSV
        ✅ Đã lưu Excel
        """)

        st.subheader(
            "📄 Dữ liệu vừa lưu"
        )

        st.dataframe(
            df_new,
            use_container_width=True
        )

        st.balloons()

        # =================================
        # RESET
        # =================================

        st.rerun()
        st.write(sheet.get_all_records())