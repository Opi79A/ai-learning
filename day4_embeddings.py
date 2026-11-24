import os
import math
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

question = "بكم البرنامج؟"
sentences = [
    "كم سعر البرنامج؟",
    "وش التكلفة؟",
    "ما هي مدة البرنامج؟",
    "متى يوصلني الملف؟",
    "الجو حار اليوم",
    "هل يمكنني الدفع بالفيزا؟",
]

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=[question] + sentences,
)
vectors = [e.values for e in result.embeddings]

print("عدد الأرقام في كل جملة:", len(vectors[0]))

def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    size_a = math.sqrt(sum(x * x for x in a))
    size_b = math.sqrt(sum(y * y for y in b))
    return dot / (size_a * size_b)

question_vector = vectors[0]
for sentence, vector in zip(sentences, vectors[1:]):
    score = similarity(question_vector, vector)
    print(f"{score:.3f}  {sentence}")