FROM python:3

RUN mkdir -p /opt/ShopManagementSystem/applications/warehouse
WORKDIR /opt/ShopManagementSystem/applications/warehouse

COPY ./applications/warehouse/application.py ./application.py
COPY ./applications/warehouse/requirements.txt ./requirements.txt
COPY ./applications/configuration.py ../configuration.py
COPY ./applications/models.py ../models.py
COPY ./utilities.py ../../utilities.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/ShopManagementSystem"

ENTRYPOINT ["python", "./application.py"]
