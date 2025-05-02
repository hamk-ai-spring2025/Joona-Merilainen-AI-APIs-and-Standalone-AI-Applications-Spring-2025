# OSA 1: KIRJASTOJEN TUONTI
import streamlit as st
import replicate
import os
import requests
from PIL import Image
from io import BytesIO

# OSA 2: REPLICATE-AVAIN JA AUTENTIKAATIO
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN is None:
    st.error("Replicate API -avain puuttuu. Aseta se ympäristömuuttujaan!")
    st.stop()
replicate.Client(api_token=REPLICATE_API_TOKEN)

# OSA 3: SIVUPALKIN ASETUKSET
with st.sidebar:
    st.title("AI Image Generation: Flux Schnell")
    st.header("Prompt and Settings")

    prompt = st.text_area("Enter a prompt describing the image", height=68)

    use_random_seed = st.checkbox("Use custom seed (uncheck for random)", value=True)
    if use_random_seed:
        random_seed = st.slider("Seed value", 0, 1000, 435)
    else:
        random_seed = None

    output_quality = st.slider("Image quality (%)", 50, 100, 80)
    ratio = st.selectbox(
        'Aspect ratio',
        ('1:1', '16:9', '3:2','2:3','4:5','5:4','9:16','3:4','4:3'))
    
    st.write('Selected aspect ratio:', ratio)

    generate_button = st.button("Generate Image")

# OSA 4: SESSION STATE - ALUSTUS
if "image_url" not in st.session_state:
    st.session_state["image_url"] = None

# OSA 5: KUVA-GENEROINTI
if generate_button and prompt:
    with st.spinner("Generating image…"):
        try:
            input_data = {
                "prompt": prompt,
                "aspect_ratio": ratio,
                "quality": output_quality
            }
            if random_seed is not None:
                input_data["seed"] = random_seed

            # Palauta URL:t, ei FileOutput-olioita
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input=input_data,
                use_file_output=False
            )

            # Varmista, että output on lista URL-osoitteita
            if isinstance(output, (list, tuple)) and output:
                st.session_state["image_url"] = output[0]
            else:
                st.error("Model output is not a valid list of URLs.")
        except Exception as e:
            st.error(f"An error occurred during image generation: {e}")

# OSA 6: KUVA JA LATAUSNAPPULA
image_url = st.session_state.get("image_url")
if image_url:
    col1, col2 = st.columns(2)
    with col1:
        st.image(image_url, caption="Generated image")
    with col2:
        resp = requests.get(image_url)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)
            st.download_button(
                label="Download image",
                data=buffer,
                file_name="generated_image.jpg",
                mime="image/jpeg"
            )
        else:
            st.error("Error while downloading the image.")
else:
    st.info("No image yet – click 'Generate Image' to create one.")
