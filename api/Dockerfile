FROM python:3.10
RUN mkdir /app 
COPY ./api /app/api
COPY README.md /app


COPY pyproject.toml /app 
COPY app.py /app
WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main

CMD [ "app.handler" ]
# CMD ["poetry", "run", "python", "app.py"]