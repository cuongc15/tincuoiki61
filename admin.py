import streamlit as st
import docx
import re
import time
from supabase import create_client

# --- CẤU HÌNH ---
st.set_page_config(page_title="Admin Quản lý đề", layout="wide")

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    st.warning("Chưa cấu hình Secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "exam_images"

# --- HÀM XỬ LÝ WORD THÔNG MINH ---
def process_docx_file(uploaded_file):
    doc = docx.Document(uploaded_file)
    
    questions = []          # Danh sách chứa các câu hỏi
    questions_map = {}      # Map để tra cứu nhanh: id -> index trong list questions
    
    current_processing_q_id = None # Đang xử lý câu hỏi số mấy
    current_answer_id = None       # Đang xử lý ĐÁP ÁN của câu số mấy
    
    # Regex nhận diện
    # Tìm "Câu 1.", "Câu 1:", "Câu 01."
    regex_question = re.compile(r'^(Câu\s+(\d+)[\.:])(.*)', re.IGNORECASE)
    # Tìm đáp án trắc nghiệm "A.", "B."...
    regex_option = re.compile(r'^([A-D][\.:])(.*)')
    
    temp_opts = []
    current_img_blob = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # 1. QUÉT ẢNH (Logic cũ)
        for run in para.runs:
            if 'graphic' in run._element.xml:
                blips = run._element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                for blip in blips:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if rId:
                        current_img_blob = doc.part.related_parts[rId].blob
                        # Nếu đang đọc câu hỏi thì gán ảnh vào câu hỏi
                        if current_processing_q_id is not None and current_processing_q_id in questions_map:
                            idx = questions_map[current_processing_q_id]
                            questions[idx]['image_blob'] = current_img_blob
                            current_img_blob = None 
        
        # 2. PHÂN TÍCH VĂN BẢN
        if not text: continue
            
        match_q = regex_question.match(text)
        
        # --- TRƯỜNG HỢP 1: PHÁT HIỆN DÒNG "CÂU X..." ---
        if match_q:
            q_num = int(match_q.group(2)) # Lấy số thứ tự (VD: 30)
            content_after_label = match_q.group(3).strip() # Nội dung sau chữ "Câu 30."
            
            # KIỂM TRA: Câu này đã tồn tại chưa?
            if q_num in questions_map:
                # ==> ĐÃ TỒN TẠI -> Đây là phần ĐÁP ÁN GỢI Ý (nằm ở cuối file)
                current_answer_id = q_num
                current_processing_q_id = None # Ngắt trạng thái đọc câu hỏi
                
                # Ghi dòng đầu tiên của đáp án vào
                idx = questions_map[q_num]
                if content_after_label:
                    questions[idx]['essay_answer'] += content_after_label + "\n"
                
            else:
                # ==> CHƯA TỒN TẠI -> Đây là CÂU HỎI MỚI (nằm ở đầu file)
                
                # (Chốt sổ câu hỏi trước đó nếu có)
                if current_processing_q_id is not None:
                    idx = questions_map[current_processing_q_id]
                    questions[idx]['options'] = temp_opts
                    if len(temp_opts) == 0:
                         questions[idx]['type'] = 'essay'
                    else:
                         questions[idx]['type'] = 'mcq'
                
                # Tạo câu hỏi mới
                new_q = {
                    "id": q_num,
                    "q": content_after_label,
                    "options": [],
                    "type": "mcq", # Tạm để mcq, lát check options sẽ đổi sau
                    "correct": "A",
                    "essay_answer": "", # Chỗ này sẽ được điền khi gặp lại ID này ở cuối file
                    "image_blob": None
                }
                
                if current_img_blob: # Gán ảnh nếu ảnh nằm ngay dòng tiêu đề
                    new_q['image_blob'] = current_img_blob
                    current_img_blob = None

                questions.append(new_q)
                questions_map[q_num] = len(questions) - 1 # Lưu vị trí để tìm lại
                
                current_processing_q_id = q_num
                current_answer_id = None # Ngắt trạng thái đọc đáp án
                temp_opts = []

        # --- TRƯỜNG HỢP 2: ĐANG ĐỌC ĐÁP ÁN TRẮC NGHIỆM (A. B. C. D.) ---
        elif regex_option.match(text) and current_processing_q_id is not None:
            temp_opts.append(text)
            
        # --- TRƯỜNG HỢP 3: NỘI DUNG TIẾP THEO ---
        else:
            # Nếu đang ở chế độ đọc ĐÁP ÁN TỰ LUẬN (cuối file)
            if current_answer_id is not None:
                idx = questions_map[current_answer_id]
                # Cộng dồn các dòng tiếp theo vào đáp án
                questions[idx]['essay_answer'] += text + "\n"
            
            # Nếu đang ở chế độ đọc CÂU HỎI TỰ LUẬN (đầu file)
            elif current_processing_q_id is not None:
                 # Có thể là nội dung dài của câu hỏi
                 pass 

    # Chốt sổ câu cuối cùng của phần đề bài
    if current_processing_q_id is not None:
        idx = questions_map[current_processing_q_id]
        questions[idx]['options'] = temp_opts
        if len(temp_opts) == 0:
            questions[idx]['type'] = 'essay'
        else:
            questions[idx]['type'] = 'mcq'
            
    return questions

# --- GIAO DIỆN ADMIN ---
st.title("🤖 Admin: Quét Đề & Tự động lấy Đáp án")
st.info("Hệ thống sẽ tự động quét phần đáp án gợi ý ở cuối file Word để điền vào ô Tự luận.")

uploaded_file = st.file_uploader("Chọn file Word (.docx)", type=['docx'])

# Reset logic
if 'last_file' not in st.session_state or st.session_state['last_file'] != uploaded_file:
    if 'data_ready' in st.session_state:
        del st.session_state['data_ready']
    st.session_state['last_file'] = uploaded_file

if uploaded_file:
    if st.button("Phân tích File"):
        with st.spinner("Đang đọc câu hỏi và tách đáp án gợi ý..."):
            extracted_data = process_docx_file(uploaded_file)
            st.session_state['data_ready'] = extracted_data
            
            mcq_count = sum(1 for q in extracted_data if q['type'] == 'mcq')
            essay_count = sum(1 for q in extracted_data if q['type'] == 'essay')
            # Đếm số câu tự luận đã tự tìm được đáp án
            auto_ans_count = sum(1 for q in extracted_data if q['type'] == 'essay' and q['essay_answer'].strip() != "")
            
            st.success(f"Tìm thấy: {mcq_count} Trắc nghiệm & {essay_count} Tự luận.")
            if auto_ans_count > 0:
                st.info(f"✨ Đã tự động điền đáp án gợi ý cho {auto_ans_count} câu tự luận!")

if 'data_ready' in st.session_state:
    data = st.session_state['data_ready']
    
    with st.form("confirm_form"):
        st.subheader("Kiểm tra nội dung")
        
        for i, item in enumerate(data):
            col_img, col_content = st.columns([1, 4])
            
            with col_img:
                if item['image_blob']:
                    st.image(item['image_blob'], width=100)
                else:
                    st.caption("No Image")

            with col_content:
                if item['type'] == 'mcq':
                    st.markdown(f"🔵 **Câu {item['id']} (Trắc nghiệm):** {item['q']}")
                    st.caption(f"Options: {item['options']}")
                    item['correct'] = st.selectbox(
                        f"Đáp án đúng câu {item['id']}", ["A", "B", "C", "D"], key=f"ans_{i}_{item['id']}"
                    )
                else:
                    st.markdown(f"🟠 **Câu {item['id']} (Tự luận):** {item['q']}")
                    # Ô này sẽ tự động có chữ nhờ code xử lý ở trên
                    item['essay_answer'] = st.text_area(
                        f"Gợi ý trả lời (Đã tự động điền)", 
                        value=item.get('essay_answer', '').strip(),
                        height=100,
                        key=f"essay_{i}_{item['id']}"
                    )
            st.divider()
            
        if st.form_submit_button("🚀 LƯU VÀO DATABASE"):
            progress_bar = st.progress(0)
            
            # Xóa dữ liệu cũ (Khuyến nghị bật dòng này)
            try:
                supabase.table("exam_questions").delete().neq("id", 0).execute()
            except:
                pass
            
            for i, item in enumerate(data):
                image_url = None
                if item['image_blob']:
                    try:
                        file_name = f"auto_{item['id']}_{int(time.time())}.png"
                        supabase.storage.from_(BUCKET_NAME).upload(
                            path=file_name, file=item['image_blob'], file_options={"content-type": "image/png"}
                        )
                        image_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
                    except: pass

                if item['type'] == 'mcq':
                    payload = {"id": item['id'], "q": item['q'], "options": item['options'], "correct_char": item['correct'], "image_url": image_url}
                else: 
                    payload = {"id": item['id'], "q": item['q'], "image_url": image_url, "answer": item['essay_answer']} # Lưu đáp án tự luận
                
                supabase.table("exam_questions").insert({"type": item['type'], "content": payload}).execute()
                progress_bar.progress((i + 1) / len(data))
                
            st.success("✅ Đã lưu xong!")
            time.sleep(1)
            del st.session_state['data_ready']
            st.rerun()
