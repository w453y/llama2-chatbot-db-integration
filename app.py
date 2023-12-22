import streamlit as st
import replicate
import os
import toml
import sqlite3

# Function to load API token from .streamlit/secrets.toml
def load_api_token():
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            return secrets.get("secrets", {}).get("REPLICATE_API_TOKEN", "")
        except Exception as e:
            st.warning(f"Error loading API token from secrets.toml: {e}")
    return ""

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Create SQLite database connection
conn = sqlite3.connect("llama_db.db")
cursor = conn.cursor()

# Create user_input table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_input (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_text TEXT NOT NULL
    )
''')
conn.commit()

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')

    # Load API token from .streamlit/secrets.toml
    replicate_api = load_api_token()

    if replicate_api:
        st.success('API key loaded from secrets.toml!', icon='✅')
    else:
        st.warning('API key not found in secrets.toml. Please enter your credentials!', icon='⚠️')
        replicate_api = st.text_input('Enter Replicate API token:', type='password')

    # Set the model to 'Llama2-13B' (fixed value)
    selected_model = 'Llama2-13B'
    llm = "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d"

    # Set fixed values for temperature, top-p, and max length
    temperature = 0.75
    top_p = 1.0
    max_length = 800

    # Set values for additional parameters
    debug = False
    top_k = 50
    system_prompt = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
    max_new_tokens = 500
    min_new_tokens = -1

os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm, 
                           input={
                               "prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                               "temperature": temperature,
                               "top_p": top_p,
                               "max_length": max_length,
                               "repetition_penalty": 1,
                               "debug": debug,
                               "top_k": top_k,
                               "system_prompt": system_prompt,
                               "max_new_tokens": max_new_tokens,
                               "min_new_tokens": min_new_tokens
                           })
    return output

# Save user input in the database
def save_user_input(user_input):
    cursor.execute("INSERT INTO user_input (input_text) VALUES (?)", (user_input,))
    conn.commit()

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Save user input to the database
    save_user_input(prompt)
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)

# Close the database connection
conn.close()