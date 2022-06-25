FROM python:3.9
# COPY requirements.txt requirements.txt
WORKDIR product-aggregator
COPY . .
RUN pip3 install -r requirements.txt

