FROM python:3.8-alpine

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["frontend.py", "--host=0.0.0.0"]

ENTRYPOINT [ "python3" ]