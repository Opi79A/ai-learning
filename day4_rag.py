import os
import math
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time
from google.genai import errors

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

# ---- ٦. تعليمات المساعد (جديد) ----
instructions = """أنت مساعد خدمة عملاء لمتجر "صوتكِ الواثق".
جاوب على سؤال العميل من المعلومات المرفقة فقط.
إذا الجواب مو موجود في المعلومات، قل بالضبط: "ما عندي معلومة عن هذا، تقدر تتواصل معنا ونساعدك."
لا تخترع أي معلومة، ولا تستنتج شي مو مكتوب صراحة.
جاوب باختصار وبلهجة سعودية ودودة."""


def answer(question):
    results = search(question)
    context = "\n\n".join(chunk for score, chunk in results)
    prompt = f"المعلومات:\n{context}\n\nسؤال العميل: {question}"

    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    temperature=0,
                ),
            )
            break
        except errors.ServerError:
            print("   ⏳ السيرفر مشغول، أنتظر...")
            time.sleep(15)

    if response is None:
        return "⚠️ ما قدرت أوصل للنموذج"
    return response.text

# ---- ٨. نجرب ----
questions = [
    "بكم البرنامج؟",
    "كم صفحة البرنامج؟",
    "فيه خصم؟",
    "تشحنون نسخة مطبوعة؟",
    "مين أفضل لاعب كرة؟",
]


for q in questions:
    print("\n❓", q)
    print("💬", answer(q))