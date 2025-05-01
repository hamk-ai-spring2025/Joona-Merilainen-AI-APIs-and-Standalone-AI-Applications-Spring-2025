import os
import streamlit as st
import replicate
from openai import OpenAI

# Sidebar for model selection and clear chat
st.sidebar.title("ModelSwitch")
model_choice = st.sidebar.selectbox(
    "Choose a model", 
    ["gpt-4", "ibm-granite/granite-3.3-8b-instruct", "deepseek"]
)
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main chat area
st.subheader("Chat")

# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model_choice.startswith("gpt-4"):
            st.badge("gpt-4")
            openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            stream = openai_client.chat.completions.create(
                model=model_choice,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            response = st.write_stream(stream)

        elif model_choice == "ibm-granite/granite-3.3-8b-instruct":
            st.badge("ibm-granite/granite-3.3-8b-instruct")
            replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
            prompt_text = (
                "You are a helpful, concise assistant. Answer the user's question clearly, "
                "and stop when the response is complete. Do not continue with additional topics.\n\n" +
                "\n\n".join(
                    f"Human: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
                    for m in st.session_state.messages
                ) +
                "\n\nAssistant:"
            )
            response_container = st.empty()
            output_text = ""
            for event in replicate_client.stream(
                "ibm-granite/granite-3.3-8b-instruct",
                input={"prompt": prompt_text, "max_tokens": 512, "temperature": 0.7}
            ):
                output_text += event.data
                response_container.markdown(output_text)
            response = output_text.strip()
            if response.endswith("{}"):
                lines = response.splitlines()
                if lines and lines[-1].strip() == "{}":
                    response = "\n".join(lines[:-1]).rstrip()

        elif model_choice == "deepseek":
            st.badge("deepseek")
            replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
            prompt_text = (
                "You are a helpful and concise assistant.\n\n" +
                "\n\n".join(
                    f"User: {m['content']}" if m['role'] == 'user' else f"Assistant: {m['content']}"
                    for m in st.session_state.messages
                ) +
                "\n\nAssistant:"
            )
            response_container = st.empty()
            output_text = ""
            for event in replicate_client.stream(
                "deepseek-ai/deepseek-v3",
                input={
                    "prompt": prompt_text,
                    "max_tokens": 1024,
                    "temperature": 0.6,
                    "top_p": 1,
                    "presence_penalty": 0,
                    "frequency_penalty": 0
                }
            ):
                output_text += event.data
                response_container.markdown(output_text)
            response = output_text.strip()
            if response.endswith("{}"):
                lines = response.splitlines()
                if lines and lines[-1].strip() == "{}":
                    response = "\n".join(lines[:-1]).rstrip()

    # Save assistant response
    response = f"[{model_choice}]\n\n{response}"
    st.session_state.messages.append({"role": "assistant", "content": response})
