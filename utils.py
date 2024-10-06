

import json
import re
from data_models import *
import google.generativeai as genai

prompt = """using the pdf provided, understand the text in it and answer questions about the content in
the documents which would be provided in a variable named user_question
and respond with an
answer to the question, a list of bullet points and also create a test question and a test answer to evaluate user's understanding
of your answer.. return your response in exactly python dictionary format with the fields, answer, bullet_points, test_question,
test_answer. Use this schema:

answer: string
bullet_points: list[string]
test_question: string
test_answer: string
"""

API_KEY="AIzaSyBpzPj83cCLSlHWNSqX_mFQWbYelerzRpA"

genai.configure(api_key=API_KEY)

def query_system(user_question):
    #read text
    model = genai.GenerativeModel("gemini-1.5-flash")
    sample_pdf = genai.upload_file("./uploads/file_for_query.pdf")
    response = model.generate_content([prompt, sample_pdf, user_question])
    return response.text



def extract_json_from_string(text):
  """Extracts the first JSON-like string from a larger text string."""
  match = re.search(r'({.*?})', text, re.DOTALL)
  if match:
    try:
      json_string = match.group(1)
      json_data = json.loads(json_string)
      return json_data
    except json.JSONDecodeError:
      print("Error decoding JSON")
      return None
  else:
    print("No JSON-like string found")
    return None

def save_test_question_id(test_question_id):
  """Saves the test_question_id to a temporary file."""
  with open('test_question_id.txt', 'w') as f:
    f.write(test_question_id)


def dummy_json_data():
  """
  Returns dummy data in the specified JSON format.
  """
  return {
      "answer": "This is a dummy answer to the question.",
      "bullet_points": [
          "This is a dummy bullet point 1.",
          "This is a dummy bullet point 2.",
          "This is a dummy bullet point 3."
      ],
      "test_question": "This is a dummy test question?",
      "test_answer": "This is a dummy test answer."
  }


def query_system_or_return_dummy(user_question):
  try:
    response = query_system(user_question)
    return response
  except Exception as e:
    print(e)
    return dummy_json_data()
