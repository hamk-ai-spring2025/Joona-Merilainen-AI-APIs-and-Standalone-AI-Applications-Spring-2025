import os
from dotenv import load_dotenv
from openai import OpenAI
from markitdown import MarkItDown
import pandas as pd

# Alustetaan Markdown-konversiokirjasto
md = MarkItDown(enable_plugins=False)

# Ladataan API-avain .env-tiedostosta
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Markdown-olioiden luokka
class mdc:
    oliolista = []

    def __init__(self, a):
        self.olio = a
        mdc.oliolista.append(self)

    def __str__(self):
        return self.olio

    def __repr__(self):
        return f"mdc(olio='{self.olio[:30]}...')"
    
def jatka():
    while True:
        jatkatko = input("\nHaluatko jatkaa ohjelman käyttöä? (k = kyllä ja e = ei) ")
        if jatkatko.lower() == "k":
            print("Jatketaan ohjelman käyttöä\n")
            print("Oletusprompti palautettu!\n")
            return True
        elif jatkatko.lower() == "e":
            print("Ohjelma lopetettu")
            return False
        else:
            print("Virheellinen valinta. Syötä 'k' tai 'e'.")

    

def ohjelma():
    
    prompti = "Tee tiivistelmä sisällöstä suomen kielellä, aineiston kielestä riippumatta"
    print("")
    print("paina (h) jos tarvitset apua")
    x = True
    
    # --- Päälooppi tiedostojen lisäämiselle ---
    while x == True:
        valikko = input("Lisää tiedosto (l), vaihda promptia (p) tai siirry analyysiin (s): ")
        
        if valikko.lower() == "x":
            print("Ohjelma lopetettu")
            x = False

        elif valikko.lower() == "s":
            break
        elif valikko.lower() == "h":
            print("")
            print("h avaa tämän valikon josta näet ohjelman pikakomennot")
            viiva = len("h avaa tämän valikon josta näet ohjelman pikakomennot")
            print(viiva * "-")
            print("Valinnat:")
            print("-h, --auta")
            print("näyttää tämän viestin\n")
            print("-l, --lisää tiedosto")
            print("-p vaihda promptia")
            print("voit muuttaa AI:lle tehtävää kyselyä,\nvakiona ohjelma antaa tiivistelmän syötetyistä tiedostoista\n")
            print("-r, --resetointi      resetoi datan")
            print("-t, --tallennus       tallentaa outputin tiedostoon")
            print("-s, --siirry analyysiin")
            print("-x, --lopeta          lopettaa ohjelman")
            print("")

        elif valikko.lower() == "p":
            prompti = str(input("Kirjoita AI:lle uusi systeemiprompti: "))
            

        elif valikko.lower() == "l":
            polku = input("Anna ladattavan tiedoston polku: ")
            try:
                if polku.endswith(".csv"):
                    df = pd.read_csv(polku)
                    content = df.to_markdown(index=False)  # muunnetaan markdown-taulukoksi
                else:
                    result = md.convert(polku)
                    content = result.markdown

                mdc(content)
                print("Tiedosto lisätty.\n")
            except Exception as e:
                print(f"Tapahtui virhe: {e}\n")
                
        elif valikko.lower() == "r":
            res = input("Oletko varma että haluat poistaa kaiken datan joka on tallennettu? (k = kyllä) ")
            if res == "k":
                print("Data on resetoitu!")
                mdc.oliolista.clear()
            else:
                print("Ladattua dataa ei resetoitu")
                continue

        else:
            print("Virheellinen valinta.\n")

    # --- Yhdistetään kaikkien olioiden sisältö GPT:lle ---
    if mdc.oliolista:
        kokonaisuus = "\n\n".join(str(obj) for obj in mdc.oliolista)

        print("Lähetetään aineisto GPT:lle arvioitavaksi...\n")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompti},
                {"role": "user", "content": kokonaisuus}
            ],
            temperature=0.3,
            top_p=0.9,
            presence_penalty=0.0,
            frequency_penalty=0.2,
            stream=True
        )
        valinta = input ("Haluatko tallentaa  outputin tiedostoon? (k = kyllä ja e = ei) ")
        if valinta.lower() == "k":
            tnimi = str(input("Anna tiedoston nimi: "))
            print("Tallennetaan output tiedostoon ja tulostetaan terminaaliin")
            f = open(f"{tnimi}.txt", "a")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    f.write(chunk.choices[0].delta.content)
            f.close()

        elif valinta.lower() == "e":
            print("Printataan terminaaliin!")
            print("--- GPT:n vastaus ---\n")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)

    else:
        print("Ei tiedostoja käsiteltäväksi.")
  
        
def main():
    print("TIEDOSTOJEN AI-ANALYYSIOHJELMA")
    while True:
        ohjelma()
        if not jatka():
            break



    
main()
