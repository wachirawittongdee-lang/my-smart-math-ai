import streamlit as st
import google.generativeai as genai

# --- 1. การตั้งค่าหน้าตาและธีม (สีฟ้า) ---
st.set_page_config(
    page_title="AI Math Solver 3.1",
    page_icon="🧮",
    layout="wide" # ขยายหน้าต่างให้เต็มจอ
)

# ใช้ CSS เพื่อเปลี่ยนสีพื้นหลังและสีตัวอักษรให้เป็นธีมสีฟ้า
st.markdown("""
<style>
    .stApp {
        background-color: #E6F3FF; /* สีฟ้าอ่อนมากๆ สำหรับพื้นหลัง */
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF;
        border-color: #3399FF; /* ขอบสีฟ้า */
    }
    h1, h2, h3 {
        color: #0066CC; /* หัวข้อสีฟ้าเข้ม */
    }
    .stButton>button {
        background-color: #3399FF; /* ปุ่มสีฟ้า */
        color: white;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #0066CC; /* ปุ่มเข้มขึ้นเมื่อเอาเมาส์ชี้ */
        color: white;
    }
    /* ปรับปรุงสไตล์สำหรับส่วนอธิบายวิธีการคิด */
    .stCode {
        background-color: #FFFFFF;
        border-left: 5px solid #3399FF;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. การตั้งค่า API Key ---
# ปลอดภัยไว้ก่อน: การวาง API Key โดยตรงในโค้ดไม่แนะนำสำหรับการใช้งานจริง
# แต่สำหรับการเรียนรู้ในขั้นตอนนี้ คุณสามารถวางรหัสที่คุณมีลงไปได้ครับ
# (ลบรหัสของคุณออกเพื่อความปลอดภัยในการสาธิต)
API_KEY = st.secrets["MY_API_KEY"]
genai.configure(api_key=API_KEY)


# --- 3. การเลือกโมเดล (ใช้รุ่น 3.1 ที่คุณใช้ได้) ---
# เราจะสร้างโมเดลสองตัว ตัวหนึ่งสำหรับการคำนวณทั่วไป และอีกตัวที่มี System Instruction สำหรับ AI ช่วยสอน
base_model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')

# โมเดลสำหรับ AI ช่วยสอน (ใส่ "หัวสมอง" ให้มันเป็นครูคณิตศาสตร์)
teaching_model = genai.GenerativeModel(
    model_name='models/gemini-3.1-flash-lite-preview',
    system_instruction="คุณคือครูคณิตศาสตร์ผู้เชี่ยวชาญและใจดี หน้าที่ของคุณคือช่วยผู้เรียนแก้โจทย์ปัญหาคณิตศาสตร์และสมการ ไม่ใช่แค่ให้คำตอบสุดท้าย แต่ต้อง **อธิบายวิธีการคิดแบบละเอียดทีละขั้นตอน** (Step-by-Step) อย่างชัดเจนและสุภาพ ใช้ภาษาง่ายๆ และแสดงสัญลักษณ์ทางคณิตศาสตร์ให้ถูกต้อง"
)


# --- 4. ส่วนประกอบหน้าเว็บ (UI) ---
st.title("🧮 เครื่องคิดเลขคณิตศาสตร์อัจฉริยะ (Version 3.1)")
st.markdown("---")

# แบ่งหน้าจอเป็น 2 ฝั่ง: ฝั่งเครื่องคิดเลข และ ฝั่ง AI ช่วยสอน
col1, col2 = st.columns([1, 1])

# --- ฝั่งที่ 1: เครื่องคิดเลขคณิตศาสตร์แบบกดปุ่ม ---
with col1:
    st.header("🔢 เครื่องคิดเลขคณิตศาสตร์")
    
    # 1. สร้างตัวแปรไว้จำค่าตัวเลขที่พิมพ์ (ถ้ายังไม่มีให้สร้างใหม่)
    if 'calc_input' not in st.session_state:
        st.session_state.calc_input = ""
    
    # 2. ฟังก์ชันจัดการเมื่อกดปุ่ม
    def handle_click(char):
        if char == "C":
            st.session_state.calc_input = ""
        elif char == "=":
            try:
                # ส่งไปให้ AI คำนวณเพื่อความแม่นยำ
                prompt = f"Calculate this and return only the number: {st.session_state.calc_input}"
                response = base_model.generate_content(prompt)
                st.session_state.calc_input = response.text.strip()
            except:
                st.session_state.calc_input = "Error"
        else:
            st.session_state.calc_input += str(char)

    # 3. ช่องแสดงผล (ห้ามลบอันนี้ เพราะมันจะโชว์ตัวเลขที่เรากด)
    st.text_input("Display", value=st.session_state.calc_input, key="display", disabled=True)

    # 4. ปุ่มกด
    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "C", "="]
    ]

    for row in buttons:
        cols = st.columns(4)
        for i, char in enumerate(row):
            # เมื่อกดปุ่ม ให้ไปเรียกฟังก์ชัน handle_click
            cols[i].button(char, on_click=handle_click, args=(char,), use_container_width=True)

# --- ฝั่งที่ 2: AI ช่วยแก้โจทย์ปัญหาคณิตศาสตร์และสมการพร้อมอธิบาย ---
with col2:
    st.header("🤖 AI ช่วยทำโจทย์คณิต (พร้อมวิธีคิด)")
    
    # ช่องพิมพ์โจทย์ปัญหาหรือสมการ
    math_problem = st.text_area("พิมพ์โจทย์ปัญหาคณิตศาสตร์หรือสมการที่คุณต้องการให้ช่วย:", height=150)

    # ปุ่มสั่งให้ AI ช่วย
    solve_btn = st.button("ให้ AI ช่วยแก้โจทย์")

    # เมื่อกดปุ่มสั่งให้ AI ช่วย
    if solve_btn and math_problem:
        st.markdown("---")
        st.info("กำลังประมวลผล...")
        
        try:
            # ส่งโจทย์ไปหาโมเดลที่มี System Instruction
            response = teaching_model.generate_content(f"Solve this math problem and explain the steps: {math_problem}")
            
            st.success("🤖 AI สรุปวิธีการคิดมาให้แล้วครับ:")
            # แสดงคำตอบแบบจัดรูปแบบ (Markdown) เพื่อให้สัญลักษณ์คณิตศาสตร์ดูดี
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI: {e}")
    elif solve_btn and not math_problem:
        st.warning("กรุณาพิมพ์โจทย์ปัญหาคณิตศาสตร์ก่อนครับ")

# --- 5. ส่วนท้ายหน้าเว็บ ---
st.markdown("---")
st.caption("พัฒนาโดยใช้ Google Gemini 3.1 & Streamlit • ธีมสีฟ้าสดใส")
