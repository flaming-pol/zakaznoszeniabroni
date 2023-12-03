FROM python:3.11

WORKDIR /src

COPY ./src /src

RUN pip install -r /src/requirements.txt

ENV PYTHONPATH=/app

CMD ["sh"]
