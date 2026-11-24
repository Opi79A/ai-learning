import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time
from google.genai import errors
import csv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"

# ---- التعليمات: قصيرة، لأن الشكل صار محدد في القالب ----
instructions = """أنت نظام تصنيف رسائل عملاء لمتجر إلكتروني.
صنّف الرسالة وحدد أولويتها.

قواعد التصنيف:
- إذا فيه شكوى مع أي غرض آخر، صنّفها شكوى دائماً.
- إذا العميل عبّر عن رغبة بالشراء، حتى لو بشرط، صنّفها طلب.
- التحية فقط أو الرسائل اللي ما لها علاقة بالمتجر: أخرى.
- إذا العميل طلب إلغاء أو تعديل بدون ما يذكر مشكلة، صنّفها طلب. وإذا ذكر مشكلة، صنّفها شكوى.
قواعد الأولوية:
- عالية: مشكلة في فلوس العميل، أو طلب متأخر، أو عميل غاضب.
- متوسطة: عميل يبي يشتري، أو مشكلة بسيطة.
- منخفضة: سؤال عام أو تحية."""

# ---- القالب: الخانات والقيم المسموحة ----
schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "category": types.Schema(
            type=types.Type.STRING,
            enum=["استفسار", "شكوى", "طلب", "أخرى"],
        ),
        "priority": types.Schema(
            type=types.Type.STRING,
            enum=["عالية", "متوسطة", "منخفضة"],
        ),
    },
    required=["category", "priority"],
)

# ---- قائمة الاختبار: كل رسالة ومعها الجواب الصحيح ----
test_cases = [
    {"message": "كم سعر بوكس العناية بالبشرة؟ والرابط اللي أرسلتوه ما يشتغل", "expected": "شكوى"},
    {"message": "طلبت قبل يومين وللحين ما وصلني رقم تتبع، وما أحد يرد علي", "expected": "شكوى"},
    {"message": "السماعة متوفرة بالأسود؟ إذا متوفرة أبغى أطلب حبتين", "expected": "طلب"},
    {"message": "السلام عليكم", "expected": "أخرى"},
    {"message": "ودي ألغي طلبي", "expected": "طلب"},
    {"message": "تم خصم المبلغ مرتين من بطاقتي!!", "expected": "شكوى"},
    {"message": "مشكورين والله، ثالث مرة يوصلني المنتج مكسور 👏", "expected": "شكوى"},
    {"message": "وش طرق الدفع عندكم؟", "expected": "استفسار"},
]



correct = 0
tested = 0

rows = []

for case in test_cases:
    result = None

    # نحاول ٣ مرات، وبين كل محاولة ننتظر ١٥ ثانية
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=case["message"],
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            result = json.loads(response.text)
            break  # نجحت، نطلع من حلقة المحاولات
        except errors.ServerError:
            print("   ⏳ السيرفر مشغول، أنتظر ١٥ ثانية وأعيد...")
            time.sleep(13)

            

    # إذا فشلت المحاولات الثلاث، نتخطى الرسالة وما نحسبها
    if result is None:
        print("⚠️ ما انختبرت:", case["message"])
        continue

    tested += 1
    if result["category"] == case["expected"]:
        correct += 1
        mark = "✅"
    else:
        mark = "❌"

    print(mark, case["message"])
    print("   النموذج:", result["category"], "| المتوقع:", case["expected"], "| الأولوية:", result["priority"])

    rows.append({
        "الرسالة": case["message"],
        "المتوقع": case["expected"],
        "النموذج": result["category"],
        "الأولوية": result["priority"],
        "النتيجة": "صح" if mark == "✅" else "غلط",
    })

print(f"\nالدقة: {correct} من {tested} اختُبرت (من أصل {len(test_cases)})")

# حفظ النتائج في ملف CSV
with open("results.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["الرسالة", "المتوقع", "النموذج", "الأولوية", "النتيجة"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)