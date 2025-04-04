import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

otsikko = "Luova kirjoittaja sovellus"
print(otsikko)
print(len(otsikko) * "-")

while True:
    
    print("")
    print("Kirjoita syötteeseen millaisen tekstin haluat minun luovan tai lopeta kirjoittamalla q ja paina enter.")
    print("")
    content = input("syöte: ")
    if content == "q" or content == "Q":
        print("Ohjelma lopetettu")
        break
    else:
        

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Olet luova ja ammattimainen SEO-kirjoittaja. Tehtäväsi on tuottaa alkuperäistä, mielikuvituksellista sisältöä, kuten markkinointitekstejä, meemejä, laulunsanoja, runoja tai blogikirjoituksia. Kirjoitustesi tulee olla hakukoneoptimoituja (SEO), mikä tarkoittaa, että käytät mahdollisimman paljon olennaisia synonyymeja ja avainsanojen muunnelmia luonnollista sujuvuutta ja luettavuutta heikentämättä. Anna aina kolme erilaista versiota samasta kehotteesta, jokainen eri tyylillä tai sävyllä. Ole ilmaisultasi vahva, mukaansatempaava ja avainsanoja runsaasti hyödyntävä."},
                {"role": "user", "content": content}
            ],
                temperature=0.9,           
                top_p=0.95,                 
                presence_penalty=0.8,      
                frequency_penalty=0.4       
                
        )

        print(response.choices[0].message.content)
