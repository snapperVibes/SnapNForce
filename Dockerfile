FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Do we need to proxy headers?
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

COPY requirements.txt .
EXPOSE 8000
CMD python main.py
