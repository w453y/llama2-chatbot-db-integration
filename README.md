# 🦙💬 Llama 2 Chatbot with Database Integration

This chatbot is created using the open-source Llama 2 LLM model from Meta and it saves the user input in the sqlite db.


## Getting your own Replicate API token

To use this app, you'll need to get your own [Replicate](https://replicate.com/) API token.

After signing up to Replicate, you can access your API token from [this page](https://replicate.com/account/api-tokens).

Replace the API token in ` .streamlit/secrets.toml `


## Installation

```
git clone https://github.com/w453y/llama2-chatbot-db-integration
cd llama2-chatbot-db-integration
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
streamlit run app.py
```

## Installation with Docker

```
docker build -t chatbot .
docker run -p 8501:8501 -v $(pwd):/app chatbot
```

### Access the saved User_Input from Database

```
sqlite3 llama_db.db
sqlite> SELECT * FROM user_input;
```
