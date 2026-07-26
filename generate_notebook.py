import nbformat as nbf
import nbclient
import json

nb = nbf.v4.new_notebook()

# Define cells
cells = []

# Cell 0: MD
cells.append(nbf.v4.new_markdown_cell("""# 🛠️ Comprehensive EDA & Data Cleaning for Global Superstore Dashboard

**วัตถุประสงค์ (Objective)**: 
สำรวจปัญหาและข้อผิดพลาดของข้อมูล (Exploratory Data Analysis - EDA), อธิบายสาเหตุของข้อผิดพลาด, และดำเนินการแก้ไข (Data Cleaning Pipeline) เพื่อเตรียมชุดข้อมูลให้สะอาด ถูกต้อง พร้อมสำหรับการนำไปสร้าง **Dashboard** ในเครื่องมือ BI ต่างๆ เช่น Power BI, Tableau, Looker Studio หรือ Excel

---

## 📋 สรุปข้อผิดพลาดสำคัญที่พบจากการทำ EDA (Executive Summary of Data Anomalies)
ในการนำข้อมูล Global Superstore ไปทำ Dashboard หากไม่แก้ไขปัญหาเหล่านี้ จะทำให้กราฟและตัวเลข KPI ผิดเพี้ยนทันที:

1. **🚨 Order ID Collisions (รหัสคำสั่งซื้อซ้ำซ้อนข้ามลูกค้าและข้ามประเทศ):** 
   - พบ `Order ID` จำนวน **659 รหัส** ที่ซ้ำกันในระบบ แต่เป็นคำสั่งซื้อของลูกค้าคนละคน คนละวันที่ และคนละประเทศ (เช่น `ES-2011-2075610` ปรากฏทั้งในฝรั่งเศสและเยอรมนี) เกิดจากการรวมฐานข้อมูล ERP ของแต่ละภูมิภาคที่ใช้เลข Running Number ซ้ำกัน
   - *ผลกระทบต่อ Dashboard:* หากใช้ `Order ID` เป็น Primary Key ในการ Join หรือ Group by ยอดขายรวมและจำนวนออเดอร์จะผิดพลาดทันที
2. **🚨 Missing Postal Codes & Float Data Type (รหัสไปรษณีย์หาย 80.5% และถูกแปลงเป็นเลขทศนิยม):**
   - พบค่าว่าง (NaN) ในคอลัมน์ `Postal Code` ถึง **41,296 แถว (80.52%)** เนื่องจากระบบบันทึกรหัสไปรษณีย์เฉพาะลูกค้าในสหรัฐอเมริกา (United States) เมื่อมีค่าว่าง Pandas จึงนำเข้าเป็น `float64` (เช่น `10024.0`)
   - *ผลกระทบต่อ Dashboard:* โปรแกรม BI จะมองว่ารหัสไปรษณีย์เป็น "ตัวเลขสำหรับคำนวณ" ทำให้เกิดการนำรหัสไปรษณีย์ไปหาผลรวมหรือค่าเฉลี่ย และแสดงผลติดทศนิยม `.0` บนแผนที่
3. **🚨 Hidden Whitespace in String Columns (ช่องว่างที่ซ่อนอยู่หน้า/หลังชื่อสินค้า):**
   - พบข้อความที่มีช่องว่างเกินมาหน้าหรือหลังข้อความ (เช่น `" Eldon Folders, Single Width"` vs `"Eldon Folders, Single Width"`) ในคอลัมน์ `Product Name` จำนวน 16 แถว
   - *ผลกระทบต่อ Dashboard:* ตัวกรอง (Slicer) และกราฟรายสินค้าจะแยกสินค้าตัวเดียวกันออกเป็น 2 แท่ง/2 หมวดหมู่
4. **🚨 Duplicate Line Items (รายการสินค้าเดิมซ้ำในออเดอร์เดียวกัน):**
   - พบคู่แถวสินค้า 38 คู่ (76 แถว) ที่มี `Order ID` และ `Product ID` เหมือนกันทุกประการ แต่มีจำนวนชิ้น (Quantity) หรือค่าจัดส่งต่างกัน เป็นกรณีการทยอยจัดส่ง (Split Shipment) หรือบันทึกแยกรายการ
   - *ผลกระทบต่อ Dashboard:* หากไม่ติดป้ายกำกับ (Flag) หรือจัดการให้ถูกต้อง การนับจำนวน SKU หรือรายการสินค้าต่อออเดอร์จะนับซ้ำ
5. **🚨 Text Date Formats & Lack of Calendar/KPI Dimensions (วันที่เป็น Text และขาดมิติการวิเคราะห์):**
   - คอลัมน์ `Order Date` และ `Ship Date` ถูกจัดเก็บเป็น String (`DD-MM-YYYY`) ทำให้ไม่สามารถ Plot กราฟแนวโน้มเวลาได้ และขาด KPI ด้านระยะเวลาจัดส่ง
6. **🚨 Abnormal Over Sales & Shipping Cost Outliers (ยอดขายและค่าขนส่งสูงผิดปกติ Outliers และตัวเลขทศนิยม 3-5 ตำแหน่ง):**
   - พบว่าตัวเลขการเงิน (`Sales`, `Profit`, `Shipping Cost`, `Discount`) มีทศนิยมเกินจริง 3-5 ตำแหน่ง (เช่น `11199.968`)
   - **ยอดขายสูงผิดปกติ (Sales Outliers):** พบรายการ Enterprise Hardware สูงสุดถึง **$22,638.48** (สูงกว่าค่าเฉลี่ย 90 เท่า)
   - **ค่าขนส่งสูงผิดปกติ (Shipping Cost Outliers):** พบค่าจัดส่งสูงถึง **$933.57** (เกณฑ์ Outlier คือ $90) และค้นพบความลับทางธุรกิจที่น่าตกใจว่า มีออเดอร์ที่ค่าขนส่งแพงมากจนกินกำไรหมดและติดลบ (Negative Profit) ถึง **634 ออเดอร์ สร้างความเสียหายรวมกว่า -$236,784.32!**
   - *ผลกระทบต่อ Dashboard:* หากไม่สร้างกลุ่ม Tiering และ Warning Flag จะทำให้สเกลของกราฟพัง และผู้บริหารไม่สามารถกรองดูออเดอร์ที่ค่าส่งกัดกินกำไรบริษัทได้"""))

# Cell 1: Code
cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ตั้งค่าการแสดงผลตารางของ Pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)
pd.set_option('display.float_format', '{:,.2f}'.format)

# โหลดข้อมูล
file_path = "/mnt/hades/HadesData/AI-visual/Global_Superstore2.csv"
df = pd.read_csv(file_path, encoding='latin1')

print(f"📊 ขนาดข้อมูลเริ่มต้น: {len(df):,} แถว | {df.shape[1]} คอลัมน์")
display(df.head(5))"""))

# Cell 2: MD
cells.append(nbf.v4.new_markdown_cell("""---
## 🔍 ส่วนที่ 1: เจาะลึกหลักฐานข้อผิดพลาดจากการทำ EDA (EDA Proof of Data Anomalies)

มาดูหลักฐานข้อผิดพลาดแต่ละจุดด้วยโค้ด เพื่อความเข้าใจที่ชัดเจนก่อนดำเนินการแก้ไข:"""))

# Cell 3: Code
cells.append(nbf.v4.new_code_cell("""# 1.1 ตรวจสอบปัญหา Order ID ซ้ำซ้อนข้ามลูกค้าและประเทศ (Order ID Collisions)
order_customers = df.groupby('Order ID')['Customer ID'].nunique()
collision_orders = order_customers[order_customers > 1]
print(f"🚨 จำนวน Order ID ที่มีลูกค้ามากกว่า 1 คน (Collision): {len(collision_orders)} รหัส")

# ตัวอย่าง Order ID ที่ซ้ำกันข้ามประเทศ
sample_oid = "ES-2011-2075610"
print(f"\\nตัวอย่างออเดอร์ที่มีปัญหา: {sample_oid}")
display(df[df['Order ID'] == sample_oid][['Row ID', 'Order ID', 'Order Date', 'Customer ID', 'Customer Name', 'Country', 'Product Name']])"""))

# Cell 4: Code
cells.append(nbf.v4.new_code_cell("""# 1.2 ตรวจสอบ Postal Code ที่ขาดหายและประเภทข้อมูลผิดพลาด
null_postal = df['Postal Code'].isnull().sum()
print(f"🚨 Postal Code มีค่าว่างทั้งหมด: {null_postal:,} แถว ({null_postal/len(df)*100:.2f}%)")
print(f"🚨 ชนิดข้อมูลปัจจุบันของ Postal Code คือ: {df['Postal Code'].dtype} (ซึ่งแสดงผลเป็นทศนิยม เช่น 10024.0)")
print("ประเทศที่มีข้อมูล Postal Code ไม่เป็นค่าว่าง:", df[df['Postal Code'].notnull()]['Country'].unique())

# 1.3 ตรวจสอบช่องว่างหน้า-หลัง (Leading/Trailing Whitespace)
print("\\n--- ตรวจสอบ Whitespace ในคอลัมน์ที่เป็น Text ---")
for col in ['Product Name', 'Customer Name', 'City', 'State']:
    stripped = df[col].astype(str).str.strip()
    diff = (df[col].astype(str) != stripped).sum()
    if diff > 0:
        print(f"🚨 พบช่องว่างหน้า/หลังในคอลัมน์ '{col}' จำนวน: {diff} แถว!")

# 1.4 ตรวจสอบปัญหาทศนิยม และ ยอดขาย/ค่าขนส่งที่สูงผิดปกติ (Sales & Shipping Cost Outliers)
print("\\n--- ตรวจสอบทศนิยมในคอลัมน์การเงิน ---")
decimals_len = df['Sales'].astype(str).apply(lambda x: len(x.split('.')[1]) if '.' in x else 0)
print(f"🚨 จำนวนทศนิยมสูงสุดที่พบใน Sales: {decimals_len.max()} ตำแหน่ง (เช่น {df[decimals_len > 2]['Sales'].iloc[0]})")

print("\\n--- ตรวจสอบยอดขายสูงผิดปกติ (Sales Outliers) ---")
q1_s = df['Sales'].quantile(0.25)
q3_s = df['Sales'].quantile(0.75)
iqr_s = q3_s - q1_s
extreme_sales = q3_s + (3 * iqr_s)
outliers_s_cnt = (df['Sales'] > extreme_sales).sum()
print(f"💡 Sales เฉลี่ย (Mean): ${df['Sales'].mean():,.2f} | มัธยฐาน (Median): ${df['Sales'].median():,.2f} | สูงสุด (Max): ${df['Sales'].max():,.2f}")
print(f"🚨 พบยอดขาย Enterprise Outliers (> ${extreme_sales:,.2f}): {outliers_s_cnt:,} แถว ({outliers_s_cnt/len(df)*100:.2f}%)")

print("\\n--- ตรวจสอบค่าขนส่งสูงผิดปกติ และการกัดกินกำไร (Shipping Cost Outliers & Profit Drain) ---")
q1_c = df['Shipping Cost'].quantile(0.25)
q3_c = df['Shipping Cost'].quantile(0.75)
iqr_c = q3_c - q1_c
extreme_cost = q3_c + (3 * iqr_c)
outliers_c = df[df['Shipping Cost'] > extreme_cost]
loss_from_ship = outliers_c[outliers_c['Profit'] < 0]
print(f"💡 Shipping Cost เฉลี่ย: ${df['Shipping Cost'].mean():,.2f} | มัธยฐาน: ${df['Shipping Cost'].median():,.2f} | สูงสุด: ${df['Shipping Cost'].max():,.2f}")
print(f"🚨 พบค่าขนส่ง Extreme Outliers (> ${extreme_cost:,.2f}): {len(outliers_c):,} แถว ({len(outliers_c)/len(df)*100:.2f}%)")
print(f"🔥 ความเสี่ยงร้ายแรงทางธุรกิจ: พบออเดอร์ที่ค่าส่งสูงผิดปกติและ 'ขาดทุน (Negative Profit)': {len(loss_from_ship):,} รายการ")
print(f"💸 มูลค่าความเสียหายรวมจากค่าส่งพุ่งจนติดลบ: ${loss_from_ship['Profit'].sum():,.2f}!")
print("\\nตัวอย่าง 5 อันดับออเดอร์ที่ค่าขนส่งแพงที่สุดจนบริษัทขาดทุนย่ำแย่:")
display(loss_from_ship.nlargest(5, 'Shipping Cost')[['Order ID', 'Product Name', 'Ship Mode', 'Country', 'Sales', 'Shipping Cost', 'Profit']])"""))

# Cell 5: MD
cells.append(nbf.v4.new_markdown_cell("""---
## 🧹 ส่วนที่ 2: ดำเนินการแก้ไขและทำความสะอาดข้อมูล (Data Cleaning Pipeline)

เราจะทำการแก้ไขข้อมูลตามลำดับ 6 ขั้นตอน (6-Step Cleaning Pipeline) เพื่อให้ได้ชุดข้อมูลที่สมบูรณ์ที่สุดสำหรับ Dashboard:"""))

# Cell 6: Code
cells.append(nbf.v4.new_code_cell("""# สร้าง DataFrame ใหม่สำหรับข้อมูลที่ทำความสะอาดแล้ว
df_clean = df.copy()

# Step 1: ลบ whitespace หน้าและหลังข้อความในทุกคอลัมน์ที่เป็น String
str_cols = df_clean.select_dtypes(include='object').columns
for col in str_cols:
    df_clean[col] = df_clean[col].astype(str).str.strip()
print("✅ Step 1: ลบ Whitespace หน้า-หลังข้อความเรียบร้อย")

# Step 2: แปลงวันที่จาก String เป็น Datetime และสร้างคอลัมน์มิติเวลาสำหรับ Dashboard
df_clean['Order Date'] = pd.to_datetime(df_clean['Order Date'], format='%d-%m-%Y')
df_clean['Ship Date'] = pd.to_datetime(df_clean['Ship Date'], format='%d-%m-%Y')

# สร้าง Calendar Dimensions เพื่อให้ใช้ง่ายใน Slicer/Filter ของ Dashboard
df_clean['Order Year'] = df_clean['Order Date'].dt.year
df_clean['Order Quarter'] = 'Q' + df_clean['Order Date'].dt.quarter.astype(str)
df_clean['Order Month'] = df_clean['Order Date'].dt.month
df_clean['Order Month Name'] = df_clean['Order Date'].dt.strftime('%b')
df_clean['Order Year-Month'] = df_clean['Order Date'].dt.to_period('M').astype(str)
df_clean['Order Day of Week'] = df_clean['Order Date'].dt.day_name()

# สร้าง KPI ด้านการดำเนินงาน: ระยะเวลาจัดส่ง (Shipping Delay SLA)
df_clean['Shipping Delay (Days)'] = (df_clean['Ship Date'] - df_clean['Order Date']).dt.days
print("✅ Step 2: แปลง Datetime และสร้าง Calendar / SLA Dimensions เรียบร้อย")

# Step 3: แก้ไข Postal Code ไม่ให้ติดทศนิยม (.0) และแทนค่าว่างด้วย 'Non-US'
df_clean['Postal Code Clean'] = df_clean['Postal Code'].fillna(-1).astype(int).astype(str)
df_clean['Postal Code Clean'] = df_clean['Postal Code Clean'].replace('-1', 'Non-US')
print("✅ Step 3: แปลง Postal Code เป็น String และเติม 'Non-US' เรียบร้อย")

# Step 4: สร้าง Global Unique Order ID เพื่อแก้ปัญหาออเดอร์ซ้ำข้ามประเทศ
df_clean['Global Order ID'] = df_clean['Order ID'] + "_" + df_clean['Customer ID'] + "_" + df_clean['Country']
print("✅ Step 4: สร้าง Global Order ID เพื่อเป็น Primary Key ที่แท้จริงเรียบร้อย")

# Step 5: สร้าง Flag ระบุรายการสินค้าที่จัดส่งแบบ Split Shipment ในออเดอร์เดียวกัน
df_clean['Is Split Shipment Item'] = df_clean.duplicated(subset=['Global Order ID', 'Product ID'], keep=False)
print("✅ Step 5: ระบุรายการสินค้าที่เป็น Split Shipment เรียบร้อย")

# Step 6: แก้ปัญหาทศนิยม และการจัดการ ยอดขาย/ค่าขนส่งสูงผิดปกติ (Outliers Segmentation & Warning Flags)
# 6.1 ปัดเศษทศนิยมทางการเงินให้เหลือ 2 ตำแหน่งตามมาตรฐานบัญชี
for num_col in ['Sales', 'Profit', 'Shipping Cost', 'Discount']:
    df_clean[num_col] = df_clean[num_col].round(2)

# 6.2 สร้างกลุ่มยอดขาย (Order Value Tier) และ Outlier Flag
q1_s = df_clean['Sales'].quantile(0.25)
q3_s = df_clean['Sales'].quantile(0.75)
iqr_s = q3_s - q1_s
upper_s = q3_s + (1.5 * iqr_s)
extreme_s = q3_s + (3 * iqr_s)

df_clean['Order Value Tier'] = df_clean['Sales'].apply(
    lambda x: '1. Standard Order (<= $581)' if x <= upper_s else ('2. High Value ($581-$912)' if x <= extreme_s else '3. Enterprise/Outlier (> $912)')
)
df_clean['Is Extreme Sales Outlier'] = df_clean['Sales'] > extreme_s

# 6.3 สร้างกลุ่มค่าขนส่ง (Shipping Cost Tier) และระบบแจ้งเตือนค่าส่งกัดกินกำไร (Profit Drain Flag)
q1_c = df_clean['Shipping Cost'].quantile(0.25)
q3_c = df_clean['Shipping Cost'].quantile(0.75)
iqr_c = q3_c - q1_c
upper_c = q3_c + (1.5 * iqr_c)
extreme_c = q3_c + (3 * iqr_c)

df_clean['Shipping Cost Tier'] = df_clean['Shipping Cost'].apply(
    lambda x: '1. Standard Shipping (<= $57)' if x <= upper_c else ('2. High Shipping ($57-$90)' if x <= extreme_c else '3. Extreme Outlier (> $90)')
)
df_clean['Is Extreme Shipping Outlier'] = df_clean['Shipping Cost'] > extreme_c
df_clean['Is Shipping Cost Draining Profit'] = (df_clean['Shipping Cost'] > extreme_c) & (df_clean['Profit'] < 0)

print("✅ Step 6: ปัดเศษทศนิยม พร้อมสร้าง Tier และ Warning Flag สำหรับทั้ง Sales และ Shipping Cost เรียบร้อย")"""))

# Cell 7: MD
cells.append(nbf.v4.new_markdown_cell("""---
## 🎯 ส่วนที่ 3: ตรวจสอบผลลัพธ์หลังการทำความสะอาด (Post-Cleaning Verification & Outlier Analysis)

มาดูกันว่าข้อมูลหลังทำความสะอาดมีความพร้อมสำหรับ Dashboard มากน้อยเพียงใด โดยเฉพาะการแบ่งกลุ่มยอดขาย และค่าขนส่ง Over ผิดปกติ:"""))

# Cell 8: Code
cells.append(nbf.v4.new_code_cell("""# ตรวจสอบคุณภาพข้อมูลและการแบ่งกลุ่ม Outliers
print("=== ตรวจสอบสถิติการแบ่งกลุ่มค่าขนส่ง (Shipping Cost Tier Distribution) ===")
ship_summary = df_clean.groupby('Shipping Cost Tier')['Shipping Cost'].agg(['count', 'sum', 'mean', 'max']).reset_index()
ship_summary['Cost Share (%)'] = (ship_summary['sum'] / df_clean['Shipping Cost'].sum()) * 100
display(ship_summary)

print("\\n=== สถิติระบบแจ้งเตือน: ค่าขนส่งสูงผิดปกติที่กัดกินจนติดลบ (Shipping Cost Draining Profit) ===")
drain_summary = df_clean.groupby('Is Shipping Cost Draining Profit')[['Sales', 'Shipping Cost', 'Profit']].sum().reset_index()
drain_summary['Order Count'] = df_clean['Is Shipping Cost Draining Profit'].value_counts().values
display(drain_summary)

print("\\n💡 คำอธิบายเชิงธุรกิจ (Business Rationale):")
print(f"• ออเดอร์กลุ่ม 'Extreme Outlier (> $90)' มีเพียง 3,415 รายการ (6.7%) แต่คิดเป็น {ship_summary.iloc[2]['Cost Share (%)']:.1f}% ของค่าใช้จ่ายขนส่งทั้งบริษัท!")
print(f"• ที่สำคัญคือ มีถึง 634 ออเดอร์ที่ 'ค่าขนส่งสูงจนกินกำไรหมด (Is Shipping Cost Draining Profit = True)' สร้างผลขาดทุนรวมถึง ${drain_summary[drain_summary['Is Shipping Cost Draining Profit']==True]['Profit'].iloc[0]:,.2f}!")
print("• การสร้าง Warning Flag นี้ใน Dashboard จะช่วยให้ผู้บริหารฝ่าย Operation กรองดูออเดอร์ที่ขาดทุนจากค่าขนส่งเพื่อปรับปรุงเส้นทางหรือสัญญาบริษัทขนส่งได้ทันที")

print("\\n=== ตัวอย่างข้อมูลพร้อมใช้ทำ Dashboard ===")
display(df_clean[['Global Order ID', 'Order Date', 'Country', 'Product Name', 'Sales', 'Shipping Cost', 'Profit', 'Shipping Cost Tier', 'Is Shipping Cost Draining Profit']].head(10))"""))

# Cell 9: MD
cells.append(nbf.v4.new_markdown_cell("""---
## 💾 ส่วนที่ 4: บันทึกชุดข้อมูลสะอาดสำหรับนำไปสร้าง Dashboard (Exporting Cleaned Data for BI Tools)

บันทึก DataFrame ที่ทำความสะอาดแล้วเป็นไฟล์ **`Global_Superstore_Cleaned.csv`** และ **`Global_Superstore_Cleaned_2.csv`** ด้วยการเข้ารหัส `utf-8-sig` (รองรับภาษาไทยและอักขระพิเศษทุกภาษาเมื่อเปิดใน Excel, Power BI หรือ Tableau)"""))

# Cell 10: Code
cells.append(nbf.v4.new_code_cell("""# บันทึกเป็นไฟล์ CSV พร้อมใช้ทำ Dashboard (บันทึกทั้ง 2 ชื่อไฟล์เพื่อรองรับทุกการอัปเดต)
output_csv_1 = "/mnt/hades/HadesData/AI-visual/Global_Superstore_Cleaned.csv"
output_csv_2 = "/mnt/hades/HadesData/AI-visual/Global_Superstore_Cleaned_2.csv"
df_clean.to_csv(output_csv_1, index=False, encoding='utf-8-sig')
df_clean.to_csv(output_csv_2, index=False, encoding='utf-8-sig')

print(f"🎉 บันทึกไฟล์ข้อมูลที่ทำความสะอาดเรียบร้อยแล้วที่:\\n  - {output_csv_1}\\n  - {output_csv_2}")
print(f"📦 ขนาดชุดข้อมูลพร้อมใช้: {len(df_clean):,} แถว | {df_clean.shape[1]} คอลัมน์")
print("🚀 คุณสามารถนำไฟล์ Global_Superstore_Cleaned.csv ไปโหลดเข้า Power BI, Tableau, Looker Studio หรือ Excel ได้ทันทีโดยไม่ต้องทำการ Transformed เพิ่มเติม!")"""))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {
        'display_name': 'global_store_venv (3.10.12)',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'codemirror_mode': {'name': 'ipython', 'version': 3},
        'file_extension': '.py',
        'mimetype': 'text/x-python',
        'name': 'python',
        'nbconvert_exporter': 'python',
        'pygments_lexer': 'ipython3',
        'version': '3.10.12'
    }
}

out_path = "/mnt/hades/HadesData/AI-visual/global_store.ipynb"
with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook created. Executing with nbclient...")
client = nbclient.NotebookClient(nb, timeout=600, kernel_name='python3')
client.execute()

with open(out_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("✅ Successfully executed and saved notebook with all outputs!")
