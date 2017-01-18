__author__ = 'domenico'

throughput_results_node0 = []
delta_results_node0 = []
def collect_traffic_logging_messages_node0(group, node, data):
    log.debug('receives data msg at %s - %s' % (str(node.ip), str(data) ))
    throughput_results_node0.append(data['throughput'])
    delta_results_node0.append(data['delta'])

throughput_results_node1 = []
delta_results_node1 = []
def collect_traffic_logging_messages_node1(group, node, data):
    log.debug('receives data msg at %s - %s' % (str(node.ip), str(data) ))
    throughput_results_node1.append(data['throughput'])
    delta_results_node1.append(data['delta'])
