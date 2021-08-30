FROM python:3.6

COPY requirements.txt /

RUN python3 -m pip install -r requirements.txt

# To manage pygraphviz dependency
RUN apt-get update
RUN apt-get -y install pkg-config graphviz python-dev libgraphviz-dev
RUN pip install pygraphviz==1.5

# Add and set JDK 8
RUN apt-get install -y apt-utils build-essential gcc

ENV JAVA_FOLDER java-se-8u41-ri

ENV JVM_ROOT /usr/lib/jvm

ENV JAVA_PKG_NAME openjdk-8u41-b04-linux-x64-14_jan_2020.tar.gz
ENV JAVA_TAR_GZ_URL https://download.java.net/openjdk/jdk8u41/ri/$JAVA_PKG_NAME

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*    && \
    apt-get clean                                                               && \
    apt-get autoremove                                                          && \
    echo Downloading $JAVA_TAR_GZ_URL                                           && \
    wget -q $JAVA_TAR_GZ_URL                                                    && \
    tar -xvf $JAVA_PKG_NAME                                                     && \
    rm $JAVA_PKG_NAME                                                           && \
    mkdir -p /usr/lib/jvm                                                       && \
    mv ./$JAVA_FOLDER $JVM_ROOT                                                 && \
    update-alternatives --install /usr/bin/java java $JVM_ROOT/$JAVA_FOLDER/bin/java 1        && \
    update-alternatives --install /usr/bin/javac javac $JVM_ROOT/$JAVA_FOLDER/bin/javac 1     && \
    java -version

# To fix: ImportError: cannot import name 'abc'
RUN python3 -m pip uninstall bson && python3 -m pip uninstall --yes pymongo && python3 -m pip install bson && python3 -m pip install pymongo==3.8.0

COPY client-connector /

ENTRYPOINT ["python3", "cc_controller.py"]