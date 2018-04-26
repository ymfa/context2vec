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

if [ ! -d '/root/.jupyter/' ]; then
    mkdir /root/.jupyter/
fi
#cp /home/simp2trad/bivec/jupyter_notebook_config.py /root/.jupyter/
for pid in $(ps -def | grep jupyter | awk '{print $2}'); do sudo kill -9 $pid; done

export SHELL=/bin/bash
jupyter notebook --ip '*'  --port=8888 --allow-root &
