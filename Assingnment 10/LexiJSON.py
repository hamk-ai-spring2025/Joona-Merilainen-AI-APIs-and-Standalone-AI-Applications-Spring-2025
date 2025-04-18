import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Lataa API-avain
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai(sana):
    
    # Promptti
    promptti = f"""You are a JSON dictionary assistant. Given a single word (in Finnish or English), return a valid and properly formatted JSON object with the following structure:

    {{
      "word": "<the input word>",
      "definition": "<short and clear definition of the word>",
      "synonyms": [<list of synonyms>],
      "antonyms": [<list of antonyms>],
      "examples": [<example sentences showing how the word is used>]
    }}

    Rules:
    - Output only the JSON object. No explanations or extra text.
    - If there are no antonyms, return an empty list.
    - Examples must be in the same language as the word.
    - Escape all special characters properly.

    Word: {sana}"""


    # API-kutsu
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": promptti}
        ],
        temperature=0.7,
        max_tokens=500
    )

    # Hae vastaus
    content = response.choices[0].message.content.strip()

    # Poista mahdollinen ```json```-merkkien ympäristö
    if content.startswith("```json"):
        content = re.sub(r"^```json\s*|```$", "", content.strip(), flags=re.DOTALL)

    # Yritä parsia JSON
    try:
        parsed = json.loads(content)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Received invalid JSON.")
        print(content)

def main():
    print("Welcome to LexiJSON!\nThis tool creates structured JSON dictionary entries based on any word you give.")

    while True:
        sana = input("Enter a word or exit the program (x): ")
        if sana.lower() == "x":
            print("The program has been terminated, thank you for using it!")
            return False
        ai(sana)

main()
        
