import os
import math
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.7-flash"


# ================= البحث في ملف المتجر (نفس اليوم ٤) =================
with open("store_info.txt", encoding="utf-8") as f:
    text = f.read()

chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

result = client.models.embed_content(model="gemini-embedding-001", contents=chunks)
chunk_vectors = [e.values for e in result.embeddings]

def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size_a = math.sqrt(sum(x * x for x in a))
    size_b = math.sqrt(sum(y * y for y in b))
    return dot / (size_a * size_b)


# ================= الأدوات: الوكيل يختار منها بنفسه =================

def search_store_info(question: str) -> str:
    """يبحث في معلومات متجر "صوتكِ الواثق" (السعر، المحتوى، الدفع، الاسترجاع، الأسئلة الشائعة).
    استخدمها لأي سؤال عن المنتج أو المتجر."""
    print("   🔧 الأداة: search_store_info")
    q = client.models.embed_content(model="gemini-embedding-001", contents=[question])
    q_vector = q.embeddings[0].values
    scores = [(similarity(q_vector, v), chunk) for v, chunk in zip(chunk_vectors, chunks)]
    scores.sort(reverse=True)
    return "\n\n".join(chunk for score, chunk in scores[:3])


def create_order(customer_name: str, quantity: int) -> str:
    """يسجل طلب شراء جديد لبرنامج "صوتكِ الواثق".
    استخدمها فقط إذا العميل قال صراحة إنه يبي يشتري، وذكر اسمه والكمية."""
    print("   🔧 الأداة: create_order")
    with open("orders.csv", "a", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), customer_name, quantity])
    return f"تم تسجيل طلب {customer_name}: {quantity} نسخة."


def escalate_to_human(reason: str) -> str:
    """يحوّل المحادثة لموظف بشري.
    استخدمها إذا العميل غاضب، أو عنده مشكلة في الدفع أو الفلوس، أو طلب يكلم موظف."""
    print("   🔧 الأداة: escalate_to_human")

    
    with open("escalations.csv", "a", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), reason])

    return "تم تحويل المحادثة لموظف، وبيتواصل معك قريب."


# ================= تعليمات الوكيل =================
instructions = """أنت وكيل خدمة عملاء لمتجر "صوتكِ الواثق".
عندك أدوات، واختر الأداة المناسبة حسب رسالة العميل:
- أي سؤال عن المنتج أو المتجر: استخدم search_store_info، وجاوب من نتيجتها فقط.
- إذا العميل يبي يشتري: لازم تعرف اسمه والكمية قبل ما تستخدم create_order. إذا ناقص شي، اسأله عنه.
- إذا العميل غاضب، أو عنده مشكلة في الدفع أو الفلوس، أو يبي موظف: استخدم escalate_to_human.
- التحية: رد بتحية قصيرة بدون أدوات.
إذا ما لقيت الجواب في المعلومات، قل: "ما عندي معلومة عن هذا، تقدر تتواصل معنا ونساعدك."
لا تخترع أي معلومة. جاوب باختصار وبلهجة سعودية ودودة."""


# ================= الوكيل =================
def agent(message):
    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    temperature=0,
                    # ✍️ فراغ ٢: حطي هنا قائمة الأدوات الثلاث بأسمائها (بدون أقواس بعد الاسم)
                    tools=[search_store_info, create_order, escalate_to_human],
                )
            )
            break
        except Exception as e:
                print("   ⏳ مشكلة:", type(e).__name__, str(e)[:200])
                time.sleep(10)

    if response is None:
        return "⚠️ ما قدرت أوصل للنموذج"
    return response.text


# ================= نجرب =================
messages = [
    "بكم البرنامج؟",
    "أبغى أشتري نسختين، اسمي سارة",
    "أبغى أشتري",
    "دفعت من أسبوع وما وصلني شي!! وين فلوسي",
    "السلام عليكم",
]

for m in messages:
    print("\n👤", m)
    print("🤖", agent(m))
    time.sleep(15)  # ننتظر ثانية قبل الرسالة الجاية