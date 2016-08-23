# 1. Run control program and all modules on local node
wishful-agent --config ./config_local.yaml


# 2a. Run control program in master node:
wishful-agent --config ./config_master.yaml
# 2a. Run modules in slave node:
wishful-agent --config ./config_slave.yaml


# For debugging mode run with -v option
