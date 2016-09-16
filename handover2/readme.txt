# 0. requirements

# install libtins on each AP node

sudo apt-get install libboost-all-dev
git clone https://github.com/mfontanini/libtins.git
cd libtins/
mkdir build
cd build/
cmake ../
make
sudo make install

# build external scanner daemon
cd scanner
cd build/
cmake ../
make

# install DHCP server
https://github.com/flan/staticdhcpd

plus add patches ... tbd

# 1. local scanning program

sudo ../../dev/bin/wishful-agent --config config_ap.yaml

