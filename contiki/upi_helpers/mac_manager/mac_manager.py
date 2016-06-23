"""This module implements basic abstractions for MAC configuration and control on sensor nodes.
"""
import abc
import logging
from common.constants import *
from upis.upi_rn import UPI_R
import pickle


class MACManager(object):
    """Abstract MAC manager class listing all the mandatory MACManager functions.
    These functions must be implemented by the subclassess.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_macconfiguration(self, parameter_key_values):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary argument containing parameter key-value pairs.

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        return -1

    @abc.abstractmethod
    def read_macconfiguration(self, parameter_keys):
        """Reads the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys as arguments.

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        return -1

    @abc.abstractmethod
    def monitor_mac(self, measurement_keys):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.

        Args:
            measurement_keys (List[str]): a list of measurement keys as arguments.

        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        return -1

    @abc.abstractmethod
    def monitor_mac_periodic(self, measurement_keys, collect_period, collect_iterations, report_period, report_callback):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.

        Args:
            measurement_keys (List[str]): a list of measurement keys as arguments
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return -1

    @abc.abstractmethod
    def monitor_mac_async(self, event_keys, event_callback):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.

        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return -1

    @abc.abstractmethod
    def activate_mac(self, name):
        """Activate a MAC radio program.

        Args:
            name (str): Name of the MAC radioprogram (CSMA, TDMA, TSCH).

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        return -1

    @abc.abstractmethod
    def get_radioinfo(self):
        """Returns a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.

        Returns:
            UPI_R.radio_info_t: a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.
        """
        return -1

    @abc.abstractmethod
    def get_radioplatforms(self):
        """Returns a list of radio_platform_t objects containing interface name and platform name.

        Returns:
            List[UPI_R.radio_platform_t]: a list of radio_platform_t objects containing interface name and platform name.
        """
        return -1

    @abc.abstractmethod
    def get_macaddress(self):
        """Returns the macaddress of the interface.

        Returns:
            int: the macaddress
        """
        return -1


class LocalMACManager(MACManager):
    """Local MAC manager class implementing all the mandatory MACManager functions.
    This class can be extended to support extra functions, specific to a MAC protocol (CSMA,TDMA,TSCH)
    """
    def __init__(self, local_manager):
        """Creates a Local MAC Manager object.

        Args:
            local_manager (LocalManager): a reference to the local WiSHFUL engine.
        """
        self.local_manager = local_manager
        self.log = logging.getLogger()
        pass

    def __execute_local_upi_func(self, UPIfunc, UPIargs, radioplatform_lst=None):
        if radioplatform_lst is None:
            UPIargs['interface'] = pickle.dumps('ALL,ALL')
        else:
            UPIargs['interface'] = pickle.dumps(radioplatform_lst)
        try:
            ret = pickle.loads(self.local_manager.runAt(UPIfunc, UPIargs))
            if type(radioplatform_lst) == str and radioplatform_lst != 'ALL,ALL':
                return ret[radioplatform_lst]
            return ret
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing %s: %s", UPIfunc.__name__, e)
            return -1

    def update_macconfiguration(self, parameter_key_values, radioplatform_lst=None):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary containing parameter key-value pairs.
             radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        UPIfunc = UPI_R.setParameterLowerLayer
        UPIargs = {'param_key_values': parameter_key_values}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def read_macconfiguration(self, parameter_keys, radioplatform_lst=None):
        """Update the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        UPIfunc = UPI_R.getParameterLowerLayer
        UPIargs = {'param_keys': parameter_keys}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def monitor_mac(self, measurement_keys, radioplatform_lst=None):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        UPIfunc = UPI_R.getMonitor
        UPIargs = {'measurement_keys': measurement_keys}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def monitor_mac_periodic(self, measurement_keys, collect_period, collect_iterations, report_period, report_callback, radioplatform_lst=None):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.getMonitorBounce
        UPIargs = {'measurement_keys': measurement_keys, 'collect_period': collect_period,
                   'report_period': report_period, 'num_iterations': collect_iterations, 'report_callback': report_callback}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def monitor_mac_async(self, event_keys, event_callback, radioplatform_lst=None):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.

        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.defineEvent
        UPIargs = {'event_keys': event_keys, 'event_callback': event_callback}
        return self.__execute_local_upi_func(UPIfunc, UPIargs)

    def activate_mac(self, name, radioplatform_lst=None):
        """Activate a MAC radio program.

        Args:
            name (str): Name of the MAC radioprogram (CSMA, TDMA, TSCH).
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.setActive
        UPIargs = {'radio_program_name': name, 'radio_program_index': 0}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def get_radioinfo(self, radioplatform_lst=None):
        """Returns a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.

        Args:
            radioplatform_lst (List[str], optional): list of radio platforms
        Returns:
            UPI_R.radio_info_t: a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.
        """
        UPIfunc = UPI_R.getRadioInfo
        UPIargs = {}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)

    def get_radioplatforms(self):
        """Returns a list of radio_platform_t objects containing interface name and platform name.

        Returns:
            List[UPI_R.radio_platform_t]: a list of radio_platform_t objects containing interface name and platform name.
        """
        UPIfunc = UPI_R.getRadioPlatforms
        UPIargs = {}
        try:
            return pickle.loads(self.local_manager.runAt(UPIfunc, UPIargs))
        except Exception as e:
            self.log.fatal(
                "An error occurred while getting available NICs: %s" % e)
        return -1

    def get_macaddress(self, radioplatform_lst=None):
        """Returns the macaddress of the interface.

        Args:
            radioplatform_lst (List[str], optional): list of radio platforms
        Returns:
            int: the macaddress
        """
        UPIfunc = UPI_R.getHwAddr
        UPIargs = {}
        return self.__execute_local_upi_func(UPIfunc, UPIargs, radioplatform_lst)


class GlobalMACManager(MACManager):
    """ Class doc """

    def __init__(self, global_manager):
        """ Class initialiser """
        self.global_manager = global_manager
        self.log = logging.getLogger()
        pass

    def __execute_global_upi_func(self, UPIfunc, UPIargs, nodes, radioplatform_lst=None):
        if radioplatform_lst is None:
            UPIargs['interface'] = pickle.dumps('ALL,ALL')
        else:
            UPIargs['interface'] = pickle.dumps(radioplatform_lst)
        try:
            pickeledRet = self.global_manager.runAt(nodes, UPIfunc, UPIargs)
            unpickledRet = {}
            for node in pickeledRet.keys():
                if type(radioplatform_lst) == str and radioplatform_lst != 'ALL,ALL':
                    unpickledRet[node] = pickle.loads(pickeledRet[node])[
                        radioplatform_lst]
                unpickledRet[node] = pickle.loads(pickeledRet[node])
            return unpickledRet
        except Exception as e:
            self.log.fatal(
                "An error occurred while executing %s: %s", UPIfunc.__name__, e)
            return -1

    def get_radioplatforms(self, nodes):
        """Returns a list of radio_platform_t objects containing interface name and platform name.

        Args:
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.

        Returns:
            List[UPI_R.radio_platform_t]: a list of radio_platform_t objects containing interface name and platform name.
        """
        UPIfunc = UPI_R.getRadioPlatforms
        UPIargs = {}
        try:
            pickeledRet = self.global_manager.runAt(nodes, UPIfunc, UPIargs)
            unpickledRet = {}
            for node in pickeledRet.keys():
                unpickledRet[node] = pickle.loads(pickeledRet[node])
            return unpickledRet
        except Exception as e:
            self.log.fatal(
                "An error occurred while getting available NICs: %s" % e)
        return -1

    def update_macconfiguration(self, parameter_key_values, nodes, radioplatform_lst=None):
        """Update the current MAC configuration.
        This function takes a dictionary argument containing parameter key-value pairs.
        This function returs a dictionary containing parameter key-error_code pairs.

        Args:
            parameter_key_values (Dict[str,Any]): a dictionary argument containing parameter key-value pairs.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str, int]: This function returs a dictionary containing parameter key-error_codes pairs.
        """
        UPIfunc = UPI_R.setParameterLowerLayer
        UPIargs = {'param_key_values': parameter_key_values}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def read_macconfiguration(self, parameter_keys, nodes, radioplatform_lst=None):
        """Update the current MAC configuration.
        This function takes a list of parameter keys as arguments.
        This function returns a dictionary containing parameter key-value pairs.

        Args:
            parameter_keys (List[str]): a list of parameter keys as arguments.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing parameter key-value pairs.
        """
        UPIfunc = UPI_R.getParameterLowerLayer
        UPIargs = {'param_keys': parameter_keys}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def monitor_mac(self, measurement_keys, nodes, radioplatform_lst=None):
        """Monitor the current MAC behaviour in a pull based manner.
        This function takes a list of measurement keys as arguments.
        This function returns a dictionary containing measurement key-value pairs.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            Dict[str,Any]: a dictionary containing measurement key-value pairs.
        """
        UPIfunc = UPI_R.getMonitor
        UPIargs = {'interface': pickle.dumps(
            radioplatform_lst), 'measurement_keys': measurement_keys}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def monitor_mac_periodic(self, measurement_keys, collect_period, collect_iterations, report_period, report_callback, nodes, radioplatform_lst=None):
        """Monitor the current MAC behaviour periodically in a pull based manner.
        This function takes a list of measurement keys and configuration alues for the periodic collection as arguments.
        This function returns an error code.

        Args:
            measurement_keys (List[str]): a list of measurement keys
            collect_period (int): Period between measurements.
            collect_iterations (int): Number of collect periods.
            report_period (int): Period between reports (report_period<=collect_period*collect_iterations)
            report_callback (Callable[[str,Dict[str,List[Any]]], None]): Callback with arguments radio_platform and measurement report.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.getMonitorBounce
        UPIargs = {'measurement_keys': measurement_keys, 'collect_period': collect_period,
                   'report_period': report_period, 'num_iterations': collect_iterations, 'report_callback': report_callback}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def monitor_mac_async(self, event_keys, event_callback, nodes, radioplatform_lst=None):
        """Monitor the MAC behaviour asynchroniously in a push based manner by registering for events.
        This function takes a list of event keys and an event callback as arguements.
        This function returns an error code.

        Args:
            event_keys (List[str]): a list of event keys
            event_callback (Callable[[str,str,Any],None]): Callback with arguments radio_platform, event name and event value.
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.defineEvent
        UPIargs = {'event_keys': event_keys, 'event_callback': event_callback}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def get_radioinfo(self, nodes, radioplatform_lst=None):
        """Returns a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.

        Args:
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms
        Returns:
            UPI_R.radio_info_t: a radio_info_t object containing all parameter, measurement and event keys as well as the available radio programs.
        """
        UPIfunc = UPI_R.getRadioInfo
        UPIargs = {}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def activate_mac(self, name, nodes, radioplatform_lst=None):
        """Activate a MAC radio program.

        Args:
            name (str): Name of the MAC radioprogram (CSMA, TDMA, TSCH).
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms

        Returns:
            int: error code (0 = success, -1 = fail, >=1 errno value)
        """
        UPIfunc = UPI_R.setActive
        UPIargs = {'radio_program_name': name, 'radio_program_index': 0}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)

    def get_macaddress(self, nodes, radioplatform_lst=None):
        """Returns the macaddress of the interface.

        Args:
            nodes (List[Node]): a list of wishful nodes to which the function must be delegated.
            radioplatform_lst (List[str], optional): list of radio platforms
        Returns:
            int: the macaddress
        """
        UPIfunc = UPI_R.getHwAddr
        UPIargs = {}
        return self.__execute_global_upi_func(UPIfunc, UPIargs, nodes, radioplatform_lst)
