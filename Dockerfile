FROM python:3.6

COPY requirements.txt /
COPY client-connector /

RUN python3 -m pip install -r requirements.txt

# To manage pygraphviz dependency
RUN apt-get update
RUN apt-get -y install pkg-config graphviz python-dev libgraphviz-dev
RUN pip install pygraphviz==1.5

ENTRYPOINT ["python3", "cc_controller.py"]