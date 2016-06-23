"""Base class for all local helper classes
"""

import logging

__author__ = 'pruckebusch'

#  """
#  Base class for all local helper classes
#  """
#  class LocalHelper(object):
#
#  def __init__(self,platform_id,platform_type,control_engine):
#  self.log = logging.getLogger()
#  self.interface = radio_platform_t(platform_id,platform_type)
#  self.control_engine = control_engine
#  cm = CM_DOT80211_LINUX
#  if platform == 'WMP':
#  cm = CM_WMP_LINUX
#  elif platform == 'CONTIKI':
#  cm = CM_DOT802154_CONTIKI
#  self.control_engine = LocalManager(cm)
#  pass


class LocalUPIHelper():

    def __init__(self, interface, control_engine):
        """Creates a LocalUPIHelper
        Args:
            interface (str): the interface ID on which the UPI functions must be executed (wlan0,lowpan0,..)
            control_engine (LocalController): reference to the the local control engine

        Example:
            LocalUPIHelper('lowpan0',control_engine)s
        """

        self.log = logging.getLogger()
        self.interface = interface
        self.control_engine = control_engine
        pass

    @staticmethod
    def getRadioPlatforms(control_engine, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Gets available radio platforms and type of supported platforms. The information elements used by the UPI_R
        interface, to manage parameters, measurements and radio program, are organized into data structures,
        which provide information on the platform type and radio capabilities.
        When executed, this function return information about available interfaces on node, the name or the identifier
        of the interface and the supported platform type.

        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: a list of radio_platform_t objects containing the interface identifier and the supported platforms.
        :rtype: list(radio_platform_t)
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return control_engine.radio.get_radio_platforms()
        if execution_delay is not None:
            control_engine.callback(result_callback).delay(execution_delay).radio.get_radio_platforms()
        elif execution_time is not None:
            control_engine.callback(result_callback).exec_time(execution_time).radio.get_radio_platforms()
        else:
            control_engine.callback(result_callback).blocking(False).radio.get_radio_platforms()

    def getRadioInfo(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """Gets the radio capabilities of a given radio platform in terms of supported measurement and supported
        parameter and list of supported radio program. The information elements used by the UPI_R interface, to manage
        parameters, measurements and radio program, are organized into data structures, which provide information
        on the platform type and radio capabilities. When executed, this function return information about available
        radio capabilities (measurements and parameters) of each interface (NIC_t) on the available radio programs
        (radio_prg_t) available for transmissions over the radio interface.

        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: The radio platform information
        :rtype: radio_info_t

        example:
                >> NIC_info = UPI_R_Helper.getRadioInfo()
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_radio_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_radio_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_radio_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_radio_info()

    def setParameterLowerLayer(self, param_key_values, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameter.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in
        the radio programs. This function (re)set the value(s) of the Parameters Radio Capabilities specified in
        the dictionary argument. The list of available parameters is defined as attributes of the UPI_R class,
        you can use the UPI_RN.getNICInfo function to find the platform supported parameters.

        :param param_key: list of parameters and values to set, in term of a dictionary data type (list of key: value) in which key is the desired UPI_R attribute, and value is the value to set. An example of argument dictionary data type is {UPI_RN.CSMA_CW : 15, UPI_RN.CSMA_CW_MIN : 15, UPI_RN.CSMA_CW_MAX : 15}.
        :type param_key: dictionary(string\:object)	
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).set_parameters(param_key_values)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).set_parameters(param_key_values)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).set_parameters(param_key_values)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).set_parameters(param_key_values)

    def getParameterLowerLayer(self, param_keys, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ The UPI_R interface is able to configure the radio behavior thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the parameters.
        Parameters correspond to the configuration registers of the hardware platform and to the variables used in the
        radio programs.
        This function get the value(s) of the Parameters Radio Capabilities specified in the dictionary argument.
        The available parameters are defined as attributes of the UPI_R clas, you can use the UPI_R.getNICInfo function
        to find the platform supported parameters.

        :param param_keys: list of parameter keys [UPI_R.CSMA_CW,UPI_R.CSMA_CW_MIN,UPI_R.CSMA_CW_MAX].
        :type param_keys: list(string)
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_parameters(param_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_parameters(param_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_parameters(param_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_parameters(param_keys)

    def getMonitor(self, measurement_keys, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ The UPI_R interface is able to get the radio measurements thanks to the abstraction of the hardware
        platform and radio programs in terms of Radio Capabilities. A subset of radio capabilities are the low-level
        measurements. The low-level measurements are continuously monitored by the hardware platform and by the
        radio programs. The measurement capabilities can be used to get information and statistics about the state of
        the physical links or the internal state of the node.
        This function get the value(s) of the Measurements Radio Capabilities specified in the dictionary
        argument. The list of available measurements are defined as attribute of the UPI_R class, you can use the
        UPI_R.getNICInfo function to find the platform supported measurements.

        :param measurement_keys: list of measurement keys (defined as UPI_R attributes for measurements). An example is [UPI_R.NUM_FREEZING_COUNT, UPI_RN.TX_ACTIVITY].

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getMonitorBounce(self, measurement_keys, collect_period, report_period, num_iterations, report_callback, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements_periodic(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def setActive(self, radio_program_name, radio_program_index, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ After the inject operation, a radio program is locally available on a platform but it is not under execution
        until it is explicitly activated. Only one radio program can be active at a given time.
        When executed, this function stops the current radio program and enables the execution of the radio program
        specified in the parameter radioProgramName and index. The index value must match with the radio program
        specified in the inject operation.

        :param radio_program_name: name of radio program
        :type radio_program_name: string
        :param radio_program_index: specifies the radio program index on platform, it has been set in the injection phase.
        :type radio_program_index: string
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def setInactive(self, radio_program_name, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ When executed, this function stops the current radio program if it maches with the radio program
        specified tin the parameter radioProgramName.

        :param radio_program_name: name of radio program
        :type radio_program_name: string
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getActive(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Each radio program is associated with a name and an index.
        This function returns the index of the active radio program.


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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def setEdcaParameters(self, queue_id, aifs, cwmin, cwmax, txop, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Allows to configure the enhanced distributed channel access parameters (aifs, cwmin, cwmax, txop) on a specific hardware queue of the interface.

        :param queueId: ID of the hardware QUEUE.
        :type queueId: int
        :param aifs: arbitrary interframe spacing, value between 0-255.
        :type aifs: int
        :param cwmin: contention window min, value between 1-1023.
        :type cwmin: int
        :param cwmax: contention window max, value between 1-1023.
        :type cwmax: int
        :param txop: TX output power, value between 0-999.
        :type txop: int
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getEdcaParameters(self, queue_id, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Allows to obtain the enhanced distributed channel access parameters (aifs, cwmin, cwmax, txop) used on a specific hardware queue for the interface.

        :param queue_id: ID of the hardware QUEUE.
        :type queue_id: int
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def setPerFlowTxPower(self, flow, tx_power, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Set TX power for flow identified with 5-tuple.

        :param flow: Flow descriptor.
        :type flow: :py:class:`pytc.Filter.FlowDesc`
        :param tx_power: The TX power
        :type tx_power: int
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def cleanPerFlowTxPowerList(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Removes the TX power settings for all flows.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getPerFlowTxPowerList(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Get entire flow TX power table for speficic wireless interface.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def genBacklogged80211L2BcastTraffic(self, num_packets, ipPayloadSize, phyBroadcastMbps, ipdst, ipsrc, use_tcpreplay, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Sends as fast as possible L2 broadcast traffic. Note that all transmitted packets are identical.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def gen80211L2LinkProbing(self, num_packets, pinter, ipdst, ipsrc, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Sends link probing packets.

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
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """

        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def sniff80211L2LinkProbing(self, ipdst, ipsrc, sniff_timeout, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Sends link probing packets.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getHwAddr(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Returns the Hardware address of the interface.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    def setRfChannel(self, channel, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Sets the RF channel on the specified interface.

        :param channel: the channel number.
        :type channel: int
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.radio.iface(self.interface).get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(False).radio.iface(self.interface).get_measurements(measurement_keys)

    # The UPI_N_Helper - UPI helper for network control at device level.

    # Generic functions for configuration

    def getNetworkInfo(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
    	"""This function returns the available network parameters, measurements and events in a network_info_t object.

        Args:
            interface (TYPE): name of NIC
            execution_time (unix_time, optional): absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
            result_callback (Callable, optional): the callback used for returning results of time scheduled function execution.
            priority (int, optional): as in UNIX, lower priority numbers mean higher priority
            on_the_fly_install (bool, optional): flag indicates whether UPIfunc is a custom function body

        Returns:
            network_info_t: the available netowrk parameters, measurements and events in a network_info_t object
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def setParameterHigherLayer(self, param_key_values, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ The UPI_N interface is able to configure the network stack behavior. The list of available parameters is defined as attributes of the UPI_N class.

        :param param_key: list of parameters and values to set, in term of a dictionary data type (list of key: value) in which key is the desired UPI_R attribute, and value is the value to set. An example of argument dictionary data type is {UPI_N.RPL_DIO_INTERVAL_MIN : 15, UPI_N.RPL_DIO_INTERVAL_DOUBLINGS : 15}.
        :type param_key: dictionary(string\:object)
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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def getParameterHigherLayer(self, param_keys, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ The UPI_N interface is able to monitor the network stack.
        This function get the value(s) of the monitored parameters specified in the list argument.
        The available parameters are defined as attributes of the UPI_N class.

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
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def defineEvent(self, event_keys, event_callback, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Define an event listener for push-based monitoring. The event callback is called each time the event is posted. 

        :param event_key: Unique name idenifying the event.
        :type event_key: string
        :param event_callback: Callback function that is executed when the event is pushed.
        :type event_callback: function
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
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def startIperfServer(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Starts an iPerf Server.

        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: throughput achieved by server
        :rtype: string
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def startIperfClient(self, server_ipaddr, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Starts an iPerf Client

        :param server_ipaddr: The servers IP address.
        :type server_ipaddr: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: throughput achieved by client
        :rtype: string
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def startPing(self, src_ipaddr, dst_ipaddr, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Starts ping between src and dst.

        :param src_ipaddr: Source IP address.
        :type src_ipaddr: string
        :param dst_ipaddr: Destination IO address.
        :type dst_ipaddr: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: dict containing avgRtt, maxRtt and percentage of lost packet
        :rtype: dict
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def setProfile(self, interface, profile, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Set emulation profile in given network interface

        :param interface: name of NIC on which the profile needs to be applied
        :type interface: string
        :param profile: Python Traffic Control profile
        :type profile: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def updateProfile(self, interface, profile, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Update emulation profile in given network interface

        :param interface: name of NIC on which the profile needs to be applied
        :type interface: string
        :param profile: Python Traffic Control profile
        :type profile: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def removeProfile(self, interface, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Remove emulation profile from given network interface.

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
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def setPerLinkProfile(self, interface, neighbor_ipaddr, profile, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Set emulation profile in network interface for given link identified with destination IP addressess

        :param interface: name of NIC on which the profile needs to be applied
        :type interface: string
        :param neighbor_ipaddr: The IP address of the neighbor node
        :type neighbor_ipaddr: string
        :param profile: Python Traffic Control profile
        :type profile: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def updatePerLinkProfile(self, interface, neighbor_ipaddr, profile, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Update emulation profile in network interface for given link identified with MAC addressess

        :param interface: name of NIC on which the profile needs to be applied
        :type interface: string
        :param neighbor_ipaddr: The IP address of the neighbor node
        :type neighbor_ipaddr: string
        :param profile: Python Traffic Control profile
        :type profile: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def removePerLinkProfile(self, interface, neighbor_ipaddr, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Remove emulation profile from network interface for given link identified with MAC addressess

        :param interface: name of NIC on which the profile needs to be applied.
        :type interface: string
        :param neighbor_ipaddr: The IP address of the neighbor node.
        :type neighbor_ipaddr: string 
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def installEgressScheduler(self, interface, scheduler, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Install Egress Scheduler in given network interface.

        :param interface: name of NIC on which the profile needs to be applied.
        :type interface: string
        :param scheduler: Traffic Scheduler
        :type scheduler: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def removeEgressScheduler(self, interface, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Remove Egress Scheduler from network interface

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
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def clearIpTables(self, table, chain, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Clear all iptables from all entries

        :param table: name of iptable where to insert new rule
        :type table: string
        :param chain: name of chain inside given table
        :type chain: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def getIpTable(self, table, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Get specific iptable and its entires

        :param table: name of iptable where to insert new rule
        :type table: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: description iptable
        :rtype: string
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def setMarking(self, flow_descriptor, mark_id, table, chain, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Add iptable rule for marking all packets belonging to flow identified with given 5-tuple

        :param flow_descriptor: definition of flow, based on 5-tuple
        :type flow_descriptor: object
        :param mark_id: value of mark id
        :type mark_id: int
        :param table: name of iptable where to insert new rule
        :type table: string
        :param chain: name of chain inside given table
        :type chain: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def delMarking(self, flow_descriptor, mark_id, table, chain, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Remove rule used to mark given flow from iptable

        :param flow_descriptor: definition of flow, based on 5-tuple
        :type flow_descriptor: object
        :param mark_id: value of mark id
        :type mark_id: int
        :param table: name of iptable where to insert new rule
        :type table: string
        :param chain: name of chain inside given table
        :type chain: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def setTos(self, flow_descriptor, type_of_service, table, chain, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Add iptable rule for setting TOS (Type-of-Service) field in all packets belonging to flow identified with given 5-tuple

        :param flow_descriptor: definition of flow, based on 5-tuple
        :type flow_descriptor: object
        :param type_of_service: value of TOS
        :type type_of_service: int
        :param table: name of iptable where to insert new rule
        :type table: string
        :param chain: name of chain inside given table
        :type chain: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def delTos(self, flow_descriptor, type_of_service, table, chain, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Remove rule used to setting TOS field from iptable

        :param flow_descriptor: definition of flow, based on 5-tuple
        :type flow_descriptor: object
        :param type_of_service: value of TOS
        :type type_of_service: int
        :param table: name of iptable where to insert new rule
        :type table: string
        :param chain: name of chain inside given table
        :type chain: string
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()

    def installApplication(self, application, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Install application in node. Possible applications are IperfClient and IperfServer.

        :param application: Application object (IperfClient or IperfServer App)
        :type execution_time: object
        :param execution_time: absolute time since epoch (2 element list of second & microsecond) when the function will be executed or None for immediate execution
        :type execution_time: list(int,int)
        :param result_callback: the callback used for returning results of time scheduled function execution.
        :type result_callback: function
        :param priority: as in UNIX, lower priority numbers mean higher priority
        :type priority: int
        :param on_the_fly_install: flag indicates whether UPIfunc is a custom function body
        :type on_the_fly_install: bool
        :returns: message with throughput achieved by application
        :rtype: string
        """
        if execution_time is None and execution_delay is None and blocking is True:
            # blocking call
            return self.control_engine.net.get_network_info()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(False).net.get_network_info()
