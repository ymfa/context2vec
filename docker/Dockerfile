
FROM chainer/chainer:v4.0.0-python2
#RUN groupadd -g 999 ql261 && \
    #useradd -r -u 999 -g ql261 ql261

#USER ql261

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y \ 
    sudo  \
    git  \
    vim && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*
RUN python -m pip install --upgrade pip
RUN python -m pip install jupyter
RUN python -m pip install pandas


RUN git config --global user.email "hey_flora@126.com"
RUN git config --global user.name "qianchu"

RUN useradd -m ql261 && echo "ql261:ql261" | chpasswd && adduser ql261 sudo

USER ql261
