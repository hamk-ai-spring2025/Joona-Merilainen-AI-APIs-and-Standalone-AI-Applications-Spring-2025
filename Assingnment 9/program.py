import os
import openai
import base64
import math
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
kuvaukset = []




def puhdista():
    kuvaukset.clear()

# Base64-kuvan lataus
def kuva_base64(polku):
    with open(polku, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def tulosta():
    kierros = 0
    for i in kuvaukset:
        kierros += 1
        print(" ")
        print("picture",kierros,"\n")
        print(i)


def ai(kuva, message):
    global kuvaukset
    
    # Viestit GPT-4o:lle
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        
                            "You are a language model powering an application that generates fluent and persuasive product descriptions"
                            "and marketing slogans based on provided images and user input. Analyze the images (using provided descriptions"
                            "or metadata) and combine that information with additional user-provided context, such as product name, purpose,"
                            "target audience, or other relevant details. Write clear, appealing, and sales-oriented product descriptions in English."
                            f"{message}"
                            "Also create 3 short, catchy slogan that captures the product’s key benefits. Be creative, but stay factual. "
                            "Never invent product features that cannot be inferred from the images or user input."
                    )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{kuva}"
                    }
                }
            ]
        }
    ]

    # Kutsu GPT-4o:ta (huomaa uusi syntaksi)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500
    )

    # lisää AI:n vastaus globaaliin listaan
    teksti = response.choices[0].message.content
    kuvaukset.append(teksti)
    
def main():
    print("Welcome to the program!")
    print("-----------------------")
    while True:
        valikko = input("Do you want to use the program or exit? Yes = y and No = n: ")
        if valikko.lower() == "n":
            print("Program terminated. Thank you for using it.")
            return False
        kuvienMaara = int(input("Select how many images you want to upload to the service; "))

        if kuvienMaara >= 1:
            for i in range(kuvienMaara):
                kuva = str(input("load a photo: "))
                viesti = str(input("user input/comment: "))
                print("Please wait a moment. The system is uploading the photo for analysis.\n")
                ai(kuva_base64(kuva), viesti)
            tulosta()
            kuvaukset.clear()


main()
