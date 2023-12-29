FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

VOLUME ["/app"]

CMD ["streamlit", "run", "app.py"]
