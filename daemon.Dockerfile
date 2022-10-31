FROM python:3

RUN mkdir -p /opt/ShopManagementSystem/applications/daemon
WORKDIR /opt/ShopManagementSystem/applications/daemon

COPY ./applications/daemon/application.py ./application.py
COPY ./applications/daemon/requirements.txt ./requirements.txt
COPY ./applications/configuration.py ../configuration.py
COPY ./applications/models.py ../models.py
COPY ./utilities.py ../../utilities.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/ShopManagementSystem"

ENTRYPOINT ["python", "./application.py"]
