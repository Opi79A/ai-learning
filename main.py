import os
from dotenv import load_dotenv
from google import genai

# نقرأ المفتاح من ملف .env بدل ما نكتبه في الكود
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# نرسل الطلب للنموذج
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="مين هو الرسام الشهير فان جوخ؟",
)

# نطبع الرد
print(response.text)