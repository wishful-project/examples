# Install node red:

    curl -sL https://deb.nodesource.com/setup_0.10 | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo apt-get install -y build-essential
    sudo npm install -g --unsafe-perm node-red

# Install additional nodes:

    cd $HOME/.node-red
    sudo npm install node-red-node-smooth
    sudo npm install zmq
    sudo npm install reddec/node-red-contrib-zmq

# Run example flow graph - moving average filter:

    cd ./examples/node_red
    node-red my_filter.json

# Run wishful-agent with master config:

    wishful-agent --config ./config_master.yaml

# Run wishful-agent with slave config:

    wishful-agent --config ./config_slave.yaml

# For debugging mode run with -v option
