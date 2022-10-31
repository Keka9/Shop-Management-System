FROM python:3

RUN mkdir -p /opt/ShopManagementSystem/authentication
WORKDIR /opt/ShopManagementSystem/authentication

COPY ./authentication/application.py ./application.py
COPY ./authentication/configuration.py ./configuration.py
COPY ./authentication/models.py ./models.py
COPY ./authentication/requirements.txt ./requirements.txt
COPY ./utilities.py ../utilities.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/ShopManagementSystem"

ENTRYPOINT ["python", "./application.py"]
