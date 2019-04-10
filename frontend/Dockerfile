FROM python:3.4-alpine
ADD citywok_frontend /citywok_frontend
ADD start-frontend.py /start-frontend.py
ADD requirements.txt /requirements.txt
WORKDIR /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "start-frontend.py"]
