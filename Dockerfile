FROM python:3.8-slim-buster

WORKDIR /app

ARG Parser_Name
ENV Parser_Name ${Parser_Name}

COPY requirements.txt requirements.txt
RUN mkdir /etc/pki

RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 4321
CMD ["sh", "-c", "python3 /app/src/${Parser_Name}.py"]
