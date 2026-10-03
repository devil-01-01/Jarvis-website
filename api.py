from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import torch
import re
import sympy as sp

app = FastAPI(title="BOSS JARVIS API - Direct 20B")

# --- 1. AAPKA MODEL DIRECT LOAD - BINA GROQ KE ---
print("Loading Model: openai/gpt-oss-20b...")

jarvis_model = pipeline(
    task="text-generation",
    model="openai/gpt-oss-20b",
    torch_dtype=torch.float32,
    trust_remote_code=True,
    device_map="auto"
)

print("Model Loaded: openai/gpt-oss-20b")

# --- 2. Request Body ---
class Query(BaseModel):
    question: str

# --- 3. Maths Brain ---
def solve_maths(q: str):
    try:
        if "%" in q:
            nums = re.findall(r"\d+\.?\d*", q)
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
                return f"{a}% of {b} = {a*b/100}"
        if "solve" in q.lower():
            x = sp.Symbol('x')
            eq = q.lower().split("solve")[-1].split("=")[0].replace("^","**")
            expr = sp.sympify(eq)
            sol = sp.solve(expr, x)
            return f"Answer: {sol}"
        return None
    except:
        return None

# --- 4. API Endpoints ---

@app.get("/")
def home():
    return {"status": "BOSS JARVIS Running", "model": "openai/gpt-oss-20b", "groq": "Not Used"}

@app.post("/chat")
def chat(data: Query):
    q = data.question

    # Pehle maths check
    math_ans = solve_maths(q)
    if math_ans:
        return {"type": "maths", "answer": math_ans}

    # Nahi to Direct 20B Model se
    prompt = f"You are BOSS JARVIS. Answer this: {q}\nAnswer:"
    output = jarvis_model(prompt, max_new_tokens=250, temperature=0.7, do_sample=True)
    answer = output[0]['generated_text'][len(prompt):].strip()

    return {"type": "chat/coding/reasoning", "model": "openai/gpt-oss-20b", "answer": answer}

@app.post("/maths")
def maths_api(data: Query):
    ans = solve_maths(data.question)
    return {"answer": ans if ans else "Not a maths query"}

# Run with: uvicorn api:app --reload
