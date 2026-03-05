import streamlit as st
import re
import time
from supabase import create_client
import docx
from PyPDF2 import PdfReader

# --- CẤU HÌNH SUPABASE ---
# (Lấy từ st.secrets hoặc điền trực tiếp để chạy trên máy)
try:
    SUPABASE_URL = st.secrets["https://coljvrkxzihtsalsabhw.supabase.co"]
    SUPABASE_KEY = st.secrets["sb_publishable_13zNj8XyMESPmm-TUYvSng_Ov_Gi4z6"]
except:
    st.warning("Chưa cấu hình Secrets. Vui lòng nhập thông tin bên dưới.")
    SUPABASE_URL = st.text_input("Supabase URL")
    SUPABASE_KEY = st.text_input("Supabase Key", type="password")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "exam_images" # Tên bucket bạn đã tạo trong Supabase Storage

# --- HÀM XỬ LÝ WORD ---
def process_docx_file(uploaded_file):
    doc = docx.Document(uploaded_file)
    
    questions = []
    current_q = None
    
    # Regex nhận diện
    regex_question = re.compile(r'^(Câu\s+\d+[\.:])(.*)', re.IGNORECASE)
    regex_option = re.compile(r'^([A-D][\.:])(.*)')
    
    temp_opts = []
    current_img_blob = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # 1. Quét ảnh trong đoạn văn
        for run in para.runs:
            if 'graphic' in run._element.xml:
                blips = run._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                for blip in blips:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if rId:
                        current_img_blob = doc.part.related_parts[rId].blob
                        # Gán ngay nếu đang trong câu hỏi
                        if current_q: 
                            current_q['image_blob'] = current_img_blob
                            current_img_blob = None # Reset sau khi gán
        
        # 2. Phân tích văn bản
        if not text: continue
            
        match_q = regex_question.match(text)
        
        # Phát hiện câu hỏi mới (VD: Câu 30...)
        if match_q:
            # Lưu câu cũ lại trước khi sang câu mới
            if current_q:
                current_q['options'] = temp_opts
                # LOGIC QUAN TRỌNG: Nếu không tìm thấy options nào -> Đánh dấu là TỰ LUẬN
                if len(temp_opts) == 0:
                    current_q['type'] = 'essay'
                else:
                    current_q['type'] = 'mcq'
                questions.append(current_q)
            
            # Khởi tạo câu mới
            q_num_str = re.search(r'\d+', match_q.group(1)).group()
            q_content = match_q.group(2).strip()
            
            current_q = {
                "id": int(q_num_str),
                "q": q_content,
                "options": [],
                "type": "mcq", # Mặc định là mcq, sẽ đổi thành essay nếu ko thấy A/B/C/D
                "correct": "",
                "essay_answer": "", # Chỗ để điền đáp án tự luận
                "image_blob": None
            }
            temp_opts = []
            
            if current_img_blob:
                current_q['image_blob'] = current_img_blob
                current_img_blob = None
            
        # Phát hiện đáp án A. B. C. D.
        elif regex_option.match(text):
            temp_opts.append(text)
            
    # Lưu câu cuối cùng
    if current_q:
        current_q['options'] = temp_opts
        if len(temp_opts) == 0:
            current_q['type'] = 'essay'
        else:
            current_q['type'] = 'mcq'
        questions.append(current_q)
        
    return questions

# --- GIAO DIỆN ---
st.title("🤖 Admin: Quét Đề (Trắc nghiệm + Tự luận)")

uploaded_file = st.file_uploader("Chọn file Word (.docx)", type=['docx'])

if uploaded_file:
    if st.button("Phân tích File"):
        with st.spinner("Đang tách câu hỏi và ảnh..."):
            extracted_data = process_docx_file(uploaded_file)
            st.session_state['data_ready'] = extracted_data
            
            # Đếm số lượng
            mcq_count = sum(1 for q in extracted_data if q['type'] == 'mcq')
            essay_count = sum(1 for q in extracted_data if q['type'] == 'essay')
            st.success(f"Tìm thấy: {mcq_count} câu Trắc nghiệm & {essay_count} câu Tự luận.")

if 'data_ready' in st.session_state:
    data = st.session_state['data_ready']
    
    with st.form("confirm_form"):
        st.subheader("Kiểm tra & Nhập đáp án")
        
        for item in data:
            col_img, col_content = st.columns([1, 4])
            
            # Cột trái: Ảnh (nếu có)
            with col_img:
                if item['image_blob']:
                    st.image(item['image_blob'], caption="Hình minh họa", width=120)
                else:
                    st.caption("Không ảnh")

            # Cột phải: Nội dung
            with col_content:
                # Phân biệt giao diện dựa trên loại câu hỏi
                if item['type'] == 'mcq':
                    st.markdown(f"🔵 **Câu {item['id']} (Trắc nghiệm):** {item['q']}")
                    st.caption(f"Options: {item['options']}")
                    # Chọn đáp án đúng cho MCQ
                    item['correct'] = st.selectbox(f"Đáp án đúng câu {item['id']}", ["A", "B", "C", "D"], key=f"ans_{item['id']}")
                else:
                    st.markdown(f"🟠 **Câu {item['id']} (Tự luận):** {item['q']}")
                    # Nhập gợi ý trả lời cho Tự luận
                    item['essay_answer'] = st.text_area(f"Gợi ý trả lời câu {item['id']}", placeholder="Nhập đáp án tự luận vào đây...", key=f"essay_{item['id']}")
            
            st.divider()
            
        if st.form_submit_button("🚀 LƯU TẤT CẢ VÀO DATABASE"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Xóa dữ liệu cũ (Reset đề)
            supabase.table("exam_questions").delete().neq("id", 0).execute()
            
            for i, item in enumerate(data):
                status_text.text(f"Đang lưu câu {item['id']}...")
                
                image_url = None
                
                # 1. Upload ảnh (nếu có)
                if item['image_blob']:
                    try:
                        file_name = f"q_{item['id']}_{int(time.time())}.png"
                        supabase.storage.from_(BUCKET_NAME).upload(
                            path=file_name,
                            file=item['image_blob'],
                            file_options={"content-type": "image/png"}
                        )
                        image_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
                    except Exception as e:
                        st.error(f"Lỗi ảnh câu {item['id']}: {e}")

                # 2. Chuẩn bị dữ liệu JSON
                if item['type'] == 'mcq':
                    payload = {
                        "id": item['id'],
                        "q": item['q'],
                        "options": item['options'],
                        "correct_char": item['correct'],
                        "image_url": image_url
                    }
                else: # essay
                    payload = {
                        "id": item['id'],
                        "q": item['q'],
                        "image_url": image_url,
                        "answer": item['essay_answer'] # Lưu gợi ý trả lời
                    }
                
                # 3. Insert vào DB
                supabase.table("exam_questions").insert({
                    "type": item['type'], 
                    "content": payload
                }).execute()
                
                progress_bar.progress((i + 1) / len(data))
                
            status_text.success("✅ Hoàn tất! Đã lưu cả Trắc nghiệm và Tự luận.")
            time.sleep(2)
            del st.session_state['data_ready']
            st.rerun()
