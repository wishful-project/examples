"""Base class for all local helper classes
"""

import logging
import wishful_agent
import wishful_upis as upis
import yaml

__author__ = 'pruckebusch'



class LocalUPIHelper():

    def __init__(self,config_file_path):
        """Creates a LocalUPIHelper
        Args:
            interface (str): the interface ID on which the UPI functions must be executed (wlan0,lowpan0,..)
            control_engine (LocalController): reference to the the local control engine

        Example:
            LocalUPIHelper('lowpan0',control_engine)s
        """
        self.log = logging.getLogger('wishful_agent.main')
        self.agent = wishful_agent.Agent(local=True)
        self.control_engine = agent.get_local_controller()
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
        self.agent.load_config(config)
        self.agent.run()
        pass

    def getRadioPlatforms(self, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.radio.get_radio_platforms()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.get_radio_platforms()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.get_radio_platforms()
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.get_radio_platforms()

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
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_radio_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_radio_info()
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_radio_info()

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
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).set_parameters(param_key_values)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).set_parameters(param_key_values)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).set_parameters(param_key_values)

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
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_parameters(param_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_parameters(param_keys)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_parameters(param_keys)

    def getMonitorLowerLayer(self, measurement_keys, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_measurements(measurement_keys)

    def getMonitorBounceLowerLayer(self, measurement_keys, collect_period, report_period, num_iterations, report_callback, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.radio.iface(self.interface).get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)

    def setActive(self, radio_program_name, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.radio.iface(self.interface).activate_radio_program(radio_program_name)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).activate_radio_program(radio_program_name)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).activate_radio_program(radio_program_name)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).activate_radio_program(radio_program_name)

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
            return self.control_engine.radio.iface(self.interface).deactivate_radio_program(radio_program_name)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).deactivate_radio_program(radio_program_name)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).deactivate_radio_program(radio_program_name)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).deactivate_radio_program(radio_program_name)

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
            return self.control_engine.radio.iface(self.interface).get_running_radio_program()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_running_radio_program()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_running_radio_program()
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_running_radio_program()

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
            return self.control_engine.radio.iface(self.interface).get_hwaddr()
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).get_hwaddr()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).get_hwaddr()
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).get_hwaddr()

    def setRfChannel(self, freq_Hz, bandwidth, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.radio.iface(self.interface).set_rxchannel(freq_Hz, bandwidth)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).set_rxchannel(freq_Hz, bandwidth)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).set_rxchannel(freq_Hz, bandwidth)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).set_rxchannel(freq_Hz, bandwidth)

    def defineEventLowerLayer(self, event_keys, event_callback, event_duration, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.radio.iface(self.interface).subscribe_events(event_keys, event_callback, event_duration)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).radio.iface(self.interface).subscribe_events(event_keys, event_callback, event_duration)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).radio.iface(self.interface).subscribe_events(event_keys, event_callback, event_duration)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).radio.iface(self.interface).subscribe_events(event_keys, event_callback, event_duration)

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
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.get_network_info()
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.get_network_info()
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.get_network_info()

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
            return self.control_engine.net.set_parameters(param_key_values)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.set_parameters(param_key_values)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.set_parameters(param_key_values)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.set_parameters(param_key_values)

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
            return self.control_engine.net.get_parameters(param_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.get_parameters(param_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.get_parameters(param_keys)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.get_parameters(param_keys)

    def defineEventHigherLayer(self, event_keys, event_callback, event_duration, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.net.subscribe_events(event_keys, event_callback, event_duration)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.subscribe_events(event_keys, event_callback, event_duration)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.subscribe_events(event_keys, event_callback, event_duration)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.subscribe_events(event_keys, event_callback, event_duration)

    def startApplication(self, application_id, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Start application in node. Possible applications are IperfClient and IperfServer.

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
            return self.control_engine.net.start_application(application_id)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.start_application(application_id)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.start_application(application_id)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.start_application(application_id)

    def stopApplication(self, application_id, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
        """ Stop application in node. Possible applications are IperfClient and IperfServer.

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
            return self.control_engine.net.stop_application(application_id)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.stop_application(application_id)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.stop_application(application_id)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.stop_application(application_id)

    def getMonitorHigherLayer(self, measurement_keys, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.net.get_measurements(measurement_keys)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.get_measurements(measurement_keys)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.get_measurements(measurement_keys)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.get_measurements(measurement_keys)

    def getMonitorBounceHigherLayer(self, measurement_keys, collect_period, report_period, num_iterations, report_callback, execution_delay=None, execution_time=None, result_callback=None, blocking=True):
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
            return self.control_engine.net.get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        if execution_delay is not None:
            self.control_engine.callback(result_callback).delay(
                execution_delay).net.get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        elif execution_time is not None:
            self.control_engine.callback(result_callback).exec_time(
                execution_time).net.get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)
        else:
            self.control_engine.callback(result_callback).blocking(
                False).net.get_measurements_periodic(measurement_keys, collect_period, report_period, num_iterations, report_callback)