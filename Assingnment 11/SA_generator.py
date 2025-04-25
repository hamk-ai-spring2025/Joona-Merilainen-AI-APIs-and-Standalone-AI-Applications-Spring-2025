from openai import OpenAI
from markdown_pdf import MarkdownPdf, Section
import os

client = OpenAI()

def ai(topic, title, author):
    print(f"Please wait... AI is generating an article about \"{topic}\" which will be converted into a PDF file and also printed on the screen.")

    response = client.responses.create(
        model="gpt-4.1",
        input="You are a scientific writing assistant. Your task is to generate a full scientific article in clean Markdown format "
              "based on a given topic. The article must follow academic structure and include APA references."
              f"The topic is: {topic}"



    )
    
    print("The article is now ready. The PDF file is located in the same folder as your program.")
    print(response.output_text)

    pdf = MarkdownPdf(toc_level=1)
    pdf.add_section(Section(response.output_text, paper_size="A4"), user_css="table, td, th {border: 1px solid black;}")
    pdf.meta["title"] = title
    pdf.meta["author"] = author
    pdf.save(f"{title}.pdf")   # Save the PDF to the current working directory


def main():
    print("Welcome to the scientific article generator!")
    topic = input("Enter a topic: ")
    title = input("Enter a title: ")
    author = input("Enter an author: ")
    ai(topic, title, author)
    while True:
        topic = input("Enter a topic, or press (x) to terminate the program:")
        if topic.lower() == "x":
            print("The program has been terminated. Thank you for using the scientific article generator!")
            break

        else:
            title = input("Enter a title: ")
            author = input("Enter an author: ")
            ai(topic, title, author)
        
        
main()
