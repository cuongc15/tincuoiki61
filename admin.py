import streamlit as st
import re
import time
from supabase import create_client
import docx
from PyPDF2 import PdfReader


# =============================
# CẤU HÌNH SUPABASE
# =============================

try:
    SUPABASE_URL = st.secrets["https://coljvrkxzihtsalsabhw.supabase.co"]
    SUPABASE_KEY = st.secrets["sb_publishable_13zNj8XyMESPmm-TUYvSng_Ov_Gi4z6"]
except:
    st.warning("Chưa cấu hình Secrets. Nhập tạm để test local.")
    SUPABASE_URL = st.text_input("Supabase URL")
    SUPABASE_KEY = st.text_input("Supabase Key", type="password")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

BUCKET_NAME = "exam_images"

# =============================
# HÀM XỬ LÝ FILE WORD
# =============================

def process_docx_file(uploaded_file):
    doc = docx.Document(uploaded_file)

    questions = []
    current_q = None
    temp_opts = []
    current_img_blob = None

    regex_question = re.compile(r'^(Câu\s+\d+[\.:])(.*)', re.IGNORECASE)
    regex_option = re.compile(r'^([A-D][\.:])(.*)')

    for para in doc.paragraphs:
        text = para.text.strip()

        # Quét ảnh
        for run in para.runs:
            if 'graphic' in run._element.xml:
                blips = run._element.findall(
                    './/{http://schemas.openxmlformats.org/drawingml/2006/main}blip'
                )
                for blip in blips:
                    rId = blip.get(
                        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
                    )
                    if rId:
                        current_img_blob = doc.part.related_parts[rId].blob

        if not text:
            continue

        match_q = regex_question.match(text)

        if match_q:
            if current_q:
                current_q['options'] = temp_opts
                current_q['type'] = 'essay' if len(temp_opts) == 0 else 'mcq'
                questions.append(current_q)

            q_num = int(re.search(r'\d+', match_q.group(1)).group())
            q_content = match_q.group(2).strip()

            current_q = {
                "id": q_num,
                "q": q_content,
                "options": [],
                "type": "mcq",
                "correct": "",
                "essay_answer": "",
                "image_blob": current_img_blob
            }

            current_img_blob = None
            temp_opts = []

        elif regex_option.match(text):
            temp_opts.append(text)

    if current_q:
        current_q['options'] = temp_opts
        current_q['type'] = 'essay' if len(temp_opts) == 0 else 'mcq'
        questions.append(current_q)

    return questions


# =============================
# GIAO DIỆN
# =============================

st.title("🤖 Admin: Quét Đề (Trắc nghiệm + Tự luận)")

uploaded_file = st.file_uploader("Chọn file Word (.docx)")

if "questions" not in st.session_state:
    st.session_state.questions = []

if uploaded_file and st.button("Phân tích File"):
    st.session_state.questions = process_docx_file(uploaded_file)

# =============================
# HIỂN THỊ CÂU HỎI
# =============================

if st.session_state.questions:

    data = st.session_state.questions

    mcq_count = sum(1 for q in data if q['type'] == 'mcq')
    essay_count = sum(1 for q in data if q['type'] == 'essay')

    st.success(f"Tìm thấy: {mcq_count} câu Trắc nghiệm & {essay_count} câu Tự luận.")

    with st.form("save_form"):

        for item in data:

            col_img, col_content = st.columns([1, 4])

            with col_img:
                if item['image_blob']:
                    st.image(item['image_blob'], width=120)
                else:
                    st.caption("Không ảnh")

            with col_content:

                if item['type'] == 'mcq':
                    st.markdown(f"🔵 **Câu {item['id']} (Trắc nghiệm):** {item['q']}")
                    st.caption(f"Options: {item['options']}")

                    item['correct'] = st.selectbox(
                        f"Đáp án đúng câu {item['id']}",
                        ["A", "B", "C", "D"],
                        key=f"ans_{item['id']}"
                    )

                else:
                    st.markdown(f"🟠 **Câu {item['id']} (Tự luận):** {item['q']}")

                    item['essay_answer'] = st.text_area(
                        f"Gợi ý trả lời câu {item['id']}",
                        key=f"essay_{item['id']}"
                    )

            st.divider()

        submit = st.form_submit_button("🚀 LƯU TẤT CẢ VÀO DATABASE")

        if submit and supabase:

            progress_bar = st.progress(0)
            status = st.empty()

            supabase.table("exam_questions").delete().neq("id", 0).execute()

            for i, item in enumerate(data):

                status.text(f"Đang lưu câu {item['id']}...")

                image_url = None

                if item['image_blob']:
                    try:
                        file_name = f"q_{item['id']}_{int(time.time())}.png"

                        supabase.storage.from_(BUCKET_NAME).upload(
                            file_name,
                            item['image_blob'],
                            {"content-type": "image/png"}
                        )

                        image_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

                    except Exception as e:
                        st.error(f"Lỗi upload ảnh: {e}")

                if item['type'] == 'mcq':
                    payload = {
                        "id": item['id'],
                        "q": item['q'],
                        "options": item['options'],
                        "correct_char": item['correct'],
                        "image_url": image_url
                    }
                else:
                    payload = {
                        "id": item['id'],
                        "q": item['q'],
                        "answer": item['essay_answer'],
                        "image_url": image_url
                    }

                supabase.table("exam_questions").insert({
                    "type": item['type'],
                    "content": payload
                }).execute()

                progress_bar.progress((i + 1) / len(data))

            status.success("✅ Hoàn tất!")
            time.sleep(1)
            st.rerun()
