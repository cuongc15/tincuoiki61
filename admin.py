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

# --- HÀM XỬ LÝ WORD & ẢNH ---
def process_docx_file(uploaded_file):
    doc = docx.Document(uploaded_file)
    
    questions = []
    current_q = None
    
    # Regex để tìm câu hỏi (VD: Câu 1., Câu 1:, Câu 01.)
    # và Đáp án (A., B., C., D.)
    regex_question = re.compile(r'^(Câu\s+\d+[\.:])(.*)', re.IGNORECASE)
    regex_option = re.compile(r'^([A-D][\.:])(.*)')
    
    # Biến tạm
    temp_opts = []
    current_img_blob = None # Lưu dữ liệu ảnh nhị phân
    
    # Duyệt qua từng đoạn văn (paragraph) trong Word
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # 1. Kiểm tra xem đoạn này có chứa ảnh không
        # Duyệt qua các "runs" (thành phần con của đoạn)
        for run in para.runs:
            # Tìm thẻ xml hình ảnh trong run
            if 'graphic' in run._element.xml:
                # Tìm rId (Relationship ID) của ảnh
                # Đây là kỹ thuật "đào" vào XML của Word
                blips = run._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                for blip in blips:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if rId:
                        # Lấy dữ liệu ảnh từ rId
                        image_part = doc.part.related_parts[rId]
                        current_img_blob = image_part.blob
                        # Gán ảnh này cho câu hỏi hiện tại (nếu đang xử lý dở)
                        if current_q:
                            current_q['image_blob'] = current_img_blob
        
        # 2. Phân tích văn bản
        if not text:
            continue
            
        # Nếu dòng bắt đầu bằng "Câu X..."
        match_q = regex_question.match(text)
        if match_q:
            # Lưu câu hỏi trước đó lại (nếu có)
            if current_q:
                current_q['options'] = temp_opts
                questions.append(current_q)
            
            # Tạo câu hỏi mới
            q_num_str = re.search(r'\d+', match_q.group(1)).group()
            q_content = match_q.group(2).strip()
            
            current_q = {
                "id": int(q_num_str),
                "q": q_content,
                "options": [],
                "correct_char": "?", # Sẽ tìm sau hoặc nhập tay
                "image_blob": None   # Chờ ảnh (nếu có)
            }
            temp_opts = [] # Reset đáp án
            
            # Nếu vừa tìm thấy ảnh ở dòng trên hoặc ngay dòng này, gán luôn
            if current_img_blob:
                current_q['image_blob'] = current_img_blob
                current_img_blob = None # Reset ảnh sau khi đã gán
            
        # Nếu dòng bắt đầu bằng "A.", "B."...
        elif regex_option.match(text):
            temp_opts.append(text)
            
    # Lưu câu cuối cùng
    if current_q:
        current_q['options'] = temp_opts
        questions.append(current_q)
        
    return questions

# --- GIAO DIỆN ADMIN ---
st.title("🤖 Admin: Tự động quét Ảnh & Câu hỏi")

uploaded_file = st.file_uploader("Chọn file Word (.docx)", type=['docx'])

if uploaded_file:
    if st.button("Phân tích File"):
        with st.spinner("Đang đọc file và tách ảnh..."):
            extracted_data = process_docx_file(uploaded_file)
            st.session_state['data_ready'] = extracted_data
            st.success(f"Đã tìm thấy {len(extracted_data)} câu hỏi.")

if 'data_ready' in st.session_state:
    data = st.session_state['data_ready']
    
    with st.form("confirm_form"):
        st.subheader("Kiểm tra dữ liệu")
        
        # Hiển thị danh sách để giáo viên check
        for item in data:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**Câu {item['id']}**")
                # Nếu có ảnh (dạng blob), hiển thị ra để check
                if item['image_blob']:
                    st.image(item['image_blob'], width=100, caption="Ảnh tìm thấy")
                else:
                    st.caption("Không có ảnh")
            with col2:
                # Cho phép sửa nội dung nếu parser đọc sai
                new_q = st.text_input(f"Nội dung câu {item['id']}", item['q'])
                item['q'] = new_q
                
                # Cho phép chọn đáp án đúng
                item['correct_char'] = st.selectbox(f"Đáp án đúng câu {item['id']}", ["A", "B", "C", "D"], key=f"ans_{item['id']}")
            
            st.divider()
            
        if st.form_submit_button("LƯU TẤT CẢ VÀO DATABASE"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Xóa dữ liệu cũ (Tùy chọn)
            # supabase.table("exam_questions").delete().neq("id", 0).execute()
            
            for i, item in enumerate(data):
                status_text.text(f"Đang xử lý câu {item['id']}...")
                
                image_url = None
                
                # 1. Nếu có ảnh, Upload lên Supabase Storage
                if item['image_blob']:
                    try:
                        file_name = f"auto_q_{item['id']}_{int(time.time())}.png"
                        supabase.storage.from_(BUCKET_NAME).upload(
                            path=file_name,
                            file=item['image_blob'],
                            file_options={"content-type": "image/png"}
                        )
                        # Lấy Public URL
                        image_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
                    except Exception as e:
                        st.error(f"Lỗi upload ảnh câu {item['id']}: {e}")

                # 2. Lưu vào Database
                payload = {
                    "id": item['id'],
                    "q": item['q'],
                    "options": item['options'],
                    "correct_char": item['correct_char'],
                    "image_url": image_url # Link ảnh từ Supabase
                }
                
                supabase.table("exam_questions").insert({
                    "type": "mcq", 
                    "content": payload
                }).execute()
                
                progress_bar.progress((i + 1) / len(data))
                
            status_text.success("✅ Hoàn tất! Đã lưu toàn bộ câu hỏi và ảnh.")
            time.sleep(2)
            del st.session_state['data_ready']
            st.rerun()
