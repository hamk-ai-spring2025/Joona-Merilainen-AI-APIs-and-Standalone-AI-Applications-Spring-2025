import os
import re
import json
import asyncio
from collections import Counter
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from crawl4ai import AsyncWebCrawler
from openai import OpenAI

# Lataa OpenAI API-avain
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Hae tuotteen nimi, kuvaus ja arvostelu Crawl4AI:lla
async def hae_sisalto(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, dynamic=True, wait=3000)
        return result.markdown

# Hae tarjous- ja normaalihinta Playwrightilla
async def hae_hinnat(url):
    async with async_playwright() as p:
        selain = await p.chromium.launch(headless=True)
        sivu = await selain.new_page()
        await sivu.goto(url)
        await sivu.wait_for_timeout(3000)

        try:
            body_text = await sivu.locator("body").inner_text()
            hinnat_str = re.findall(r"\d{2,4},\d{2}", body_text)

            kelvolliset = []
            for h in hinnat_str:
                try:
                    num = float(h.replace(",", "."))
                    if 300.0 < num < 5000.0:
                        kelvolliset.append(h)
                except:
                    continue

            esiintymat = Counter(kelvolliset)
            toistuvat = [h for h in esiintymat if esiintymat[h] >= 2]

            if not toistuvat:
                return ("Hinta ei saatavilla", "Hinta ei saatavilla")

            toistuvat_num = [(float(h.replace(",", ".")), h) for h in toistuvat]
            toistuvat_num.sort()
            return (toistuvat_num[0][1], toistuvat_num[-1][1])

        except:
            return ("Hinta ei saatavilla", "Hinta ei saatavilla")
        finally:
            await selain.close()

# Kehota GPT-4:ää poimimaan tiedot ja parantamaan kuvauksen
def muodosta_json(markdown, tarjoushinta, normaalihinta):
    prompt = f"""
Alla on tuotetietoja verkkokaupan sivulta markdown-muodossa.

{markdown}

Tarjoushinta: {tarjoushinta}
Normaalihinta: {normaalihinta}

Tehtäväsi:
1. Poimi tuotteen nimi, lyhyt kuvaus ja arvostelun keskiarvo.
2. Kirjoita uusi, houkutteleva ja paranneltu tuotekuvaus huomioiden:
   - alkuperäinen kuvaus
   - annettu hinta
   - arvostelun keskiarvo

Palauta tulos seuraavassa JSON-muodossa:

{{
  "nimi": "...",
  "kuvaus": "...",
  "hinta": "...",
  "arvostelu": "...",
  "paranneltuKuvaus": "..."
}}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

# Koko sovelluksen ajo
async def suorita(url):
    markdown = await hae_sisalto(url)
    tarjous, normaali = await hae_hinnat(url)
    valmis_json = muodosta_json(markdown, tarjous, normaali)
    print(valmis_json)

def main():
    while True:
        test_url = str(input("Anna tuotteen URL tai lopeta ohjelma valitsemalla (x): "))
        if test_url.lower() == "x":
            print("Ohjelma lopetettu!")
            return False
        else:
            asyncio.run(suorita(test_url))  

# Testi-URL
if __name__ == "__main__":
    main()
