import streamlit as st
import random
from supabase import create_client

# --- CẤU HÌNH ---
st.set_page_config(page_title="Ôn tập Tin học 6 - GK2", layout="wide", initial_sidebar_state="collapsed")

# Ẩn menu
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

# Kết nối Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Lỗi kết nối Database. Vui lòng kiểm tra Secrets.")
    st.stop()

# --- TẢI DỮ LIỆU ---
@st.cache_data(ttl=60) 
def load_exam_data():
    """Lấy dữ liệu MCQ và Essay từ Supabase"""
    response = supabase.table("exam_questions").select("*").execute()
    
    mcq_list = []
    essay_list = []
    
    for item in response.data:
        if item['type'] == 'mcq':
            mcq_list.append(item['content'])
        elif item['type'] == 'essay':
            essay_list.append(item['content'])
            
    return mcq_list, essay_list

# --- KHỞI TẠO ĐỀ ---
if 'exam_setup' not in st.session_state:
    db_mcq, db_essay = load_exam_data()
    
    # Trộn MCQ
    shuffled_mcq = []
    original_mcq = db_mcq[:]
    random.shuffle(original_mcq) # Đảo câu hỏi
    
    for q in original_mcq:
        # Xử lý đáp án text/char
        correct_text = next((opt for opt in q["options"] if opt.startswith(q["correct_char"])), "")
        # Cắt bỏ "A. ", "B. "
        clean_opts = [opt[3:] for opt in q["options"]]
        clean_correct = correct_text[3:]
        
        # Đảo thứ tự đáp án
        random.shuffle(clean_opts)
        
        shuffled_mcq.append({
            "id": q["id"],
            "q": q["q"],
            "opts": clean_opts,
            "correct_text": clean_correct
        })
    
    # Sắp xếp tự luận theo ID (để đúng thứ tự đề cương)
    db_essay.sort(key=lambda x: x['id'])

    st.session_state['exam_setup'] = {
        "mcq": shuffled_mcq,
        "essay": db_essay
    }

setup = st.session_state['exam_setup']

# --- GIAO DIỆN ---
st.title("📝 ĐỀ CƯƠNG GIỮA KỲ II - TIN HỌC 6")
st.caption("Năm học 2025 - 2026")
st.markdown("---")

with st.form("exam_form"):
    st.text_input("Họ và tên học sinh:")
    st.text_input("Lớp:")
    
    # 1. TRẮC NGHIỆM
    st.header("I. TRẮC NGHIỆM")
    user_mcq = {}
    for i, q in enumerate(setup["mcq"]):
        st.write(f"**Câu {i+1} (Gốc câu {q['id']}):** {q['q']}")
        user_mcq[q['id']] = st.radio(f"chon_cau_{q['id']}", q['opts'], index=None, key=f"radio_{q['id']}", label_visibility="collapsed")
        st.divider()
        
    # 2. TỰ LUẬN
    st.header("II. TỰ LUẬN")
    st.info("Học sinh tự làm ra giấy, sau đó bấm Nộp bài để xem gợi ý đáp án.")
    for q in setup["essay"]:
        st.write(f"**Câu {q['id']}:** {q['q']}")
        st.text_area(f"Trả lời câu {q['id']}:", height=100, key=f"essay_{q['id']}")

    submitted = st.form_submit_button("Nộp bài & Xem kết quả")

# --- XỬ LÝ KẾT QUẢ ---
if submitted:
    score = 0
    total_mcq = len(setup["mcq"])
    if total_mcq == 0: total_mcq = 1
    point_per_q = 10.0 / (total_mcq + len(setup["essay"])) # Tính điểm tương đối
    
    # Chấm MCQ
    correct_cnt = 0
    for q in setup["mcq"]:
        if user_mcq.get(q['id']) == q['correct_text']:
            correct_cnt += 1
            
    st.success(f"Bạn làm đúng {correct_cnt}/{total_mcq} câu trắc nghiệm.")
    
    if correct_cnt >= (total_mcq * 0.5): # Đúng trên 50% trắc nghiệm mới hiện đáp án
        st.balloons()
        with st.expander("XEM ĐÁP ÁN CHI TIẾT", expanded=True):
            st.subheader("1. Đáp án Trắc nghiệm")
            for q in setup["mcq"]:
                u_ans = user_mcq.get(q['id'], "Chưa chọn")
                res = "✅" if u_ans == q['correct_text'] else "❌"
                st.write(f"**Câu gốc {q['id']}:** {res}")
                if u_ans != q['correct_text']:
                    st.write(f"👉 Đáp án đúng: :green[{q['correct_text']}]")
                st.divider()
            
            st.subheader("2. Gợi ý Tự luận")
            for q in setup["essay"]:
                st.markdown(f"**Câu {q['id']}:**")
                st.info(q['answer'])
    else:
        st.warning("Bạn cần làm đúng ít nhất 50% số câu trắc nghiệm để xem đáp án chi tiết!")
