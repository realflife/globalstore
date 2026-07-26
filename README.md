# Global Superstore - Executive Strategic BI & Interactive Decision Simulator

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Data Readiness: 100%](https://img.shields.io/badge/Data_Ready-100%25-brightgreen.svg)
![Deployment: GitHub Pages](https://img.shields.io/badge/Deploy-GitHub_Pages-blue.svg)

โปรเจกต์วิเคราะห์ข้อมูลเชิงลึก (EDA) และนำเสนอกลยุทธ์สำหรับผู้บริหารองค์กร **Global Superstore (2011–2014)** พัฒนาในรูปแบบ **Interactive Visual Suite & Client-side BI Decision Dashboard** โดยไม่ต้องพึ่งพา Backend Server หรือติดตั้งซอฟต์แวร์ BI เพิ่มเติม สามารถเปิดใช้งานและจำลองข้อมูลการตัดสินใจได้ทันทีผ่านเบราว์เซอร์หรือ **GitHub Pages**

---

## 🌟 จุดเด่นของระบบ (Key Features)

### 1. Dual-Mode Architecture (ระบบ 2 โหมดการนำเสนอในหนึ่งเดียว)
* 🎯 **โหมดที่ 1: สไลด์ผู้บริหารเน้นภาพ (7 Visual Executive Slides):**
  * ลดข้อความยาว เปลี่ยนเป็น KPI Cards, Badges และไอคอนสื่อความหมายที่ชัดเจน
  * กราฟโต้ตอบได้จริง (Interactive Chart.js) ในทุกสไลด์ เอาเมาส์ชี้เพื่อดูตัวเลขจริง หรือคลิก Legend เพื่อเปิด-ปิดเส้นกราฟ
  * มาพร้อมระบบ **"สคริปต์พูด (Speaking Notes)"** สำหรับผู้นำเสนอในห้องประชุม
* 📊 **โหมดที่ 2: จำลองการตัดสินใจด้วยข้อมูลจริง (Interactive BI Decision Dashboard):**
  * ฝังข้อมูล Cube ที่ประมวลผลแล้วกว่า 51,290 แถว ให้เบราว์เซอร์ทำงานเป็น BI Engine
  * **Interactive Filter Toolbar:** กรองตามปี (Year 2011-2014), ตลาด (Market) และหมวดหมู่สินค้า (Category) ได้แบบ Real-time
  * **Quick Action Filters:** ปุ่มกรองด่วนเพื่อตรวจจับจุดรั่วไหลทันที (สินค้าทำกำไรสูงสุด vs กลุ่มส่วนลดมรณะ >20% vs กลุ่มค่าจัดส่งกินกำไร)
  * **Live Search Table:** ตารางแสดงรายการจริงประกอบการตัดสินใจ พร้อมช่องค้นหาประเทศ สินค้า หรือ Order ID อย่างรวดเร็ว

---

## 🔍 ผลการวิเคราะห์เชิงยุทธศาสตร์ (Strategic Findings)

จากการทำความสะอาดข้อมูลครบ 6 ขั้นตอนตามหลัก **4-Mantra Debugging Discipline** เราพบคำตอบของคำถามผู้บริหารที่ว่า **"ทำไมยอดขายโต แต่กำไรกลับลดลง?"** ดังนี้:

1. 🔥 **กับดักส่วนลดมรณะ (The Death Discount Trap):**
   * จุดคุ้มทุนขององค์กรอยู่ที่ส่วนลดไม่เกิน **20%**
   * ทันทีที่ให้ส่วนลดตั้งแต่ 21% ขึ้นไป อัตรากำไรสุทธิพลิกติดลบเฉลี่ย **-42% ถึง -111%**
   * มีออเดอร์ถึง 20% ขององค์กร (10,361 รายการ) ที่ลดราคาลึก 31-80% สร้างผลขาดทุนรวมกว่า **-$793,526**
2. 🚢 **วิกฤตค่าจัดส่งสุดขั้วกินกำไร (Logistics Outliers):**
   * พบออเดอร์ส่งด่วนข้ามทวีป 634 รายการ ที่ค่าจัดส่งสูงกว่ากำไรขั้นต้นของสินค้า สร้างผลขาดทุนรวม **-$236,784**

---

## 📈 3 นโยบายสั่งการเพิ่มกำไร (Executive Action Plan)

1. **ตั้งเพดานส่วนลดเหล็กไม่เกิน 20% (Hard Cap):** ห้ามลดราคาสินค้าเกิน 20% ในทุกกลุ่มสินค้า โดยเฉพาะประเทศหลุมดำ (Turkey, Nigeria) ต้องยกเลิกโปรลด 50-70% ทันที ดึงกำไรกลับคืน **+$500,000+/ปี**
2. **ปฏิรูปโมเดลขายโต๊ะทำงาน (Bundle Selling):** ยกเลิกการขายโต๊ะทำงานเดี่ยวแบบลดราคา แต่เปลี่ยนเป็นบังคับขายคู่ (Bundle) กับเก้าอี้หรือตู้หนังสือที่กำไรสูง หยุดขาดทุนสะสม **-$64,083**
3. **คุมเข้มส่งด่วน Express & ข้ามทวีป:** กำหนดเกณฑ์ Minimum Order Value (ยอดซื้อขั้นต่ำ) สำหรับการส่ง Same Day / First Class หากไม่ถึงเกณฑ์ต้องส่งแบบ Standard ประหยัดงบขนส่ง **+$236,784/ปี**

---

## 🚀 วิธีการเข้าชมและใช้งาน (Quick Start & Deployment)

### การเข้าชมออนไลน์ (GitHub Pages)
1. ไปที่แท็บ **Settings** ของ Repository นี้บน GitHub
2. เลือกเมนูด้านซ้าย **Pages**
3. ที่หัวข้อย่อย **Branch** ให้เลือก `main` (หรือ `master`) โฟลเดอร์ `/ (root)` แล้วกด **Save**
4. รอระบบ Build ประมาณ 1 นาที คุณจะสามารถเข้าชม Presentation และ BI Dashboard ได้ทันทีที่ URL ของ GitHub Pages (เนื่องจากไฟล์หน้าหลักถูกตั้งชื่อเป็น `index.html` เรียบร้อยแล้ว)

### การรันและเปิดบนเครื่องส่วนตัว (Local Execution)
คุณสามารถดาวน์โหลดโค้ดชุดนี้ไปเปิดบนคอมพิวเตอร์ของคุณได้ทันทีโดยไม่ต้องตั้งค่า Server:
* ดับเบิ้ลคลิกเปิดไฟล์ `index.html` หรือ `global_superstore_eda_presentation.html` ด้วยเบราว์เซอร์ (Google Chrome, Edge, Safari หรือ Firefox)

### การประมวลผลข้อมูลใหม่ (Data Processing Pipeline)
หากต้องการอัปเดตข้อมูลหรือแก้ไขตรรกะการประมวลผล สามารถรันคำสั่งด้วย Python:
```bash
# 1. ติดตั้งไลบรารีที่จำเป็น (หากยังไม่ได้ติดตั้ง)
pip install pandas numpy

# 2. รันสคริปต์สร้างไฟล์ Cleaned Data และ HTML Presentation
python build_interactive_presentation.py
```

---

## 📂 โครงสร้างไฟล์ในโปรเจกต์ (Project Structure)
* `index.html`: หน้าหลักของ Interactive Presentation และ BI Dashboard (สำหรับ GitHub Pages)
* `global_superstore_eda_presentation.html`: ไฟล์คู่แฝดของ index.html
* `build_interactive_presentation.py`: สคริปต์หลักภาษา Python ในการอ่าน CSV, จัดทำ Cube Aggregation และ Generate HTML
* `Global_Superstore_Cleaned_2.csv`: ไฟล์ข้อมูลที่ผ่านการคลีนและวิศวกรรมฟีเจอร์เรียบร้อยแล้ว (51,290 แถว, 39 คอลัมน์) เข้ารหัส `utf-8-sig`
* `global_store.ipynb`: Jupyter Notebook สำหรับการทำ EDA เบื้องต้นและวิเคราะห์ปัญหา
* `generate_notebook.py`: สคริปต์สำหรับสร้าง Notebook อัตโนมัติ

---
*Developed with Data-Driven BI Best Practices & 4-Mantra Discipline.*
