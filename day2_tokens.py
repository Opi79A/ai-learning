import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash-lite"

# ---- التجربة ١: كم توكن؟ ----
arabic = "أهلاً، كم سعر البرنامج؟"
english = "Hello, how much is the program?"

ar_tokens = client.models.count_tokens(model=MODEL, contents=arabic).total_tokens
en_tokens = client.models.count_tokens(model=MODEL, contents=english).total_tokens
print("عربي:", ar_tokens, "توكن")
print("إنجليزي:", en_tokens, "توكن")

# ---- التجربة ٢: الحرارة ----
question = "اقترح اسم واحد فقط لمتجر عطور، بدون شرح"

for temp in [0.0,1.0,2.0]:
    print(f"\n--- temperature = {temp} ---")
    for i in range(3):
        response = client.models.generate_content(
            model=MODEL,
            contents=question,
            config=types.GenerateContentConfig(temperature=temp),
        )
        print(response.text.strip())