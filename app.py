import streamlit as st
import random
from datetime import datetime
import pandas as pd
from questions_reader import load_questions
from utils import save_result

st.set_page_config(page_title="Quiz Tin học 6", layout="centered")

st.title("📘 Ứng dụng kiểm tra – Tin học 6")

st.subheader("🔐 Xác thực thông tin học sinh")

name = st.text_input("Họ và tên")
school_class = st.text_input("Lớp")

if not name or not school_class:
    st.warning("👉 Vui lòng nhập đầy đủ họ tên và lớp để bắt đầu.")
    st.stop()

st.success("✅ Xác thực thành công")

questions_mcq, questions_essay = load_questions("sample_questions.docx")

random.shuffle(questions_mcq)
for q in questions_mcq:
    random.shuffle(q["options"])


st.header("📝 Phần I – Trắc nghiệm")

answers = []
score = 0

for i, q in enumerate(questions_mcq, start=1):
    st.subheader(f"Câu {i}: {q['question']}")
    choice = st.radio("Chọn đáp án:", q["options"], key=f"mcq_{i}")

    answers.append((q["question"], choice, q["answer"]))

    if choice.startswith(q["answer"]):
        score += 1


st.header("✍️ Phần II – Tự luận")

essay_results = []

for i, q in enumerate(questions_essay, start=1):
    st.subheader(f"Câu T{i}: {q}")
    text = st.text_area("Bài làm:", key=f"essay_{i}")
    essay_results.append((q, text))

if st.button("📌 Nộp bài"):
    st.write("---")
    st.subheader("📊 Kết quả")

    st.success(f"🎯 Điểm trắc nghiệm: **{score}/{len(questions_mcq)}**")

    if score >= 6:
        st.success("🏆 Bạn đạt từ 6 điểm — cho phép xem đáp án")

        st.write("### ✅ Đáp án đúng")

        for q, c, a in answers:
            st.write(f"• **{q}**")
            st.write(f"👉 Đáp án đúng: **{a}**")

    else:
        st.warning("⚠️ Chưa đủ 6 điểm — chưa thể xem đáp án")

    save_result(
        name=name,
        school_class=school_class,
        score=score,
        answers=answers,
        essays=essay_results
    )

    st.info("💾 Bài làm đã được lưu")
