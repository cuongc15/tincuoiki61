import streamlit as st
import json

# --- CẤU HÌNH DỮ LIỆU ĐỀ THI (MÔ PHỎNG TỪ PDF CỦA BẠN) ---
# Trong thực tế, bạn có thể load phần này từ file .json hoặc .docx
exam_data = {
    "title": "ĐỀ KIỂM TRA GIỮA HỌC KỲ I - TIN HỌC LỚP 6",
    "year": "2025 – 2026",
    "duration": "45 phút",
    "questions_mcq": [ # Phần trắc nghiệm 1 lựa chọn
        {"id": 1, "q": "Phương án nào sau đây nêu đúng khái niệm về dữ liệu?", "options": ["A. Là những gì đem lại hiểu biết cho con người.", "B. Là thông tin được ghi lên vật mang tin.", "C. Là kết quả của việc xử lí thông tin.", "D. Là vật chứa đựng thông tin."], "correct": "B"},
        {"id": 2, "q": "Trong hoạt động xử lí thông tin của con người, hoạt động nào sau đây thuộc về bước thu nhận thông tin?", "options": ["A. Phân tích, tổng hợp.", "B. Suy luận, phán đoán.", "C. Nghe bản tin dự báo thời tiết.", "D. Rút ra quyết định."], "correct": "C"},
        {"id": 3, "q": "Bộ phận nào của máy tính có nhiệm vụ tiếp nhận thông tin từ bên ngoài?", "options": ["A. Thiết bị vào.", "B. Bộ xử lí.", "C. Bộ nhớ.", "D. Thiết bị ra."], "correct": "A"},
        {"id": 4, "q": "Đơn vị nào sau đây là lớn nhất trong các đơn vị đo dung lượng thông tin cơ bản?", "options": ["A. Kilobyte (KB).", "B. Megabyte (MB).", "C. Gigabyte (GB).", "D. Terabyte (TB)."], "correct": "D"},
        {"id": 5, "q": "Khi ta nghe bản tin dự báo thời tiết 'Ngày mai trời nắng, nhiệt độ 30°C', thông tin này có vai trò gì?", "options": ["A. Giúp con người thu thập dữ liệu.", "B. Giúp con người đưa ra những lựa chọn.", "C. Giúp con người lưu trữ dữ liệu.", "D. Giúp con người truyền thông tin."], "correct": "B"},
        {"id": 6, "q": "Để biểu diễn thông tin thành dãy bit (chuỗi các kí hiệu 0 và 1), máy tính sử dụng phương pháp nào?", "options": ["A. Số thập phân.", "B. Dữ liệu thô.", "C. Biểu diễn bằng các bảng mã.", "D. Biểu diễn bằng các vật mang tin."], "correct": "C"},
        {"id": 7, "q": "Phát biểu nào sau đây nêu đúng về lợi ích cơ bản của mạng máy tính?", "options": ["A. Giảm chi phí khi dùng chung các thiết bị phần cứng.", "B. Đảm bảo dữ liệu của mỗi người dùng không bị chia sẻ.", "C. Chỉ phục vụ cho việc trao đổi thông tin giữa các máy tính.", "D. Giúp người dùng có thể làm việc liên tục suốt ngày đêm."], "correct": "A"},
        {"id": 8, "q": "Phát biểu nào sau đây là sai về các thành phần chính của mạng máy tính?", "options": ["A. Gồm thiết bị đầu cuối và thiết bị kết nối.", "B. Gồm phần mềm mạng để điều khiển quá trình truyền dữ liệu.", "C. Gồm các thiết bị kết nối như Bộ chuyển mạch (Switch) hoặc Bộ định tuyến (Router).", "D. Gồm máy tính và phần mềm mạng."], "correct": "D"}
    ],
    "questions_tf": [ # Phần trắc nghiệm Đúng/Sai
        {
            "main_q": "Câu 1. Trong một buổi họp lớp, cô giáo yêu cầu tổ trưởng tổ 1 ghi chép lại toàn bộ ý kiến...",
            "sub_qs": [
                {"id": "1a", "text": "a) Các ý kiến đóng góp của thành viên lớp trên sổ tay là Dữ liệu.", "correct": "Đúng"},
                {"id": "1b", "text": "b) Việc tổ trưởng ghi chép các ý kiến đóng góp thuộc hoạt động Thu nhận thông tin.", "correct": "Đúng"},
                {"id": "1c", "text": "c) Việc tổng hợp các ý kiến thành một bản kế hoạch hoàn chỉnh thuộc hoạt động Xử lí thông tin.", "correct": "Đúng"},
                {"id": "1d", "text": "d) Nếu tổ trưởng sử dụng máy tính để ghi chép và tổng hợp, hiệu quả công việc sẽ cao hơn khi dùng sổ tay.", "correct": "Đúng"}
            ]
        },
        {
            "main_q": "Câu 2. Các đơn vị đo dung lượng thông tin là rất quan trọng...",
            "sub_qs": [
                {"id": "2a", "text": "a) Bit là đơn vị đo dung lượng thông tin lớn nhất.", "correct": "Sai"},
                {"id": "2b", "text": "b) Thứ tự các đơn vị đo dung lượng thông tin từ nhỏ đến lớn là Bit, Byte, Kilobyte, Megabyte, Gigabyte.", "correct": "Đúng"},
                {"id": "2c", "text": "c) Một tệp văn bản có dung lượng 1.024 Byte tương đương với 1 Kilobyte.", "correct": "Đúng"},
                {"id": "2d", "text": "d) Một bộ phim độ nét cao có dung lượng 4 GB có thể được chứa trọn vẹn trên một USB có dung lượng 4.000 MB.", "correct": "Sai"} # 4GB = 4096MB > 4000MB
            ]
        }
    ],
    "essay_questions": [
        "Câu 1 (2.0 điểm): Nêu khái niệm và lợi ích của mạng máy tính?",
        "Câu 2 (4.0 điểm): Bài toán Dung lượng (An sao chép ảnh và video vào ổ cứng 2TB...)"
    ]
}

# --- GIAO DIỆN ỨNG DỤNG ---

st.set_page_config(page_title="Kiểm tra Tin học 6", layout="wide")

# Sidebar: Cài đặt cho Giáo viên
with st.sidebar:
    st.header("⚙️ Dành cho Giáo viên")
    pass_score = st.number_input("Điểm tối thiểu để xem đáp án", min_value=0.0, max_value=10.0, value=5.0, step=0.5)
    st.info("Chỉ khi học sinh đạt trên điểm này, đáp án chi tiết mới hiện ra.")
    st.divider()
    st.write("Tải file đề thi (Tính năng mở rộng trong tương lai để đọc file .docx)")

# Header
st.title(f"📝 {exam_data['title']}")
st.subheader(f"Năm học: {exam_data['year']} | Thời gian: {exam_data['duration']}")
st.markdown("---")

# Form làm bài
with st.form("exam_form"):
    student_name = st.text_input("Họ và tên học sinh:")
    student_class = st.text_input("Lớp:")
    
    st.markdown("### I. TRẮC NGHIỆM (4.0 điểm)")
    
    # --- PHẦN A: NHIỀU LỰA CHỌN ---
    st.markdown("#### A. Chọn đáp án đúng nhất (Mỗi câu 0.25 điểm)")
    user_answers_mcq = {}
    for q in exam_data["questions_mcq"]:
        st.write(f"**Câu {q['id']}:** {q['q']}")
        # Dùng radio nhưng để index=None để chưa chọn gì
        user_answers_mcq[q['id']] = st.radio(f"Chọn đáp án câu {q['id']}:", q['options'], index=None, key=f"mcq_{q['id']}")
        st.write("")

    # --- PHẦN B: ĐÚNG / SAI ---
    st.markdown("#### B. Chọn Đúng hoặc Sai (Mỗi ý đúng 0.25 điểm)")
    user_answers_tf = {}
    
    for idx, group in enumerate(exam_data["questions_tf"]):
        st.write(f"**{group['main_q']}**")
        for sub in group["sub_qs"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(sub["text"])
            with col2:
                user_answers_tf[sub["id"]] = st.radio(f"Đ/S {sub['id']}", ["Đúng", "Sai"], index=None, horizontal=True, key=f"tf_{sub['id']}")
        st.write("")

    # --- PHẦN II: TỰ LUẬN ---
    st.markdown("### II. TỰ LUẬN (6.0 điểm)")
    st.info("Phần này hệ thống không chấm tự động. Hãy làm ra giấy hoặc nhập vào ô bên dưới để tự đối chiếu sau.")
    for eq in exam_data["essay_questions"]:
        st.text_area(eq, height=100)

    submitted = st.form_submit_button("Nộp bài & Xem kết quả")

# --- XỬ LÝ KẾT QUẢ ---
if submitted:
    if not student_name:
        st.error("Vui lòng nhập tên của bạn!")
    else:
        total_score = 0.0
        
        # Chấm phần MCQ
        correct_mcq_count = 0
        for q in exam_data["questions_mcq"]:
            user_ans = user_answers_mcq.get(q['id'])
            # Lấy ký tự đầu (A, B, C, D) để so sánh
            if user_ans and user_ans.startswith(q['correct']):
                total_score += 0.25
                correct_mcq_count += 1
        
        # Chấm phần TF
        correct_tf_count = 0
        for group in exam_data["questions_tf"]:
            for sub in group["sub_qs"]:
                if user_answers_tf.get(sub["id"]) == sub["correct"]:
                    total_score += 0.25
                    correct_tf_count += 1

        # Hiển thị điểm số (Chỉ tính điểm trắc nghiệm trong demo này vì Tự luận cần người chấm)
        # Tổng max trắc nghiệm trong đề là 4.0 điểm (8 câu MCQ + 2 câu TF x 4 ý)
        # Tuy nhiên, theo ma trận đề bài: 
        # MCQ: 8 câu = 2 điểm? (Theo đề: Mỗi câu 0.25 -> 8*0.25 = 2.0) -> ĐÚNG
        # TF: 2 câu lớn (8 ý nhỏ) -> Mỗi ý 0.25 -> 8*0.25 = 2.0 -> ĐÚNG
        # Tổng trắc nghiệm là 4.0.
        
        st.success(f"Chào **{student_name}**, bạn đã hoàn thành bài kiểm tra!")
        
        # Logic hiển thị kết quả
        st.metric(label="Điểm Trắc nghiệm của bạn", value=f"{total_score} / 4.0")
        
        if total_score >= pass_score: # Dùng điểm sàn giáo viên đặt (ví dụ set thấp xuống để test phần trắc nghiệm)
            st.balloons()
            st.header("🔓 ĐÁP ÁN CHI TIẾT")
            
            # Hiện đáp án MCQ
            st.subheader("Đáp án Trắc nghiệm")
            for q in exam_data["questions_mcq"]:
                user_val = user_answers_mcq.get(q['id'], "Chưa chọn")
                color = "green" if user_val.startswith(q['correct']) else "red"
                st.markdown(f"- **Câu {q['id']}:** Đáp án đúng: **{q['correct']}**. (Bạn chọn: :{color}[{user_val}])")
            
            # Hiện đáp án TF
            st.subheader("Đáp án Đúng/Sai")
            for group in exam_data["questions_tf"]:
                st.write(f"_{group['main_q']}_")
                for sub in group["sub_qs"]:
                    user_val = user_answers_tf.get(sub["id"], "Trống")
                    color = "green" if user_val == sub["correct"] else "red"
                    st.markdown(f"- {sub['id']}: Đáp án **{sub['correct']}**. (Bạn chọn: :{color}[{user_val}])")

            # Hiện đáp án Tự luận (Lấy từ PDF)
            st.subheader("Gợi ý giải Tự luận")
            st.markdown("""
            **Câu 1:**
            - Khái niệm: Mạng máy tính là hai hay nhiều máy tính và các thiết bị được kết nối để truyền thông tin cho nhau.
            - Lợi ích: Liên lạc, trao đổi thông tin, chia sẻ dữ liệu và dùng chung thiết bị.

            **Câu 2:**
            - a) Đổi 2TB = 2.000.000 MB. Số tệp ảnh tối đa = 2.000.000 / 2 = **1.000.000 tệp**.
            - b) 100 video x 5GB = 500GB. Dung lượng còn lại: 2000GB - 500GB = **1500 GB**.
            - c) Bit là đơn vị nhỏ nhất (0,1). Byte/KB/MB... dùng để tổ chức và đo lường dung lượng lớn dễ dàng hơn.
            """)
            
        else:
            st.warning(f"Bạn chưa đạt đủ điểm sàn ({pass_score} điểm) để xem đáp án chi tiết. Hãy thử lại nhé!")
            # Trong thực tế, điểm tự luận chiếm 60%, nên logic điểm sàn này 
            # chủ yếu dùng để check xem học sinh có làm nghiêm túc phần trắc nghiệm không.
