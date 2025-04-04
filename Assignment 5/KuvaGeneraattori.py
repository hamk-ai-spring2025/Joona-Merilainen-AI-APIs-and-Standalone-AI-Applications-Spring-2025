import os
import openai
from dotenv import load_dotenv

# Lataa .env-tiedoston muuttujat (jos käytössä)
load_dotenv()

# Hakee API-avaimen ympäristömuuttujasta
api_key = os.getenv("OPENAI_API_KEY")

# Luo asiakas
client = openai.OpenAI(api_key=api_key)


# Funktio joka luo kuvan promptista
def luoKuva(prompt):
    print("Luodaan kuva promptista!")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    print(f"Kuva luotu! Näet sen osoitteessa:\n{image_url}")

# Analysoi kuvan ja generoi siitä tekstin
def kuva(polku):
    kysymys = "Analysoi kuva"
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": kysymys},
                {
                    "type": "input_image",
                    "image_url": polku,
                },
            ],
        }],
    )

    # Printtaa generoidun testin
    print(response.output_text)
    print("\nOdota hetki, kuvaa analysoidaan...")
    # Lähettää generoidun tekstin luokuva funktiolle
    luoKuva(response.output_text)
    

def main():
    while True:
        kysymys = "Anna kuvatiedoston URL, kirjain X lopettaa ohjelman: "
        print (len(kysymys) * "-")
        kprintti = kysymys + "\n" + len(kysymys) * "-" + "\n"
        polku = input(kprintti)
        
        if polku.lower() == "x":
            print("Ohjelma lopetettu! ")
            return False
        else:
            kuva(polku)
    
    
main()
