import os
import math
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- ١. نقرأ الملف (جديد) ----
with open("store_info.txt", encoding="utf-8") as f:
    text = f.read()

# ---- ٢. نقسمه لقطع: كل فقرة قطعة (جديد) ----
chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
print("عدد القطع:", len(chunks))

# ---- ٣. نحول كل القطع لأرقام (فراغ ١: أنتِ تكتبينه) ----
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=chunks,
)
chunk_vectors = [e.values for e in result.embeddings]

# ---- ٤. دالة القرب (انسخيها من day4_embeddings.py) ----
def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size_a = math.sqrt(sum(x * x for x in a))
    size_b = math.sqrt(sum(y * y for y in b))
    return dot / (size_a * size_b)

# ---- ٥. دالة البحث (جديد) ----
def search(question, top_k=3):
    q = client.models.embed_content(model="gemini-embedding-001", contents=[question])
    q_vector = q.embeddings[0].values
    scores = [(similarity(q_vector, v), chunk) for v, chunk in zip(chunk_vectors, chunks)]
    scores.sort(reverse=True)
    return scores[:top_k]

# ---- ٦. نجرب (فراغ ٢: حلقة على الأسئلة) ----
questions = ["بكم البرنامج؟", "وش طرق الدفع؟", "فيه خصم؟"]

for q in questions:
    print("\n❓", q)
    for score, chunk in search(q):
        print(f"   {score:.3f} | {chunk[:60]}")