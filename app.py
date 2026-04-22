import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บและธีมสีฟ้า ---
st.set_page_config(page_title="AI Math Solver", page_icon="🧮", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #E6F3FF; }
    h1, h2, h3 { color: #0066CC; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #3399FF; color: white; height: 3em; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. การดึง API Key จาก Secrets (ต้องตั้งใน Streamlit Cloud ด้วย) ---
try:
    # พยายามดึงรหัสจาก Secrets ที่เราตั้งไว้ในหน้าเว็บ
    API_KEY = st.secrets["MY_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("❌ ไม่พบ API Key! กรุณาไปที่ Settings > Secrets แล้วใส่ MY_API_KEY")
    st.stop() # หยุดทำงานถ้าไม่มี Key เพื่อป้องกันหน้าจอขาว

# สร้าง Model เตรียมไว้
model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')

# --- 3. ส่วนของเครื่องคิดเลข (ใช้ Session State จำค่า) ---
if 'calc_input' not in st.session_state:
    st.session_state.calc_input = ""

def handle_click(char):
    if char == "C":
        st.session_state.calc_input = ""
    elif char == "=":
        if st.session_state.calc_input:
            try:
                # เปลี่ยนจากถาม AI มาใช้ Python คำนวณเอง (เร็วกว่า 100 เท่า)
                # เราใช้ eval() เพื่อคำนวณสมการคณิตศาสตร์โดยตรง
                result = eval(st.session_state.calc_input)
                st.session_state.calc_input = str(result)
            except Exception:
                # ถ้า Python งงกับสัญลักษณ์ค่อยส่งไปให้ AI ช่วย (Fallback)
                try:
                    res = model.generate_content(f"Calculate and return only the number: {st.session_state.calc_input}")
                    st.session_state.calc_input = res.text.strip()
                except:
                    st.session_state.calc_input = "Error"
    else:
        st.session_state.calc_input += str(char)

# --- 4. หน้าจอ UI ---
st.title("🧮 เครื่องคิดเลขคณิตศาสตร์อัจฉริยะ")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🔢 Calculator")
    # แสดงตัวเลขที่กำลังพิมพ์
    st.subheader(f"📟 {st.session_state.calc_input if st.session_state.calc_input else '0'}")
    
    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "C", "="]
    ]
    
    for row in buttons:
        cols = st.columns(4)
        for i, char in enumerate(row):
            cols[i].button(char, on_click=handle_click, args=(char,))

with col2:
    st.header("🤖 AI Math Tutor")
    prob = st.text_area("วางโจทย์ปัญหาที่นี่:", placeholder="เช่น มีส้ม 5 ผล แบ่งให้เพื่อน...")
    if st.button("ช่วยอธิบายข้อนี้หน่อย"):
        if prob:
            with st.spinner("AI กำลังคิด..."):
                response = model.generate_content(f"จงแก้โจทย์นี้และอธิบายทีละขั้นตอน: {prob}")
                st.write(response.text)
