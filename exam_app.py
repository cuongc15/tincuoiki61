import streamlit as st
import random
from supabase import create_client

# --- CẤU HÌNH ---
st.set_page_config(page_title="Thi Tin học 6", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

try:
    SUPABASE_URL = st.secrets["https://coljvrkxzihtsalsabhw.supabase.co"]
    SUPABASE_KEY = st.secrets["sb_publishable_13zNj8XyMESPmm-TUYvSng_Ov_Gi4z6"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Lỗi kết nối Database.")
    st.stop()

# --- TẢI DỮ LIỆU ---
@st.cache_data(ttl=60) 
def load_exam_data():
    response = supabase.table("exam_questions").select("*").execute()
    mcq_list = []
    essay_list = []
    for item in response.data:
        if item['type'] == 'mcq':
            mcq_list.append(item['content'])
        elif item['type'] == 'essay':
            essay_list.append(item['content'])
    return mcq_list, essay_list

if 'exam_setup' not in st.session_state:
    db_mcq, db_essay = load_exam_data()
    
    # Trộn MCQ
    shuffled_mcq = []
    original_mcq = db_mcq[:]
    random.shuffle(original_mcq)
    for q in original_mcq:
        correct_text = next((opt for opt in q["options"] if opt.startswith(q["correct_char"])), "")
        clean_opts = [opt[3:] for opt in q["options"]]
        clean_correct = correct_text[3:]
        random.shuffle(clean_opts)
        
        shuffled_mcq.append({
            "id": q["id"],
            "q": q["q"],
            "options": clean_opts,
            "correct_text": clean_correct,
            "image_url": q.get("image_url") # Lấy link ảnh
        })
    
    # Sắp xếp Essay theo ID
    db_essay.sort(key=lambda x: x['id'])
    
    st.session_state['exam_setup'] = {"mcq": shuffled_mcq, "essay": db_essay}

setup = st.session_state['exam_setup']

# --- GIAO DIỆN ---
st.title("📝 BÀI KIỂM TRA TIN HỌC")
st.markdown("---")

with st.form("exam_form"):
    st.text_input("Họ và tên học sinh:")
    st.text_input("Lớp:")
    
    # 1. TRẮC NGHIỆM
    if setup["mcq"]:
        st.header("I. TRẮC NGHIỆM")
        user_mcq = {}
        for i, q in enumerate(setup["mcq"]):
            st.markdown(f"**Câu {i+1}:** {q['q']}")
            
            # Hiện ảnh MCQ
            if q.get("image_url"):
                st.image(q["image_url"], width=300)

            user_mcq[q['id']] = st.radio(f"radio_{q['id']}", q['options'], index=None, key=f"r_{q['id']}", label_visibility="collapsed")
            st.divider()
    
    # 2. TỰ LUẬN
    if setup["essay"]:
        st.header("II. TỰ LUẬN")
        st.info("Học sinh làm bài ra giấy. Sau khi nộp bài sẽ xem được gợi ý đáp án.")
        for q in setup["essay"]:
            st.markdown(f"**Câu {q['id']}:** {q['q']}")
            
            # Hiện ảnh Tự luận
            if q.get("image_url"):
                st.image(q["image_url"], width=400, caption=f"Hình minh họa câu {q['id']}")
                
            st.text_area(f"Bài làm câu {q['id']}:", height=100, key=f"essay_{q['id']}")
            st.divider()

    submitted = st.form_submit_button("NỘP BÀI")

# --- KẾT QUẢ ---
if submitted:
    total_mcq = len(setup["mcq"])
    correct_cnt = 0
    for q in setup["mcq"]:
        if user_mcq.get(q['id']) == q['correct_text']:
            correct_cnt += 1
            
    # Tính điểm (Giả sử 10 điểm chia đều hoặc tùy bạn chỉnh)
    st.success(f"Kết quả Trắc nghiệm: {correct_cnt}/{total_mcq} câu đúng.")
    
    # Điều kiện xem đáp án
    if total_mcq > 0 and correct_cnt < (total_mcq * 0.5):
        st.error("Bạn phải làm đúng trên 50% trắc nghiệm để xem đáp án!")
    else:
        st.balloons()
        with st.expander("XEM ĐÁP ÁN & GỢI Ý", expanded=True):
            # Đáp án MCQ
            if setup["mcq"]:
                st.subheader("1. Đáp án Trắc nghiệm")
                for q in setup["mcq"]:
                    u_ans = user_mcq.get(q['id'], "Chưa chọn")
                    if u_ans == q['correct_text']:
                        st.markdown(f"Câu {q['id']}: ✅ :green[{u_ans}]")
                    else:
                        st.markdown(f"Câu {q['id']}: ❌ (Bạn chọn: {u_ans}) -> Đúng: :green[{q['correct_text']}]")

            # Đáp án Tự luận
            if setup["essay"]:
                st.subheader("2. Gợi ý Tự luận")
                for q in setup["essay"]:
                    st.markdown(f"**Câu {q['id']}:**")
                    # Hiện đáp án lấy từ DB
                    st.info(q.get('answer', 'Không có gợi ý.'))
