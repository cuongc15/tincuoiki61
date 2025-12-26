from docx import Document
import re

def load_questions(path):
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)

    pattern = r"(Câu\s+\d+\..*?)(?=\nCâu\s+\d+\.|\nII\.|\Z)"
    raw = re.findall(pattern, text, flags=re.S)

    mcq = []
    essay = []

    for block in raw:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        q = lines[0]

        options = [l for l in lines[1:] if l[:2] in ["A.", "B.", "C.", "D."]]

        if options:
            mcq.append({
                "question": q,
                "options": options,
                "answer": options[0][0]
            })
        else:
            essay.append(q)

    return mcq, essay
