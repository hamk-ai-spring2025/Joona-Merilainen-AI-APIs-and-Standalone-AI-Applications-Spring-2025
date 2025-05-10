import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.utilities import GoogleSerperAPIWrapper
import re

# Ladataan ympäristömuuttujat
load_dotenv()
serper_api_key = os.getenv("SERPER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not serper_api_key or not openai_api_key:
    st.error("API-avaimia ei löydy. Lisää ne .env-tiedostoon.")
    st.stop()

# GPT-4 + systeemiprompti
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.5,
    openai_api_key=openai_api_key
)

# Prompti uutistiivistykselle
prompt = ChatPromptTemplate.from_messages([
    ("system", "Olet asiantunteva ja puolueeton uutistiivistäjä. Kirjoita selkeä, ytimekäs ja faktapohjainen yhteenveto."),
    ("human", "{news_input}")
])

chain = LLMChain(llm=llm, prompt=prompt)

# Serper-haku ilman kielirajoituksia
search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)

# Streamlit UI
st.set_page_config(page_title="Uutishaku & Yhteenveto", layout="centered")
st.title("Uutishaku ja yhteenveto")
st.write("Syötä hakusana, valitse aikaväli ja hae tiivistelmä ajankohtaisista uutisista.")

search_term = st.text_input("Hakusana tai aihe", "ukrainan sota")
time_period = st.selectbox("Aikaväli", ["tänään", "viime viikolla", "viime kuussa", "viime vuonna"])

# Muuttaa päivät englanninkieliksi
if time_period == "tänään":
    time_period = "today"
elif time_period == "viime viikolla":
    time_period ="last week"
elif time_period == "viime kuussa":
    time_period ="last month"
elif time_period == "viime vuonna":
    time_period ="last year"
    
if st.button("Hae ja tiivistä uutiset"):
    query = f"{search_term} uutiset {time_period}"

    with st.spinner("Haetaan uutisia..."):
        try:
            raw_results = search.run(query)
            #st.subheader("Haun raakadata (debug):")
            #st.code(raw_results, language="text")


            # Erota otsikot, suodata ja pidä vain ne, joissa esiintyy hakusana
            headlines = re.split(r'[\n•·–|]+', raw_results)
            keyword = search_term.lower()
            cleaned = [line.strip() for line in headlines if line.strip()]



            if not cleaned:
                st.warning("Ei löytynyt aiheeseen liittyviä uutisotsikoita.")
                st.stop()

            st.subheader("Haetut uutisotsikot:")
            for i, item in enumerate(cleaned[:10], 1):
                st.markdown(f"**{i}.** {item}")

            with st.spinner("Tiivistetään uutiset..."):
                filtered_text = "\n".join(cleaned)
                summary = chain.run(news_input=filtered_text)
                st.subheader("Yhteenveto:")
                st.write(summary)

        except Exception as e:
            st.error(f"Tapahtui virhe: {e}")
