import openai

client = openai.OpenAI()  # toimii vain jos ympäristömuuttuja on asetettu


# Lähetetään tiedosto ensin (jos se on local .webp-kuva)
file = client.files.create(
    file=open("kahvipaketti.webp", "rb"),
    purpose="assistants"
)

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a language model powering an application that generates fluent and persuasive product "
                        "descriptions and marketing slogans based on provided images and user input..."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"file://{file.id}"
                    }
                }
            ]
        }
    ],
)

print(response.choices[0].message.content)
