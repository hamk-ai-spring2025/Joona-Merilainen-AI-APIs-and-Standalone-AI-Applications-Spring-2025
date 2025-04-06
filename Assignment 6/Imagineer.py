from dotenv import load_dotenv
from openai import OpenAI
import os
import replicate
import random

client = OpenAI()

load_dotenv()  # lataa .env-tiedoston

token = os.getenv("REPLICATE_API_TOKEN")
if not token:
    raise Exception("REPLICATE_API_TOKEN not set!")

def kysely():
    prompti = input("What kind of image would you like? ")
    # Tekee promptista tiedostonnimet, jos yli 20 merkkiä leikkaa loput muuten pysyy samana
    if len(prompti) > 19:
        tiedostonNimi = prompti[0:20]
    else:
        tiedostonNimi = prompti
    siemen = input("Set seed (leave empty for random): ")
    if siemen == "":
        seed = random.randint(0, 4294967295)
    else:
        siemen = int(siemen)
        seed = siemen

    # Valitse kuva kuvasuhde      
    koko = int(input("Select an aspect ratio:\n 1) 1:1\n 2) 16:9\n 3) 4:3\n 4) 3:4\n"))

    if koko == 1:
        kuvakoko = "1:1"
    elif koko == 2:
        kuvakoko = "16:9"
    elif koko == 3:
        kuvakoko = "4:3"
    elif koko == 4:
        kuvakoko = "3:4"

    # Rajoittaa kuvien määrän 1-10 kpl
    maara = int(input("How many pictures do you want to generate? "))
    if maara > 10:
        maara = 10
        print("Unfortunately, the maximum number of images is 10")
        print("let's generate 10 images")
    elif maara < 1:
        maara = 1
        print("You need to generate at least 1 image.")
        print("Generating 1 image for you...")
    else:
        maara = maara
            
        
    
    
    kuva(prompti, tiedostonNimi,seed,kuvakoko, maara)
    

def kuva(prompti, tiedostonNimi,seed, kuvakoko, maara):
    
        kierros =1
        while kierros <= maara:
            print("\nGenerating image... Please wait a moment.")

            if kierros >= 2:
                seed = random.randint(0, 4294967295)
            nimi = f"{tiedostonNimi}_Seed_{seed}" + ".jpg"
            input={
                    "seed": seed,
                    "steps": 25,
                    "width": 1024,
                    "height": 1024,
                    "prompt": prompti,
                    "guidance": 3,
                    "interval": 2,
                    "aspect_ratio": kuvakoko,
                    "output_format": "jpg",
                    "output_quality": 80,
                    "safety_tolerance": 2,
                    "prompt_upsampling": False
                }

            output = replicate.run(
                "black-forest-labs/flux-pro",
                input=input
            )
            with open(nimi, "wb") as file:
                file.write(output.read())
            
           
            print(f"Photo has been generated")
            print("")
            print(f"Seed: {seed}\nFilename: {nimi}")
            print("The generated image is available at the following URL: ")
            print(output)
            print("")
            
            kierros += 1



def main():
    kysely()
    while True:
        ohjelma=input("Do you want to continue generating photos or exit the program? (y = yes, n = no):")
        if ohjelma.lower() == "y":
            kysely()
        elif ohjelma.lower() == "n":
            print("Thanks for using the program. Goodbye!")
            return False
        else:
            print("Invalid input. Please try again.")
        




main()




