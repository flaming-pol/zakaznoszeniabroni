FROM python:3.11

WORKDIR /src

COPY ./src /src

RUN pip install -r /src/requirements.txt

ENV PYTHONPATH=/app

#CMD ["python", "znb.py"]

ENTRYPOINT ["/src/entrypoint.sh"]
