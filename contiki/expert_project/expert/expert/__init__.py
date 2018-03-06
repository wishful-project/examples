"""
EXPERT - Evaluation of Routing adapTation scenarios for wireless networks . The EXPERT scheme intends to optimize the performance of the routing algorithms by taking into consideration real-time network measurements (e.g., density, symmetry, mobility, application requirements). In particular, the algorithm monitors several network measurements constantly and switches to a different link estimator for routing whenever this is needed. EXPERT is an open and modular network routing optimizer that could eventually serve as a black box inter-operating with the underlying network infrastructure.
"""

__author__ = "Dimitris Katris"
__copyright__ = "Copyright (c) 2017, Intellia"
__version__ = "0.1.0"
__email__ = "dkatris@intellia.gr"



def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def algorithm(number_list):
    mean_number = mean(number_list)
    dif_list = [abs(element-mean_number) for element in number_list]
    result = sum(dif_list) / (len(dif_list) * mean_number)
    if result > 1 : return 1
    return sum(dif_list) / (len(dif_list) * mean_number)


def calculate_density(controller, node):
    number_neighbours = 0
    radio_platforms = controller.blocking(True).node(node).radio.iface("lowpan0").get_radio_platforms()
    for i in range(1, len(radio_platforms)):
        val = controller.blocking(True).node(node).net.iface(radio_platforms[i]).get_measurements_net(['nd6_num_neighbors'])
        number_neighbours += val['nd6_num_neighbors']
    density = number_neighbours / (len(radio_platforms) * (len(radio_platforms)-1))
    print("Density ~> ", density)
    return density


def calculate_tx_deviation(controller, node):
    tx_power_list = []
    radio_platforms = controller.blocking(True).node(node).radio.iface("lowpan0").get_radio_platforms()
    for rp in radio_platforms:
        val = controller.blocking(True).node(node).radio.iface(rp).get_parameters(['IEEE802154_phyTXPower'])
        tx_power_list.append(val['IEEE802154_phyTXPower'])
    tx_deviation = algorithm(tx_power_list)
    print("TX deviation ~> ", tx_deviation)
    return tx_deviation


def calculate_interval(controller, node):
    interval_list = []
    radio_platforms = controller.blocking(True).node(node).radio.iface("lowpan0").get_radio_platforms()
    for rp in radio_platforms:
        val = controller.blocking(True).node(node).net.iface(rp).get_parameters_net(['app_send_interval'])
        interval_list.append(val['app_send_interval'])
    interval_deviation = algorithm(interval_list)
    mean_interval = mean(interval_list)
    interval = 1 - mean_interval/128.0
    print("Interval ~> ", interval)
    return interval



def implementation_exp_algo(controller, node, mobility=0):
    objective_function = exp_algo(controller, node, mobility)
    print("Setting Objective function ~>", objective_function)
    radio_platforms = controller.blocking(True).node(node).radio.iface("lowpan0").get_radio_platforms()
    for rp in radio_platforms:
        ret = controller.blocking(True).node(node).net.iface(rp).set_parameters_net({'rpl_objective_function': objective_function})
        print("{}: {}".format(rp, ret))


def calculate_mobility(controller, node, mobility=0):
    print("Mobility ~> ", mobility)
    return 0


def exp_algo(controller, node, mobility=0):
    density = calculate_density(controller, node)
    tx_deviation = calculate_tx_deviation(controller, node)
    interval = calculate_interval(controller, node)
    mobility = calculate_mobility(controller, node, mobility)
    value = 0.25 * density + 0.25 * (1-tx_deviation) + 0.25 * interval + 0.25 * (1-mobility)
    if value >= 0.5:
        return 1
    return 0
