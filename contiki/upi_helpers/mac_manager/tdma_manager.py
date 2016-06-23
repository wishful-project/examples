"""Summary
"""
import csv
from enum import IntEnum
from upi_helpers.mac_manager.mac_manager import *
import logging


class TDMALink(object):
    """This class represents a TDMA link with another node.
    """

    def __init__(self, macNodeAddress, macLinkOptions, macLinkType, macTimeslot, phyChannel):
        """Create a TDMA link

        Args
            macNodeAddress (int): Address of the neighboring node that shares this TDMA link.
            macLinkOptions (int): Transmit = 4 / Receive =  5 / Beacon = 2 / Sync = 3/ NoOp = 1 / WiFi Sync = 8
            macLinkType (int): Advertising or normal link.
            macTimeslot (int): Slotnumber in slotframe
            phyChannel (int): 802.15.4 channel used in slot
        """
        self.macNodeAddress = macNodeAddress
        self.macLinkOptions = macLinkOptions
        self.macLinkType = macLinkType
        self.macTimeslot = macTimeslot
        self.phyChannel = phyChannel

    def toTuple(self):
        """Converts TDMA link object to tuple

        Returns:
            tuple: A tuple representing the TDMA link
        """
        return self.macNodeAddress, self.macLinkOptions, self.macLinkType, self.macTimeslot, self.phyChannel

    @staticmethod
    def fromTuple(tpl):
        """Create a TDMA link from tuple.

        Args:
            tpl (tuple): input tuple

        Returns:
            TDMALink: The TDMA link
        """
        return TDMALink(tpl[0], tpl[1], tpl[2], tpl[3], tpl[4])

    def __str__(self):
        return "{" + format(self.macNodeAddress, '#04x') + "," + str(self.macLinkOptions) + "," + str(self.macLinkType) + "," + str(self.macTimeslot) + "," + str(self.phyChannel) + "}"


class TDMASlot(object):
    """This class represents a TDMA slot.
    """

    def __init__(self, macSrcNodeAddress, macDstNodeAddress, macLinkType, macTimeslot, phyChannel):
        """Create a TDMA slot.

        Args:
            macSrcNodeAddress (int): Source address
            macDstNodeAddress (int): Destination address
            macLinkType (int): Link type (Transmit = 4 / Receive =  5 / Beacon = 2 / Sync = 3/ NoOp = 1 / WiFi Sync = 8)
            macTimeslot (int): Slotnumber in slotframe
            phyChannel (int): 802.15.4 channel used in slot
        """
        self.macSrcNodeAddress = macSrcNodeAddress
        self.macDstNodeAddress = macDstNodeAddress
        self.macLinkType = macLinkType
        self.macTimeslot = macTimeslot
        self.phyChannel = phyChannel

    def __str__(self):
        return "{" + format(self.macSrcNodeAddress, '#04x') + ":" + format(self.macDstNodeAddress, '#04x') + "," + str(self.macLinkType) + "," + str(self.macTimeslot) + "," + str(self.phyChannel) + "}"


class TDMASlotFrame(object):
    """This class represents a TDMA slotfrane.
    """

    def __init__(self, slotframe_length):
        """Create a TDMA slotframe object.

        Args:
            slotframe_length (int): number of slot in slotframe.
        """
        self.log = logging.getLogger()
        self.slotframe_length = slotframe_length
        self.slots = [TDMASlot(0, 0, 0, 0, 0) for x in range(slotframe_length)]
        pass

    def read_tdma_slotframe(self, slotframe_csv):
        """Create TDMA slotframe from CSV file.

        Args:
            slotframe_csv (int): CSV file containing slotframe structures with following columns: macSrcNodeAddress,macDstNodeAddress,macLinkType,macTimeslot,phyChannel
        """
        try:
            file_sf = open(slotframe_csv, 'rt')
            reader = csv.DictReader(file_sf)
            index = 0
            for row in reader:
                if index < self.slotframe_length:
                    self.slots[int(row['macTimeslot'])] = TDMASlot(int(row['macSrcNodeAddress']), int(
                        row['macDstNodeAddress']), int(row['macLinkType']), int(row['macTimeslot']), int(row['phyChannel']))
                else:
                    self.log.info("Skipping slot %s", row)
                index += 1
        except Exception as e:
            self.log.fatal(
                "An error occurred while reading parameters: %s" % e)
        finally:
            file_sf.close()

    def __str__(self):
        str_val = "Sl#\t"
        for i in range(0, self.slotframe_length):
            str_val = str_val + str(i) + "\t\t\t"
        str_val = str_val + "\n"
        for j in range(0, self.slotframe_length):
            str_val = str_val + "\t" + str(self.slots[j])
        str_val = str_val + "\n"
        return str_val


class macLinkOptions(IntEnum):
    """Possible MACLinkOptions
    """
    NOPI = 1
    IEEE802154_BEACON = 2
    SYNC = 3
    TX = 4
    RX = 5
    OFF = 6
    IEEE80211_BEACON = 8


class macLinkType(IntEnum):
    """Possible MacLinkTypes
    """
    NORMAL = 0,
    ADVERTISING = 1,


class LocalTDMAManager(LocalMACManager):
    """This class implements a local TDMA MAC Manager. It extends the LocalMACManager with TDMA specific functions.
    """

    def __init__(self, local_manager, slotframe_csv, slotframe_length):
        """Creates a local TDMA manager

        Args:
            local_manager (LocalManager): A reference to the WiSHFUL local manager.
            slotframe_csv (string): the filename and path to a slotframe CSV file. If empty, the default slotframe will be loaded
            slotframe_length (int): Number of slots in slotframe
        """
        super(LocalTDMAManager, self).__init__(local_manager)
        self.slotframe = TDMASlotFrame(slotframe_length)
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tdma_slotframe.csv'
        self.slotframe.read_tdma_slotframe(slotframe_csv)
        pass

    def configure_tdmaschedule(self, nodeID_radioplatform_map):
        """Configure the TDMA schedule on the nodes included in nodeID_radioplatform_map.
        The TDMA schedule is read from the CSV file givven as argument during object creation.

        Args:
            nodeID_radioplatform_map (dict): Dictionary with keys = node_id (mac short addr) and values the corresponding radioplatforms.

        Returns:
            dict: for each node_id a list of error codes.
        """
        my_ret = {}
        for nodeID in nodeID_radioplatform_map.keys():
            my_ret[nodeID] = []
        for i in range(0, self.slotframe.slotframe_length):
            slot = self.slotframe.slots[i]
            if slot.macSrcNodeAddress != 0:
                if slot.macLinkType == macLinkType.NORMAL:
                    if slot.macSrcNodeAddress in nodeID_radioplatform_map.keys():
                        dst_link = TDMALink(slot.macDstNodeAddress, macLinkOptions.TX,
                                            slot.macLinkType, slot.macTimeslot, slot.phyChannel)
                        param_key_values = {
                            "IEEE802154e_macTimeslot": dst_link.toTuple()}
                        ret = self.update_macconfiguration(
                            param_key_values, nodeID_radioplatform_map[slot.macSrcNodeAddress])
                        if ret != -1:
                            ret = ret["IEEE802154e_macTimeslot"]
                        else:
                            self.log.info('Error setting timeslot')
                        my_ret[slot.macSrcNodeAddress].append(ret)
                    if slot.macDstNodeAddress in nodeID_radioplatform_map.keys():
                        src_link = TDMALink(slot.macSrcNodeAddress, macLinkOptions.RX,
                                            slot.macLinkType, slot.macTimeslot, slot.phyChannel)
                        param_key_values = {
                            "IEEE802154e_macTimeslot": src_link.toTuple()}
                        ret = self.update_macconfiguration(
                            param_key_values, nodeID_radioplatform_map[slot.macDstNodeAddress])
                        if ret != -1:
                            ret = ret["IEEE802154e_macTimeslot"]
                        else:
                            self.log.info('Error setting timeslot')
                        my_ret[slot.macSrcNodeAddress].append(ret)
                elif slot.macLinkType == macLinkType.ADVERTISING:
                    for nodeID in nodeID_radioplatform_map.keys():
                        param_key_values = {}
                        if nodeID == slot.macSrcNodeAddress:
                            param_key_values["IEEE802154e_macTimeslot"] = TDMALink(
                                slot.macDstNodeAddress, macLinkOptions.IEEE802154_BEACON, slot.macLinkType, slot.macTimeslot, slot.phyChannel).toTuple()
                        else:
                            param_key_values["IEEE802154e_macTimeslot"] = TDMALink(
                                slot.macSrcNodeAddress, macLinkOptions.SYNC, slot.macLinkType, slot.macTimeslot, slot.phyChannel).toTuple()
                        ret = self.update_macconfiguration(
                            param_key_values, nodeID_radioplatform_map[nodeID])
                        if ret != -1:
                            ret = ret["IEEE802154e_macTimeslot"]
                        else:
                            self.log.info('Error setting timeslot')
                        my_ret[slot.macSrcNodeAddress].append(ret)
                else:
                    self.log.info('Unknown slot type: %s',
                                  str(self.slotframe.slots[i]))
        return my_ret


class GlobalTDMAManager(GlobalMACManager):
    """This class implements a global TDMA MAC Manager. It extends the GlobalMACManager with TDMA specific functions.
    """

    def __init__(self, global_manager, slotframe_csv, slotframe_length):
        """Creates a global TDMA manager.

        Args:
            global_manager (GlobalManager): A reference to the WiSHFUL global manager.
            slotframe_csv (string): the filename and path to a slotframe CSV file. If empty, the default slotframe will be loaded
            slotframe_length (int): Number of slots in slotframe
        """
        super(GlobalTDMAManager, self).__init__(global_manager)
        self.slotframe = TDMASlotFrame(slotframe_length)
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tdma_slotframe.csv'
        self.slotframe.read_tdma_slotframe(slotframe_csv)
        pass

    def configure_tdmaschedule(self, nodes, nodeID_ipaddress_map, nodeID_radioplatform_map):
        """Configure the TDMA schedule on the nodes included in nodeID_radioplatform_map.
        The TDMA schedule is read from the CSV file givven as argument during object creation.

        Args:
            nodes (list): List of nodes.
            nodeID_ipaddress_map (dict of int: str): Dictionary with keys = node_id (mac short addr) and values the IPAdress of the WiSHFUL agent controlling the node.
            nodeID_radioplatform_map (dict): Dictionary with keys = node_id (mac short addr) and values the corresponding radioplatforms.

        Returns:
            dict: for each node_id a list of error codes.
        """
        my_ret = {}
        for nodeID in nodeID_radioplatform_map.keys():
            my_ret[nodeID] = []
        for i in range(0, self.slotframe.slotframe_length):
            slot = self.slotframe.slots[i]
            if slot.macSrcNodeAddress != 0:
                if slot.macLinkType == macLinkType.NORMAL:
                    if slot.macSrcNodeAddress in nodeID_radioplatform_map.keys():
                        dst_link = TDMALink(slot.macDstNodeAddress, macLinkOptions.TX,
                                            slot.macLinkType, slot.macTimeslot, slot.phyChannel)
                        param_key_values = {
                            "IEEE802154e_macTimeslot": dst_link.toTuple()}
                        ret = self.configure_mac(param_key_values, [nodeID_ipaddress_map[
                                                 slot.macSrcNodeAddress]], nodeID_radioplatform_map[slot.macSrcNodeAddress])
                        if ret != -1:
                            error = ret[str(nodeID_ipaddress_map[slot.macSrcNodeAddress])][
                                nodeID_radioplatform_map[slot.macSrcNodeAddress]]["IEEE802154e_macTimeslot"]
                            # error : corrected ret
                            self.log.info("Node %s, %s:%s  adding IEEE802154e_macTimeslot %s: error %s", nodeID, str(nodeID_ipaddress_map[
                                          slot.macSrcNodeAddress]), nodeID_radioplatform_map[slot.macSrcNodeAddress], param_key_values["IEEE802154e_macTimeslot"], error)
                            my_ret[slot.macSrcNodeAddress].append(error)
                        else:
                            my_ret[slot.macSrcNodeAddress].append(ret)
                            self.log.info('Error setting timeslot for node %s,%s,%s', str(nodeID_ipaddress_map[
                                          slot.macSrcNodeAddress]), nodeID_radioplatform_map[slot.macSrcNodeAddress], nodeID)
                    if slot.macDstNodeAddress in nodeID_radioplatform_map.keys():
                        src_link = TDMALink(slot.macSrcNodeAddress, macLinkOptions.RX,
                                            slot.macLinkType, slot.macTimeslot, slot.phyChannel)
                        param_key_values = {
                            "IEEE802154e_macTimeslot": src_link.toTuple()}
                        ret = self.configure_mac(param_key_values, [nodeID_ipaddress_map[
                                                 slot.macDstNodeAddress]], nodeID_radioplatform_map[slot.macDstNodeAddress])
                        if ret != -1:
                            error = ret[str(nodeID_ipaddress_map[slot.macDstNodeAddress])][
                                nodeID_radioplatform_map[slot.macDstNodeAddress]]["IEEE802154e_macTimeslot"]
                            # error : corrected ret
                            self.log.info("Node %s, %s:%s  adding IEEE802154e_macTimeslot %s: error %s", nodeID, str(nodeID_ipaddress_map[
                                          nodeID]), nodeID_radioplatform_map[nodeID], param_key_values["IEEE802154e_macTimeslot"], error)
                            my_ret[slot.macDstNodeAddress].append(error)
                        else:
                            my_ret[slot.macDstNodeAddress].append(ret)
                            self.log.info('Error setting timeslot for node %s,%s,%s', str(nodeID_ipaddress_map[
                                          slot.macDstNodeAddress]), nodeID_radioplatform_map[slot.macSrcNodeAddress], nodeID)
                elif slot.macLinkType == macLinkType.ADVERTISING:
                    for nodeID in nodeID_radioplatform_map.keys():
                        param_key_values = {}
                        if nodeID == slot.macSrcNodeAddress:
                            param_key_values["IEEE802154e_macTimeslot"] = TDMALink(
                                slot.macDstNodeAddress, macLinkOptions.IEEE802154_BEACON, slot.macLinkType, slot.macTimeslot, slot.phyChannel).toTuple()
                        else:
                            param_key_values["IEEE802154e_macTimeslot"] = TDMALink(
                                slot.macSrcNodeAddress, macLinkOptions.SYNC, slot.macLinkType, slot.macTimeslot, slot.phyChannel).toTuple()
                        ret = self.configure_mac(param_key_values, [nodeID_ipaddress_map[
                                                 nodeID]], nodeID_radioplatform_map[nodeID])
                        if ret != -1:
                            error = ret[str(nodeID_ipaddress_map[nodeID])][
                                nodeID_radioplatform_map[nodeID]]["IEEE802154e_macTimeslot"]
                            self.log.info("Node %s, %s:%s  adding IEEE802154e_macTimeslot %s: error %s", nodeID, str(nodeID_ipaddress_map[
                                          nodeID]), nodeID_radioplatform_map[nodeID], param_key_values["IEEE802154e_macTimeslot"], error)
                            my_ret[nodeID].append(error)
                        else:
                            self.log.info('Error setting timeslot for node %s,%s,%s', str(
                                nodeID_ipaddress_map[nodeID]), nodeID_radioplatform_map[nodeID], nodeID)
                            my_ret[nodeID].append(ret)
                else:
                    self.log.info('Unknown slot type: %s',
                                  str(self.slotframe.slots[i]))
        return my_ret
