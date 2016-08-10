from master.master import GlobalManager
from upis.upi_rn import *
import logging
import pickle

__author__ = 'pruckebusch'


class GlobalUPIHelper(object):
    """Base class for global helper classes

    Attributes:
        global_mgr (GlobalManager): reference to WiShFUL global manager created by helper
    """
    def __init__(self, group_name):
        self.log = logging.getLogger()
        self.control_engine = control_engine
        self.log.info('Created global manager')
        pass

    def stop(self):
        """Stop the global helper and manager
        """
        self.global_mgr.stop()

    def getNodes(self, nodes):
        """Retrieve all nodes which can be controlled.

        Args:
            nodes (Node): List of expected nodes

        Returns:
             The available nodes.
        """
        # node discovery: wait until all specified nodes are available
        discovered_nodes = self.global_mgr.waitForNodes(nodes)
        expectedNodeIps = [node.getIpAddress() for node in discovered_nodes]
        self.log.info('Expected Wishful nodes: %s' % str(expectedNodeIps))
        nodeRpcIds = [str(node._rpcId) for node in discovered_nodes]
        self.log.info('Discovered Wishful nodes: %s' % str(nodeRpcIds))
        return discovered_nodes

    def startCallbackHandler(self):
        self.global_mgr.startResultCollector()
        pass

    def getRadioPlatforms(self, nodes, execution_time=None, result_callback=None, priority=1):
        """ Gets available NIC on board and type of supported platforms. The information elements used by the UPI_R
        interface, to manage parameters, measurements and radio program, are organized into data structures,
        which provide information on the platform type and radio capabilities.
        When executed, this function return information about available interfaces on node, the name or the identifier
        of the interface and the supported platform type.

        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: a list of NIC_t objects containing the interface identifier and the supported platforms.
        :rtype: list(NIC_t)
        """

        UPIfunc = UPI_R.getRadioPlatforms
        UPIargs = {}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while getting available NICs: %s" % e)
        return -1

    def getRadioInfo(self, nodes, interface, execution_time=None, result_callback=None, priority=1):
        """Gets the radio capabilities of a given network card NIC_t in terms of supported measurement and supported
        parameter and list of supported radio program. The information elements used by the UPI_R interface, to manage
        parameters, measurements and radio program, are organized into data structures, which provide information
        on the platform type and radio capabilities. When executed, this function return information about available
        radio capabilities (measurements and parameters) of each interface (NIC_t) on the available radio programs
        (radio_prg_t) available for transmissions over the radio interface.

        :param param_key: a list in term of a dictionary data type (list of key: value) in which: the key is "PLATFORM" and the value is the platform to get the capabilities
        :type param_key: dict
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The NIC information
        :rtype: radio_info_t

        example:
                >> NIC_info = UPI_R_Helper.getNICInfo()
        """
        UPIfunc = UPI_R.getRadioInfo
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal("An error occurred while getting NIC Info: %s" % e)
            return -1

    def setParameterLowerLayer(self, nodes, interface, param_key_values, execution_time=None, result_callback=None, priority=1):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameter.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in
        the radio programs. This function (re)set the value(s) of the Parameters Radio Capabilities specified in
        the dictionary argument. The list of available parameters is defined as attributes of the UPI_R class,
        you can use the UPI_RN.getNICInfo function to find the platform supported parameters.

        :param param_key: list of parameters and values to set, in term of a dictionary data type (list of key: value) in which key is the desired UPI_R attribute, and value is the value to set. An example of argument dictionary data type is {UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}.
        :type param_key: dictionary(string\:object)
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if the parameter setting call was successfully performed or False otherwise.
        :rtype: bool

        :example:
                >> param_key_values = {UPI_R.CSMA_CW : 15, UPI_R.CSMA_CW_MIN : 15, UPI_R.CSMA_CW_MAX : 15}\n
                >> result = UPI_R_Helper.setParameterLowerLayer(param_key_values)\n
                >> print result\n
                ['True', 'True', 'False']\n
        """
        UPIfunc = UPI_R.setParameterLowerLayer
        UPIargs = {'interface': pickle.dumps(
            interface), 'param_key_values': param_key_values}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setParameterLowerLayer: %s" % e)
            return -1

    def getParameterLowerLayer(self, nodes, interface, param_keys, execution_time=None, result_callback=None, priority=1):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameters.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in the
        radio programs.
        This function get the value(s) of the Parameters Radio Capabilities specified in the dictionary argument.
        The available parameters are defined as attributes of the UPI_R clas, you can use the UPI_R.getNICInfo function
        to find the platform supported parameters.

        :param param_keys: list of parameter keys [UPI_R.CSMA_CW,UPI_R.CSMA_CW_MIN,UPI_R.CSMA_CW_MAX].
        :type param_keys: list(string)
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: a dictionary in which the key is the UPI_R class attribute, and value is the current setting of the attribute. An example of argument dictionary data type is {UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}.
        :rtype: dict(string,object)

        :example:
                >> param_key = [UPI_R.CSMA_CW,UPI_R.CSMA_CW_MIN,UPI_R.CSMA_CW_MAX]\n
                >> result = UPI_R_Helper.getParameterLowerLayer(param_key)\n
                >> print result\n
                {UPI_R.CSMA_CW : 15, UPI_R.CSMA_CW_MIN : 15, UPI_R.CSMA_CW_MAX : 15}\n
        """
        UPIfunc = UPI_R.getParameterLowerLayer
        UPIargs = {'interface': pickle.dumps(
            interface), 'param_keys': param_keys}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getParameterLowerLayer: %s" % e)
            return -1

    def getMonitor(self, nodes, interface, measurement_keys, execution_time=None, result_callback=None, priority=1):
        """ The UPI_R interface is able to get the radio measurements thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the low-level
        measurements. The low-level measurements are continuously monitored by the hardware platform and by the
        radio programs. The measurement capabilities can be used to get information and statistics about the state of
        the physical links or the internal state of the node.
        This function get the value(s) of the Measurements Radio Capabilities specified in the dictionary
        argument. The list of available measurements are defined as attribute of the UPI_R class, you can use the
        UPI_R.getNICInfo function to find the platform supported measurements.

        :param measurement_keys: list of measurement keys (defined as UPI_R attributes for measurements). An example is [UPI_R.NUM_FREEZING_COUNT, UPI_RN.TX_ACTIVITY].
        :type measurement_keys: list
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: a dictionary with the measurement keys and values (the keys are the UPI_R attributes for measurements, the value is the reading of the measurement.  An example is {UPI_RN.NUM_FREEZING_COUNT : 150, UPI_RN.TX_ACTIVITY : 45670}.
        :rtype: dict(string,object)

        :example:
                >> measurement_keys = [UPI_R.NUM_FREEZING_COUNT]\n
                >> result = UPI_R_Helper.getMonitor(measurement_keys)\n
                >> print result\n
                {UPI_R.NUM_FREEZING_COUNT : 150}\n
        """
        UPIfunc = UPI_R.getMonitor
        UPIargs = {'interface': pickle.dumps(
            interface), 'measurement_keys': measurement_keys}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getMonitor: %s" % e)
            return -1

    def getMonitorBounce(self, nodes, interface, measurement_keys, collect_period, report_period, num_iterations, report_callback, execution_time=None, result_callback=None, priority=1):
        """ The UPI_R interface is able to get the radio measurements thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the low-level
        measurements.The low-level measurements are continuously monitored by the hardware platform and by the
        radio programs. The measurement capabilities can be used to get information and statistics about the state of
        the physical links or the internal state of the node.
        This function works similarly to  getMonitor, it gets the value(s) of the Measurements Radio Capabilities
        specified in the measurement_keys list argument, but in cycling mode.
        The function gets the measurements every collect_period and stores them on node memory. Every report_period all
        measurements are reported to the local control program, and this operation is performed a number of times specified by
        num_iterations. A callback function is used to receive the measurements results. The list of available measurements
        are defined as attribute of the UPI_R class, you can use the UPI_R.getNICInfo function to find the platform
        supported measurements.

        :param measurement_keys: list of measurement keys. The keys are UPI_R attributes for measurements.
        :type measurement_keys: list(string)
        :param collect_period: defines the time between two consecutive measurement readings, in microsecond.
        :type collect_period: float
        :param report_period: defines the time between two consecutive reports to the control program, in microseconds.
        :type report_period: float
        :param num_iterations: defines how many times the measurements have to be performed.
        :type num_iterations: float
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: dictionary with measurement keys and as value a list of measurements. The keys are UPI_R attributes for measurements. An example is {UPI_RN.TX_ACTIVITY : [45670,45010]}.
        :rtype: dict(string,list(object))

        :example:
                >> measurement_keys = [UPI_R.BUSY_TIME, UPI_R.TX_ACTIVITY]\n
                >> result = UPI_R_Helper.getMonitorBounce(measurement_keys, 500000, 2000000, 60)\n
                >> print result\n
                {UPI_R.BUSY_TIME : [1505,1230], UPI_R.TX_ACTIVITY: [45670,43560]}\n
        """
        UPIfunc = UPI_R.getMonitorBounce
        UPIargs = {'interface': pickle.dumps(interface), 'measurement_keys': measurement_keys, 'collect_period': collect_period,
                   'report_period': report_period, 'num_iterations': num_iterations, 'report_callback': report_callback}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getMonitorBounce: %s" % e)
            return -1

    def inject(self, nodes, interface, radio_program_name, radio_program_path, radio_program_index, execution_time=None, result_callback=None, priority=1):
        """ Before executing a radio program,  it is required to inject the code into the platform
        Several radio programs can be Injected(copied) into the radio platform simultaneously, but their
        execution is started only after the call of the UPI_R.setActive function, which switches the program state to
        Active. Each radio program injected on a radio platform is associated with an index.

        :param radio_program_name: name of radio program to inject
        :type radio_program_name: string
        :param radio_program_path: path of the radio program to inject
        :type radio_program_path: string
        :param radio_program_index: specifies the platform index in which the radio program must be injected
        :type radio_program_index: int
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if the injection call was successfully performed or False otherwise.
        :rtype: bool

        :example:
                >> result = UPI_R_Helper.inject('CSMA', './radio_program/csma.txt', 2) \n
                >> print result \n
                True \n
        """
        UPIfunc = UPI_R.inject
        UPIargs = {'interface': pickle.dumps(interface), 'radio_program_name': radio_program_name,
                   'radio_program_path': radio_program_path, 'radio_program_index': radio_program_index}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal("An error occurred while executing inject: %s" % e)
            return -1

    def setActive(self, nodes, interface, radio_program_name, radio_program_index, execution_time=None, result_callback=None, priority=1):
        """ After the inject operation, a radio program is locally available on a platform but it is not under execution
        until it is explicitly activated. Only one radio program can be active at a given time.
        When executed, this function stops the current radio program and enables the execution of the radio program
        specified in the parameter radioProgramName and index. The index value must match with the radio program
        specified in the inject operation.

        :param radio_program_name: name of radio program
        :type radio_program_name: string
        :param radio_program_index: specifies the radio program index on platform, it has been set in the injection phase.
        :type radio_program_index: string
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if the activation call was successfully performed or False otherwise.
        :rtype: bool

        :example:
                >> result = UPI_R_Helper.setActive(interface, 'CSMA', 2) \n
                >> print result
                True
        """
        UPIfunc = UPI_R.setActive
        UPIargs = {'interface': pickle.dumps(
            interface), 'radio_program_name': radio_program_name, 'radio_program_index': radio_program_index}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setActive: %s" % e)
            return -1

    def setInactive(self, nodes, interface, radio_program_name, execution_time=None, result_callback=None, priority=1):
        """ When executed, this function stops the current radio program if it maches with the radio program
        specified tin the parameter radioProgramName.

        :param radio_program_name: name of radio program
        :type radio_program_name: string
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if the inactivation call was successfully performed or False otherwise.
        :rtype: bool

        :example:
                >> result = UPI_R_Helper.setInactive('CSMA') \n
                >> print result \n
                True \n
        """
        UPIfunc = UPI_R.setInactive
        UPIargs = {'interface': pickle.dumps(
            interface), 'radio_program_name': radio_program_name}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setInactive: %s" % e)
            return -1

    def getActive(self, nodes, interface, execution_time=None, result_callback=None, priority=1):
        """ Each radio program is associated with a name and an index.
        This function returns the index of the active radio program.


        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: the index of the active radio program.
        :rtype: int

        :example:
                >> result = UPI_R_Helper.getActive() \n
                >> print result \n
                2 \n
        """
        UPIfunc = UPI_R.getActive
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getActive: %s" % e)
            return -1

    def setEdcaParameters(self, nodes, interface, queue_id, aifs, cwmin, cwmax, txop, execution_time=None, result_callback=None, priority=1):
        """ Allows to configure the enhanced distributed channel access parameters (aifs, cwmin, cwmax, txop) on a specific hardware queue of the interface.

        :param int queueId: ID of the hardware QUEUE.
        :param int aifs: arbitrary interframe spacing, value between 0-255.
        :param int cwmin: contention window min, value between 1-1023.
        :param int cwmax: contention window max, value between 1-1023.
        :param int txop: TX output power, value between 0-999.
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if Successfully changed the EDCA parameters, False otherwise
        :rtype: bool
        """
        UPIfunc = UPI_R.setEdcaParameters
        UPIargs = {'interface': pickle.dumps(
            interface), 'queue_id': queue_id, 'aifs': aifs, 'cwmin': cwmin, 'cwmax': cwmax, 'txop': txop}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setEdcaParameters: %s" % e)
            return -1

    def getEdcaParameters(self, nodes, interface, queue_id, execution_time=None, result_callback=None, priority=1):
        """ Allows to obtain the enhanced distributed channel access parameters (aifs, cwmin, cwmax, txop) used on a specific hardware queue for the interface.

        :param int queue_id: ID of the hardware QUEUE.
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: A dictionary containing the EDCA parameters key value pairs {'aifs':0-255, 'cwmin':1-1023, 'cwmax':1-1023, 'txop':0-999}
        :rtype: dict(string,int)
        """
        UPIfunc = UPI_R.getEdcaParameters
        UPIargs = {'interface': pickle.dumps(interface), 'queue_id': queue_id}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getEdcaParameters: %s" % e)
            return -1

    def setPerFlowTxPower(self, nodes, interface, flow, tx_power, execution_time=None, result_callback=None, priority=1):
        """ Allows to set a TX power per flow.

        :param flow: Flow descriptor.
        :type flow: :py:class:`pytc.Filter.FlowDesc`
        :param tx_power: The TX power
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: List[int]
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The return code.
        :rtype: bool
        """
        UPIfunc = UPI_R.setPerFlowTxPower
        UPIargs = {'interface': pickle.dumps(
            interface), 'flow': pickle.dumps(flow), 'tx_power': tx_power}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setPerFlowTxPower: %s" % e)
            return -1

    def cleanPerFlowTxPowerList(self, nodes, interface, execution_time=None, result_callback=None, priority=1):
        """ Removes the TX power settings for all flows.


        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if Successfully cleaned the TX powers for all flows, False otherwise
        :rtype: bool
        """
        UPIfunc = UPI_R.cleanPerFlowTxPowerList
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing cleanPerFlowTxPowerList: %s" % e)
            return -1

    def getPerFlowTxPowerList(self, nodes, interface, execution_time=None, result_callback=None, priority=1):
        """ Returns the TX power set per flow.


        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param interface: name of NIC
        :type interface: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: A dictionary with as keys the flows(pytc.Filter.FlowDesc) and values the TX power.
        :rtype: dict(pytc.Filter.FlowDesc\:int)
        """
        UPIfunc = UPI_R.getPerFlowTxPowerList
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getPerFlowTxPowerList: %s" % e)
            return -1
        return

    def genBacklogged80211L2BcastTraffic(self, nodes, interface, num_packets, ipPayloadSize, phyBroadcastMbps, ipdst, ipsrc, use_tcpreplay, execution_time=None, result_callback=None, priority=1):
        """ Sends as fast as possible L2 broadcast traffic. Note that all transmitted packets are identical.

        :param interface: name of NIC
        :type interface: string
        :param num_packets: number of packets to be sent
        :type num_packets: int
        :param ipPayloadSize: size of IP packet payload in bytes
        :type ipPayloadSize: int
        :param phyBroadcastMbps: rate of broadcast traffic in Mbps
        :type phyBroadcastMbps: int
        :param ipdst: destination IP address
        :type ipdst: string
        :param ipsrc: source IP address
        :type ipsrc: string
        :param use_tcpreplay: whether TCP replay should be used or not
        :type use_tcpreplay: bool
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The achieved transmit frame rate.
        :rtype: float
        """
        UPIfunc = UPI_R.genBacklogged80211L2BcastTraffic
        UPIargs = {'interface': pickle.dumps(
            interface), 'num_packets': num_packets, 'ipPayloadSize': ipPayloadSize, 'phyBroadcastMbps': use_tcpreplay}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing genBacklogged80211L2BcastTraffic: %s" % e)
            return -1
        return

    def gen80211L2LinkProbing(self, nodes, interface, num_packets, pinter, ipdst, ipsrc, execution_time=None, result_callback=None, priority=1):
        """ Sends link probing packets.

        :param interface: name of NIC
        :type interface: string
        :param int num_packets: number of packets to be sent
        :param int ipPayloadSize: size of IP packet payload in bytes
        :param int phyBroadcastMbps: rate of broadcast traffic in Mbps
        :param string ipdst: destination IP address
        :param string ipsrc: source IP address
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """

        UPIfunc = UPI_R.gen80211L2LinkProbing
        UPIargs = {'interface': pickle.dumps(
            interface), 'num_packets': num_packets, 'pinter': pinter, 'ipdst': ipdst, 'ipsrc': ipsrc}
        try:
            self.global_mgr.runAt(nodes, UPIfunc, UPIargs,
                                  execution_time, result_callback, priority)
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing gen80211L2LinkProbing: %s" % e)
        pass

    def sniff80211L2LinkProbing(self, nodes, interface, ipdst, ipsrc, sniff_timeout, execution_time=None, result_callback=None, priority=1):
        """ Sends link probing packets.

        :param interface: name of NIC
        :type interface: string
        :param num_packets: number of packets to be sniffed
        :type num_packets: int
        :param ipPayloadSize: size of IP packet payload in bytes
        :type ipPayloadSize: int
        :param phyBroadcastMbps: rate of broadcast traffic in Mbps
        :type phyBroadcastMbps: int
        :param ipdst: destination IP address
        :type ipdst: string
        :param ipsrc: source IP address
        :type ipsrc: string
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The number of received probing packets.
        :rtype: int
        """
        UPIfunc = UPI_RN.sniff80211L2LinkProbing
        UPIargs = {'interface': pickle.dumps(
            interface), 'ipdst': ipdst, 'ipsrc': ipsrc, 'sniff_timeout': sniff_timeout}

        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing sniff80211L2LinkProbing: %s" % e)
        return None

    def getHwAddr(self, nodes, interface, execution_time=None, result_callback=None, priority=1):
        """ Returns the Hardware address of the interface.

        :param interface: name of NIC
        :type interface: string
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The hardware address.
        :rtype: string
        """
        UPIfunc = UPI_R.getHwAddr
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getHwAddr: %s" % e)
            return -1
        return

    def setRfChannel(self, nodes, interface, channel, execution_time=None, result_callback=None, priority=1):
        """ Sets the RF channel on the specified interface.

        :param interface: name of NIC
        :type interface: string
        :param channel: the channel number.
        :type channel: int
        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: True if Successfully changed the RF channel, False otherwise
        :rtype: bool
        """
        UPIfunc = UPI_R.setRfChannel
        UPIargs = {'interface': pickle.dumps(interface), 'channel': channel}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setRfChannel: %s" % e)
            return -1
        return

    # The UPI_N_Helper - UPI helper for network control at device level.

    # Generic functions for configuration

    def getNetworkInfo(self, nodes, interface, execution_time=None, result_callback=None, priority=1, on_the_fly_install=False):
        """This function returns the available netowrk parameters, measurements and events in a network_info_t object.

        Args:
            nodes (TYPE):  A list of nodes on which the function must be executed.
            interface (TYPE): name of NIC
            execution_time (unix_time, optional): absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
            result_callback (Callable, optional): the callback used for returning results of time scheduled function execution.
            priority (int, optional): as in UNIX, lower priority numbers mean higher priority
            on_the_fly_install (bool, optional): flag indicates whether UPIfunc is a custom function body

        Returns:
            network_info_t: the available netowrk parameters, measurements and events in a network_info_t object
        """
        UPIfunc = UPI_N.getNetworkInfo
        UPIargs = {'interface': pickle.dumps(interface)}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while getting Network Info: %s" % e)
            return -1

    def setParameterHigherLayer(self, nodes, interface, param_key_values, execution_time=None, result_callback=None, priority=1, on_the_fly_install=False):
        """The UPI_N interface is able to configure the network stack behavior. The list of available parameters is defined as attributes of the UPI_N class.

        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param interface: name of NIC
        :type interface: string
        :param param_key_values: list of parameters and values to set, in term of a dictionary data type (list of key: value) in which key is the desired UPI_R attribute, and value is the value to set. An example of argument dictionary data type is {UPI_N.RPL_DIO_INTERVAL_MIN : 15, UPI_N.RPL_DIO_INTERVAL_DOUBLINGS : 15}.
        :type param_key_values: dictionary(string\:object)
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: Dictionary with parameter key, error tuples.
        :rtype: dict

        :example:
                >> param_key_values = {UPI_N.RPL_DIO_INTERVAL_MIN : 15, UPI_N.RPL_DO_INTERVAL_DOUBLINGS : 15}\n
                >> result = UPI_N_Helper.setParameterHigherLayer(param_key_values)\n
                >> print result\n
                {'RPL_DIO_INTERVAL_MIN' : 15, 'RPL_DIO_INTERVAL_DOUBLINGS' : 15}\n
        """
        UPIfunc = UPI_N.setParameterHigherLayer
        UPIargs = {'interface': pickle.dumps(
            interface), 'param_key_values': param_key_values}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing setParameterHigherLayer: %s" % e)
            return -1

    def getParameterHigherLayer(self, nodes, interface, param_keys, execution_time=None, result_callback=None, priority=1):
    	""" The UPI_N interface is able to monitor the network stack.
        This function get the value(s) of the monitored parameters specified in the list argument.
        The available parameters are defined as attributes of the UPI_N class.

        :param nodes: A list of nodes on which the function must be executed.
        :type nodes: list
        :param interface: name of NIC
        :type interface: string
        :param param_keys: list of parameter keys [UPI_N.RPL_DIO_INTERVAL_MIN,UPI_N.RPL_DO_INTERVAL_DOUBLINGS].
        :type param_keys: list(string)
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: a dictionary in which the key is the UPI_N class attribute, and value is the current setting of the attribute. An example of argument dictionary data type is {UPI_N.RPL_DIO_INTERVAL_MIN : 15, UPI_N.RPL_DO_INTERVAL_DOUBLINGS : 15}.
        :rtype: dict(string,object)

        :example:
                >> param_key = [UPI_N.RPL_DIO_INTERVAL_MIN,UPI_N.RPL_DO_INTERVAL_DOUBLINGS]\n
                >> result = UPI_R_Helper.getParameterHigherLayer(param_key)\n
                >> print result\n
                {'RPL_DIO_INTERVAL_MIN' : 15, 'RPL_DO_INTERVAL_DOUBLINGS' : 15}\n
        """
        UPIfunc = UPI_N.getParameterHigherLayer
        UPIargs = {'interface': pickle.dumps(
            interface), 'param_keys': param_keys}
        try:
            retValue = self.global_mgr.runAt(
                nodes, UPIfunc, UPIargs, execution_time, result_callback, priority)
            cleanRetValue = {}
            for key in retValue.keys():
                cleanRetValue[key] = pickle.loads(retValue[key])
            return cleanRetValue
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing getParameterHigherLayer: %s" % e)
            return -1
