from python:alpine

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT python main.py