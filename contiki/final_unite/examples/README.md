# Unite Example

## Simple example
This is a simple example of UNITE extension.
For the purpose of the example, we enable the default unicast application, provided by the Wishful platform.
This example is a proof of concept. By executing it, it is observable that the UNITE modules are capable of identifying QoS violation events,
and force the nodes to change their configuration, appropriately.


## How-to

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
