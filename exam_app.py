import streamlit as st
import random

# --- 1. DỮ LIỆU GỐC (HARD-CODE) ---
RAW_EXAM_DATA = {
    "title": "ĐỀ KIỂM TRA GIỮA HỌC KỲ I - TIN HỌC LỚP 6",
    "year": "2025 – 2026",
    "duration": "45 phút",
    "questions_mcq": [
        {"id": 1, "q": "Phương án nào sau đây nêu đúng khái niệm về dữ liệu?", "options": ["A. Là những gì đem lại hiểu biết cho con người.", "B. Là thông tin được ghi lên vật mang tin.", "C. Là kết quả của việc xử lí thông tin.", "D. Là vật chứa đựng thông tin."], "correct_char": "B"},
        {"id": 2, "q": "Trong hoạt động xử lí thông tin của con người, hoạt động nào sau đây thuộc về bước thu nhận thông tin?", "options": ["A. Phân tích, tổng hợp.", "B. Suy luận, phán đoán.", "C. Nghe bản tin dự báo thời tiết.", "D. Rút ra quyết định."], "correct_char": "C"},
        {"id": 3, "q": "Bộ phận nào của máy tính có nhiệm vụ tiếp nhận thông tin từ bên ngoài?", "options": ["A. Thiết bị vào.", "B. Bộ xử lí.", "C. Bộ nhớ.", "D. Thiết bị ra."], "correct_char": "A"},
        {"id": 4, "q": "Đơn vị nào sau đây là lớn nhất trong các đơn vị đo dung lượng thông tin cơ bản?", "options": ["A. Kilobyte (KB).", "B. Megabyte (MB).", "C. Gigabyte (GB).", "D. Terabyte (TB)."], "correct_char": "D"},
        {"id": 5, "q": "Khi ta nghe bản tin dự báo thời tiết 'Ngày mai trời nắng, nhiệt độ 30°C', thông tin này có vai trò gì?", "options": ["A. Giúp con người thu thập dữ liệu.", "B. Giúp con người đưa ra những lựa chọn.", "C. Giúp con người lưu trữ dữ liệu.", "D. Giúp con người truyền thông tin."], "correct_char": "B"},
        {"id": 6, "q": "Để biểu diễn thông tin thành dãy bit (chuỗi các kí hiệu 0 và 1), máy tính sử dụng phương pháp nào?", "options": ["A. Số thập phân.", "B. Dữ liệu thô.", "C. Biểu diễn bằng các bảng mã.", "D. Biểu diễn bằng các vật mang tin."], "correct_char": "C"},
        {"id": 7, "q": "Phát biểu nào sau đây nêu đúng về lợi ích cơ bản của mạng máy tính?", "options": ["A. Giảm chi phí khi dùng chung các thiết bị phần cứng.", "B. Đảm bảo dữ liệu của mỗi người dùng không bị chia sẻ.", "C. Chỉ phục vụ cho việc trao đổi thông tin giữa các máy tính.", "D. Giúp người dùng có thể làm việc liên tục suốt ngày đêm."], "correct_char": "A"},
        {"id": 8, "q": "Phát biểu nào sau đây là sai về các thành phần chính của mạng máy tính?", "options": ["A. Gồm thiết bị đầu cuối và thiết bị kết nối.", "B. Gồm phần mềm mạng để điều khiển quá trình truyền dữ liệu.", "C. Gồm các thiết bị kết nối như Bộ chuyển mạch (Switch) hoặc Bộ định tuyến (Router).", "D. Gồm máy tính và phần mềm mạng."], "correct_char": "D"}
    ],
    "questions_tf": [
        {
            "main_q": "Câu hỏi Đúng/Sai 1: Về việc ghi chép trong buổi họp lớp...",
            "sub_qs": [
                {"id": "1a", "text": "Các ý kiến đóng góp của thành viên lớp trên sổ tay là Dữ liệu.", "correct": "Đúng"},
                {"id": "1b", "text": "Việc tổ trưởng ghi chép các ý kiến đóng góp thuộc hoạt động Thu nhận thông tin.", "correct": "Đúng"},
                {"id": "1c", "text": "Việc tổng hợp các ý kiến thành một bản kế hoạch hoàn chỉnh thuộc hoạt động Xử lí thông tin.", "correct": "Đúng"},
                {"id": "1d", "text": "Nếu tổ trưởng sử dụng máy tính để ghi chép và tổng hợp, hiệu quả công việc sẽ cao hơn khi dùng sổ tay.", "correct": "Đúng"}
            ]
        },
        {
            "main_q": "Câu hỏi Đúng/Sai 2: Về đơn vị đo dung lượng thông tin...",
            "sub_qs": [
                {"id": "2a", "text": "Bit là đơn vị đo dung lượng thông tin lớn nhất.", "correct": "Sai"},
                {"id": "2b", "text": "Thứ tự từ nhỏ đến lớn là Bit, Byte, Kilobyte, Megabyte, Gigabyte.", "correct": "Đúng"},
                {"id": "2c", "text": "Một tệp văn bản có dung lượng 1.024 Byte tương đương với 1 Kilobyte.", "correct": "Đúng"},
                {"id": "2d", "text": "Một bộ phim độ nét cao 4 GB có thể chứa trọn vẹn trên USB 4.000 MB.", "correct": "Sai"}
            ]
        }
    ],
    "essay_questions": [
        "Câu 1 (Tự luận): Nêu khái niệm và lợi ích của mạng máy tính?",
        "Câu 2 (Tự luận): Bài toán Dung lượng (An sao chép ảnh và video vào ổ cứng 2TB...)"
    ]
}

# --- 2. HÀM XỬ LÝ ĐẢO CÂU HỎI (CHẠY 1 LẦN) ---
def initialize_exam():
    """Hàm này chỉ chạy khi bắt đầu phiên làm việc để tạo đề ngẫu nhiên"""
    if 'exam_setup' not in st.session_state:
        # 1. Xử lý Trắc nghiệm (MCQ)
        shuffled_mcq = []
        original_mcq = RAW_EXAM_DATA["questions_mcq"][:] # Copy để không sửa dữ liệu gốc
        random.shuffle(original_mcq) # Đảo thứ tự câu hỏi

        for q in original_mcq:
            # Tìm nội dung đáp án đúng dựa trên ký tự gốc (A, B, C, D)
            # Ví dụ: correct_char là "B" thì lấy nội dung chuỗi bắt đầu bằng "B."
            correct_text_full = next((opt for opt in q["options"] if opt.startswith(q["correct_char"])), "")
            # Cắt bỏ tiền tố "A. ", "B. " để khi đảo không bị lộ
            clean_options = [opt[3:] for opt in q["options"]] 
            clean_correct_text = correct_text_full[3:]
            
            # Đảo vị trí các đáp án
            random.shuffle(clean_options)
            
            shuffled_mcq.append({
                "original_id": q["id"],
                "question": q["q"],
                "options": clean_options,
                "correct_text": clean_correct_text
            })

        # 2. Xử lý Đúng/Sai (TF)
        # Đảo thứ tự các ý nhỏ a,b,c,d bên trong
        shuffled_tf = []
        for group in RAW_EXAM_DATA["questions_tf"]:
            sub_list = group["sub_qs"][:]
            random.shuffle(sub_list)
            shuffled_tf.append({
                "main_q": group["main_q"],
                "sub_qs": sub_list
            })

        # Lưu vào session_state
        st.session_state['exam_setup'] = {
            "mcq": shuffled_mcq,
            "tf": shuffled_tf
        }

# Gọi hàm khởi tạo
initialize_exam()
exam_setup = st.session_state['exam_setup']

# --- 3. GIAO DIỆN ỨNG DỤNG ---
st.set_page_config(page_title="Kiểm tra Tin học 6", layout="wide")

with st.sidebar:
    st.header("⚙️ Cài đặt")
    pass_score = st.number_input("Điểm sàn xem đáp án", 0.0, 10.0, 5.0, step=0.5)
    if st.button("🔄 Tạo đề ngẫu nhiên mới"):
        del st.session_state['exam_setup']
        st.rerun()

st.title(f"📝 {RAW_EXAM_DATA['title']}")
st.caption("Lưu ý: Thứ tự câu hỏi và đáp án đã được đảo ngẫu nhiên.")
st.markdown("---")

with st.form("exam_form"):
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        student_name = st.text_input("Họ và tên học sinh:")
    with col_info2:
        student_class = st.text_input("Lớp:")
    
    # --- PHẦN I: TRẮC NGHIỆM KHÁCH QUAN ---
    # Tính toán thang điểm: Tổng 8 điểm.
    # Số lượng câu hỏi = 8 câu MCQ + 8 ý Đúng/Sai = 16 mục.
    # => Mỗi mục = 8 / 16 = 0.5 điểm.
    POINT_PER_ITEM = 0.5 
    
    st.header("I. TRẮC NGHIỆM (8.0 điểm)")
    st.info("Chọn đáp án đúng nhất hoặc xác định Đúng/Sai.")

    # A. MCQ
    st.subheader("Phần 1: Chọn đáp án đúng")
    user_answers_mcq = {}
    
    # Duyệt qua danh sách câu hỏi đã đảo
    for idx, q in enumerate(exam_setup["mcq"]):
        st.write(f"**Câu {idx + 1}:** {q['question']}")
        # Key của widget phải là duy nhất, dùng original_id
        user_answers_mcq[q['original_id']] = st.radio(
            f"Chọn đáp án câu {idx + 1}", 
            q['options'], 
            index=None, 
            key=f"mcq_rand_{q['original_id']}",
            label_visibility="collapsed"
        )
        st.write("")
        st.divider()

    # B. True/False
    st.subheader("Phần 2: Chọn Đúng hoặc Sai")
    user_answers_tf = {}
    
    for g_idx, group in enumerate(exam_setup["tf"]):
        st.write(f"**{group['main_q']}**")
        for s_idx, sub in enumerate(group["sub_qs"]):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"- {sub['text']}")
            with col2:
                # Key duy nhất
                user_answers_tf[sub['id']] = st.radio(
                    f"TF_{sub['id']}", 
                    ["Đúng", "Sai"], 
                    index=None, 
                    horizontal=True, 
                    key=f"tf_rand_{sub['id']}",
                    label_visibility="collapsed"
                )
        st.write("")
        st.divider()

    # --- PHẦN II: TỰ LUẬN ---
    st.header("II. TỰ LUẬN (2.0 điểm)")
    for eq in RAW_EXAM_DATA["essay_questions"]:
        st.write(f"**{eq}**")
        st.text_area("Bài làm:", height=100, key=f"essay_{eq[:5]}")

    submitted = st.form_submit_button("Nộp bài & Xem kết quả")

# --- 4. XỬ LÝ KẾT QUẢ ---
if submitted:
    if not student_name:
        st.error("⚠️ Vui lòng nhập tên của bạn!")
    else:
        total_score = 0.0
        max_mcq_score = 8.0
        
        # Chấm MCQ
        # Logic: So sánh chuỗi text người dùng chọn với chuỗi text đúng đã lưu
        correct_count = 0
        total_items = len(exam_setup["mcq"]) + sum(len(g["sub_qs"]) for g in exam_setup["tf"])
        
        # Tính lại điểm mỗi câu dựa trên tổng điểm 8
        point_per_q = 8.0 / total_items

        # Chấm MCQ
        for q in exam_setup["mcq"]:
            user_val = user_answers_mcq.get(q['original_id'])
            if user_val == q['correct_text']:
                total_score += point_per_q
                correct_count += 1
        
        # Chấm TF
        for group in exam_setup["tf"]:
            for sub in group["sub_qs"]:
                if user_answers_tf.get(sub["id"]) == sub["correct"]:
                    total_score += point_per_q
                    correct_count += 1
        
        # Làm tròn điểm
        total_score = round(total_score, 2)

        st.success(f"Chúc mừng **{student_name}** đã hoàn thành bài thi!")
        st.metric("ĐIỂM TRẮC NGHIỆM", f"{total_score} / 8.0")
        
        if total_score >= pass_score:
            st.balloons()
            with st.expander("🔍 XEM ĐÁP ÁN CHI TIẾT", expanded=True):
                st.subheader("Giải thích đáp án")
                
                # Hiển thị lại MCQ
                st.markdown("#### Phần 1: Trắc nghiệm")
                for idx, q in enumerate(exam_setup["mcq"]):
                    user_val = user_answers_mcq.get(q['original_id'], "Chưa làm")
                    is_right = (user_val == q['correct_text'])
                    emoji = "✅" if is_right else "❌"
                    
                    st.markdown(f"**Câu {idx+1}:** {q['question']}")
                    if is_right:
                        st.markdown(f"- Bạn chọn: :green[{user_val}] {emoji}")
                    else:
                        st.markdown(f"- Bạn chọn: :red[{user_val}]")
                        st.markdown(f"- Đáp án đúng: :green[{q['correct_text']}]")
                    st.divider()
                
                # Hiển thị lại TF
                st.markdown("#### Phần 2: Đúng/Sai")
                for group in exam_setup["tf"]:
                    st.write(f"_{group['main_q']}_")
                    for sub in group["sub_qs"]:
                        val = user_answers_tf.get(sub["id"], "Trống")
                        is_right = (val == sub["correct"])
                        color = "green" if is_right else "red"
                        st.markdown(f"- {sub['text']} -> Đáp án: **{sub['correct']}**. (Bạn chọn: :{color}[{val}])")
        else:
            st.warning(f"Bạn cần đạt ít nhất {pass_score} điểm trắc nghiệm để xem đáp án. Hãy cố gắng lần sau!")
