FROM python:3

RUN mkdir -p /opt/ShopManagementSystem/applications
WORKDIR /opt/ShopManagementSystem/applications

COPY ./applications/migrate.py ./migrate.py
COPY ./applications/configuration.py ./configuration.py
COPY ./applications/models.py ./models.py
COPY ./authentication/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/ShopManagementSystem"

ENTRYPOINT ["python", "./migrate.py"]
