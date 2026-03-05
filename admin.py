import streamlit as st
import re
from supabase import create_client
from supabase import create_client
from dotenv import load_dotenv
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

if not SUPABASE_URL or not SUPABASE_KEY:
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- HÀM ĐỌC FILE ---
def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# --- HÀM PHÂN TÍCH ĐỀ THI (PARSER) ---
def parse_exam_content(text):
    """
    Hàm này cực kỳ quan trọng:
    Nó dùng Regular Expression (Regex) để tìm 'Câu 1.', 'A.', 'B.' và bảng đáp án.
    """
    questions_mcq = []
    
    # 1. Tìm bảng đáp án (Thường nằm cuối, dạng: 1. A 2. B ...)
    # Logic: Tìm chuỗi có dạng "1. [A-D]" lặp lại
    answer_key = {}
    # Tìm tất cả các mẫu "Số. Chữ cái" (VD: 1. A, 2. D)
    key_matches = re.findall(r'(\d+)\s*[\.:]\s*([A-D])', text)
    if key_matches:
        for num, ans in key_matches:
            answer_key[int(num)] = ans

    # 2. Tách các câu hỏi Trắc nghiệm
    # Regex tìm: "Câu [số]." theo sau là nội dung, đến khi gặp "Câu [số tiếp]"
    # Pattern giải thích: 
    # Câu \d+[\.:] : Bắt đầu bằng chữ Câu + số + dấu chấm hoặc 2 chấm
    # (.*?) : Lấy nội dung ở giữa (non-greedy)
    # (?=Câu \d+[\.:]|$|II\.) : Dừng lại khi gặp Câu tiếp theo HOẶC hết bài HOẶC gặp phần II. Tự luận
    
    # Chuẩn hóa văn bản một chút để dễ xử lý (xóa dòng trống thừa)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_text = '\n'.join(lines)

    # Tách khối trắc nghiệm (Thường từ đầu hoặc sau chứ I. TRẮC NGHIỆM)
    mcq_section = clean_text
    if "II. TỰ LUẬN" in clean_text:
        mcq_section = clean_text.split("II. TỰ LUẬN")[0]
    
    # Tìm các câu hỏi
    raw_questions = re.split(r'(Câu\s+\d+[\.:])', mcq_section)
    
    current_q = {}
    
    # raw_questions sẽ có dạng ['', 'Câu 1.', 'Nội dung...', 'Câu 2.', 'Nội dung...']
    for i in range(1, len(raw_questions), 2):
        q_label = raw_questions[i].strip() # VD: Câu 1.
        q_content_full = raw_questions[i+1].strip() # Nội dung câu hỏi và đáp án
        
        # Lấy số câu
        q_num = int(re.search(r'\d+', q_label).group())
        
        # Tách nội dung câu hỏi và các đáp án A, B, C, D
        # Tìm vị trí của A. B. C. D.
        # Lưu ý: Regex này giả định đáp án có dạng "A. " (A chấm cách)
        opts_matches = re.split(r'([A-D][\.:])', q_content_full)
        
        if len(opts_matches) >= 9: # Phải có ít nhất Question + 4 labels + 4 contents
            q_text = opts_matches[0].strip()
            options = []
            # opts_matches[1] là "A.", opts_matches[2] là nội dung A...
            options.append(opts_matches[1] + " " + opts_matches[2].strip())
            options.append(opts_matches[3] + " " + opts_matches[4].strip())
            options.append(opts_matches[5] + " " + opts_matches[6].strip())
            options.append(opts_matches[7] + " " + opts_matches[8].strip())
            
            # Lấy đáp án đúng từ bảng đáp án đã quét ở trên
            correct_char = answer_key.get(q_num, "?") # Mặc định ? nếu không tìm thấy
            
            questions_mcq.append({
                "id": q_num,
                "q": q_text,
                "options": options,
                "correct_char": correct_char
            })

    return questions_mcq, answer_key

# --- GIAO DIỆN ADMIN ---
st.title("🛠️ Admin: Nạp đề thi từ File")
st.warning("Trang này chỉ dành cho giáo viên.")

uploaded_file = st.file_uploader("Chọn file đề thi (.docx hoặc .pdf)", type=['docx', 'pdf'])

if uploaded_file:
    # 1. Đọc text
    raw_text = extract_text_from_file(uploaded_file)
    
    with st.expander("Xem nội dung thô trích xuất được"):
        st.text(raw_text)

    # 2. Phân tích
    if st.button("Phân tích đề thi"):
        mcq_list, detected_keys = parse_exam_content(raw_text)
        
        st.success(f"Đã tìm thấy {len(mcq_list)} câu trắc nghiệm.")
        st.info(f"Đã quét được đáp án: {detected_keys}")
        
        # Lưu tạm vào session để review trước khi up
        st.session_state['preview_data'] = mcq_list

if 'preview_data' in st.session_state:
    st.subheader("Kiểm tra dữ liệu trước khi lưu")
    
    # Hiển thị dạng bảng để check
    for item in st.session_state['preview_data']:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**Câu {item['id']}:** {item['q']}")
            st.caption(f"Options: {item['options']}")
        with col2:
            st.write(f"Đ.Án: **{item['correct_char']}**")
            
    # Nút lưu
    if st.button("LƯU VÀO SUPABASE 🚀"):
        # Xóa dữ liệu cũ (Tùy chọn)
        supabase.table("exam_questions").delete().neq("id", 0).execute()
        
        # Chuẩn bị data
        data_to_insert = []
        for item in st.session_state['preview_data']:
            # Chuyển đổi sang format JSON của bảng
            payload = {
                "id": item['id'],
                "q": item['q'],
                "options": item['options'],
                "correct_char": item['correct_char']
            }
            data_to_insert.append({"type": "mcq", "content": payload})
            
        # Insert
        try:
            supabase.table("exam_questions").insert(data_to_insert).execute()
            st.success("Đã nạp dữ liệu thành công! Hãy mở App thi để kiểm tra.")
            del st.session_state['preview_data'] # Xóa cache
        except Exception as e:
            st.error(f"Lỗi khi lưu: {e}")
