# WiSHFUL Expert

## Package Installation
First, you have to install the EXPERT package.

- cd expert/
- pip install .


## Importing EXPERT package
After package installation, you may import EXPERT in your source code using command:
	“import expert” 
Now, you are ready to call the EXPERT method call. The second argument is the border router. The third argument is the percentage of nodes that are considered mobile in your experiment (i.e., this cannot be measured via the statistics offered by WiSHFUL; in a static network you may leave this ‘0’).
	expert.implementation_exp_algo(controller, nodes[0], 0)


## To Run the experiments:
- Start the agent:
python agent.py --config expert/agent_nordc_csma_ipv6.yaml 
- Start the controller:
 python example/controller.py --config config/localhost/global_cp_config.yaml


