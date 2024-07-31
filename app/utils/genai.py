import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))



def ask_question(question: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(question)
    return response.text

def generate_content(question, image) :
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = question
    if question :
        response = model.generate_content([prompt, image])
    else :
        response = model.generate_content(image)
    print(response)
    return response.text

