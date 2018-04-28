#run inside the docker nvidia-docker run  --name context2vec-gpu -it -p 8888:8888 -v /home/ql261/simp2trad/:/home/simp2trad/ chainer/chainer:v4.0.0-python2-lqc /bin/bash 

#install optional
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git
git config --global user.email "hey_flora@126.com"
git config --global user.name "Your Name"

# set up bash shell
# pack python project
cd /home/simp2trad/context2vec
sudo python setup.py install

# run jupyter
cd /home/
sudo chmod -R 777 ./*
cd /home/simp2trad/
sudo python -m pip install --upgrade pip
sudo python -m pip install jupyter
sudo python -m pip install pandas

if [ ! -d '/root/.jupyter/' ]; then
    sudo mkdir /root/.jupyter/
fi
#cp /home/simp2trad/bivec/jupyter_notebook_config.py /root/.jupyter/
for pid in $(ps -def | grep jupyter | awk '{print $2}'); do sudo kill -9 $pid; done

export SHELL=/bin/bash
jupyter notebook --ip '*'  --port=8888 --allow-root &
