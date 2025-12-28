import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_invoice_with_gemini(text):
    prompt = f"""
    You're an invoice extraction system.

    Extract the following fields from the invoice text:

    - invoice-number
    - invoice_date
    - total_amount 

    Return only a valid JSON object with these 3 keys.
    us null for missing values.

    Invoice text:
    {text}
    """
    
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # If Gemini returns code block formatting like ```json ...```
    if raw.startswith("```"):
        raw = raw.split("```")[1].replace("json", "").strip()

    try:
        return json.load(raw)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": raw}
    


def extract_invoice_with_groq(text):

    prompt = f"""
    Extrac the following fields from this invoice:
    
    - invoice_number
    - invoice_date 
    - total_amount
    
    Return only valid JSON.
    
    Invoice text:
    {text}
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{'role': "user", "content": prompt}],
        temperature=1,
        max_completion_tokens=8192,
        stream=False,
        stop=None
    )

    raw = completion.choices[0].message.content

    if raw.startswith("```"):
        raw = raw.split("```")[1].replace("json", "").strip()

    return json.loads(raw)
