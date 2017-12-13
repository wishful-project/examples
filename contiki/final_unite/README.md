# Unite Extention

## Features
:grey_exclamation: proactively identification of future network abnormalities

:boom: nodes, locally, securing the QoS by taking short term desicions

:dart: long term desicions are taken by the global controller keeping QoS high

:ballot_box_with_check: high quality services on top of the WishFul solution


## How-To
Experimenters who want to integrate UNITE Extention and taste high quality services on top of the Wishful solution, 
while keeping the QoS at high levels, need to follow *Getting Started* section for installing all the extension's dependencies.
Then, in the global controller program, should instruct all the nodes to execute the experimenter's desired code, which must be flashed to all nodes.



## Getting Started

##### 1. Install ubuntu package python3-tk 

##### 2. Install pip requirements
```
pip install -r ./libunite/requirements.txt
```
##### 3. Configure the controller node and the agents based on wishful docs
##### 4. Execute your agents
```../hierarchical_control/wishful_simple_agent --config ../hierarchical_control/agent_config.yaml```
##### 5. Execute the global controller
```./unite_simple_controller --config ./controller_config.yaml```
