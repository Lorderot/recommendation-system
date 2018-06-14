FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv

RUN apt-get install -y curl
RUN apt-get install -y libtool
RUN apt-get install -y automake
RUN apt-get install -y python3-tk
RUN curl -L https://github.com/libspatialindex/libspatialindex/archive/1.8.5.tar.gz | tar xz
WORKDIR libspatialindex-1.8.5
RUN bash autogen.sh
RUN bash configure
RUN make
RUN make install
RUN ldconfig

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

ADD requirements.txt /requirements.txt
ADD config.py /config.py
ADD get_real_estate.py /get_real_estate.py
ADD server.py /server.py
ADD models.py /models.py
ADD jsons /jsons
WORKDIR /
RUN python3.6 -m pip install -r requirements.txt

ENV APP_SETTINGS=config.ProductionConfig
ENV PROD_DATABASE_URL=postgresql://postgres:qawsed@saloedov.ml:5432/real_estate
ENV DEV_DATABASE_URL=postgresql://postgres:qawsed@saloedov.ml:5432/real_estate
ENV TEST_DATABASE_URL=postgresql://postgres:qawsed@saloedov.ml:5432/real_estate
#ENV PROD_DATABASE_URL=postgresql://lorderot:qawsed@10.18.90.62:5432/test_db
#ENV DEV_DATABASE_URL=postgresql://lorderot:qawsed@10.18.90.62:5432/test_db
#ENV TEST_DATABASE_URL=postgresql://lorderot:qawsed@10.18.90.62:5432/test_db
ENV FLASK_APP server.py

ENTRYPOINT ["python3.6", "server.py"]
