import csv
from enum import IntEnum
from upi_helpers.mac_manager.mac_manager import *
import logging


class TSCHHoppingSequence(object):
    """A Class representing A TSCH hopping sequence

    Attributes:
        TSCHHoppingSequenceList (list): a hopping sequence containing 802.15.4 channels.
    """

    def __init__(self, TSCHHoppingSequenceList):
        """Create a TSCH hopping sequence object.

        Args:
            TSCHHoppingSequenceList (list): a hopping sequence containing 802.15.4 channels.
        """
        self.TSCHHoppingSequenceList = TSCHHoppingSequenceList

    def toTuple(self):
        """Converts a hopping sequence to a tuple

        Returns:
            tuple: hopping sequnce in tuple format.
        """
        return tuple(self.TSCHHoppingSequenceList)

    @staticmethod
    def fromTuple(tpl):
        """Create a TSCH hopping sequence from tuple.

        Args:
            tpl (tuple): input tuple

        Returns:
            TSCHHoppingSequence: The TSCH hopping sequence
        """
        return TSCHHoppingSequence(list(tpl))

    def __str__(self):
        return str(self.TSCHHoppingSequenceList)


class TSCHLink(object):
    """This class represents a TSCH link with another node.
    """

    def __init__(self, macNodeAddress, macLinkOptions, macLinkType, macTimeslot, macChannelOffset):
        """Create a TSCH link

        Args
            macNodeAddress (int): Address of the neighboring node that shares this TSCHs link.
            macLinkOptions (int): Transmit = 4 / Receive =  5 / Beacon = 2 / Sync = 3/ NoOp = 1 / WiFi Sync = 8
            macLinkType (int): Advertising or normal link.
            macTimeslot (int): Slotnumber in slotframe
            macChannelOffset (int): channeloffset used in slot
        """
        self.macNodeAddress = macNodeAddress
        self.macLinkOptions = macLinkOptions
        self.macLinkType = macLinkType
        self.macTimeslot = macTimeslot
        self.macChannelOffset = macChannelOffset

    def toTuple(self):
        """Converts a TSCH link to a tuple

        Returns:
            tuple: TSCH link in tuple format.
        """
        return self.macNodeAddress, self.macLinkOptions, self.macLinkType, self.macTimeslot, self.macChannelOffset

    @staticmethod
    def fromTuple(tpl):
        """Create a TSCH link from tuple.

        Args:
            tpl (tuple): input tuple

        Returns:
            TSCHLink: The TSCH link
        """
        return TSCHLink(tpl[0], tpl[1], tpl[2], tpl[3], tpl[4])

    def __str__(self):
        return "{" + format(self.macNodeAddress, '#04x') + "," + str(self.macLinkOptions) + "," + str(self.macLinkType) + "," + str(self.macTimeslot) + "," + str(self.macChannelOffset) + "}"


class TSCHSlot(object):
    """This class represents a TSCH slot.
    """

    def __init__(self, macSrcNodeAddress, macDstNodeAddress, macLinkType, macTimeslot, macChannelOffset):
        """Create a TDMA slot.

        Args:
            macSrcNodeAddress (int): Source address
            macDstNodeAddress (int): Destination address
            macLinkType (int): Link type (Transmit = 4 / Receive =  5 / Beacon = 2 / Sync = 3/ NoOp = 1 / WiFi Sync = 8)
            macTimeslot (int): Slotnumber in slotframe
            macChannelOffset (int): channeloffset used in slot
        """
        self.macSrcNodeAddress = macSrcNodeAddress
        self.macDstNodeAddress = macDstNodeAddress
        self.macLinkType = macLinkType
        self.macTimeslot = macTimeslot
        self.macChannelOffset = macChannelOffset

    def __str__(self):
        return "{" + format(self.macSrcNodeAddress, '#04x') + ":" + format(self.macDstNodeAddress, '#04x') + "," + str(self.macLinkType) + "," + str(self.macTimeslot) + "," + str(self.macChannelOffset) + "}"


class TSCHSlotFrame(object):
    """This class represents a TSCH slotfrane.
    """

    def __init__(self, slotframe_length, num_channels):
        """Create a TSCH slotframe object.

        Args:
            slotframe_length (int): number of slot in slotframe.
            num_channels (int): number of hopping channels
        """
        self.log = logging.getLogger()
        self.slotframe_length = slotframe_length
        self.num_channels = num_channels
        self.slot_matrix = [[TSCHSlot(0, 0, 0, 0, 0) for x in range(
            slotframe_length)] for x in range(num_channels)]
        pass

    def read_tsch_slotframe(self, slotframe_csv):
        """Create TSCH slotframe from CSV file.

        Args:
            slotframe_csv (int): CSV file containing slotframe structures with following columns: macSrcNodeAddress,macDstNodeAddress,macLinkType,macTimeslot,macChannelOffset
        """
        try:
            file_sf = open(slotframe_csv, 'rt')
            reader = csv.DictReader(file_sf)
            index = 0
            for row in reader:
                if index < self.slotframe_length:
                    self.slot_matrix[int(row['macChannelOffset'])][int(row['macTimeslot'])] = TSCHSlot(int(row['macSrcNodeAddress']), int(
                        row['macDstNodeAddress']), int(row['macLinkType']), int(row['macTimeslot']), int(row['macChannelOffset']))
                else:
                    self.log.info("Skipping slot %s", row)
                index += 1
        except Exception as e:
            self.log.fatal(
                "An error occurred while reading parameters: %s" % e)
        finally:
            file_sf.close()
        pass

    def __str__(self):
        str_val = "Ch\\Sl#\t"
        for i in range(0, self.slotframe_length):
            str_val = str_val + str(i) + "\t\t\t"
        str_val = str_val + "\n"
        for i in range(0, self.num_channels):
            str_val = str_val + str(i)
            for j in range(0, self.slotframe_length):
                str_val = str_val + "\t" + str(self.slot_matrix[i][j])
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


class LocalTSCHManager(LocalMACManager):
    """This class implements a local TSCH MAC Manager.
    It extends the LocalMACManager with TSCH specific functions.
    """

    def __init__(self, local_manager, slotframe_csv, slotframe_length, num_channels):
        """Creates a local TSCH manager

        Args:
            local_manager (LocalManager): A reference to the WiSHFUL local manager.
            slotframe_csv (string): the filename and path to a slotframe CSV file. If empty, the default slotframe will be loaded
            slotframe_length (int): Number of slots in slotframe
            num_channels (int): number of hopping channels
        """
        super(LocalTSCHManager, self).__init__(local_manager)
        self.slotframe = TSCHSlotFrame(slotframe_length, num_channels)
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tsch_slotframe.csv'
        self.slotframe.read_tsch_slotframe(slotframe_csv)
        pass

    def configure_tschschedule(self, nodeID_radioplatform_map):
        """Configure the TSCH schedule on the nodes included in nodeID_radioplatform_map.
        The TSCH schedule is read from the CSV file given as argument during object creation.

        Args:
            nodeID_radioplatform_map (dict): Dictionary with keys = node_id (mac short addr) and values the corresponding radioplatforms.

        Returns:
            dict: for each node_id a list of error codes.
        """
        my_ret = {}
        for nodeID in nodeID_radioplatform_map.keys():
            my_ret[nodeID_radioplatform_map[nodeID]] = []
        for i in range(0, self.slotframe.num_channels):
            for j in range(0, self.slotframe.slotframe_length):
                slot = self.slotframe.slot_matrix[i][j]
                if slot.macSrcNodeAddress != 0:
                    if slot.macLinkType == macLinkType.NORMAL:
                        if slot.macSrcNodeAddress in nodeID_radioplatform_map.keys():
                            dst_link = TSCHLink(slot.macDstNodeAddress, macLinkOptions.TX,
                                                slot.macLinkType, slot.macTimeslot, slot.macChannelOffset)
                            param_key_values = {
                                "IEEE802154e_macTimeslot": dst_link.toTuple()}
                            ret = self.update_macconfiguration(
                                param_key_values, nodeID_radioplatform_map[slot.macSrcNodeAddress])
                            if ret != -1:
                                my_ret[nodeID_radioplatform_map[slot.macSrcNodeAddress]].append(
                                    ret["IEEE802154e_macTimeslot"])
                            else:
                                my_ret[nodeID_radioplatform_map[
                                    slot.macSrcNodeAddress]].append(ret)
                                self.log.info('Error setting timeslot')
                        if slot.macDstNodeAddress in nodeID_radioplatform_map.keys():
                            src_link = TSCHLink(slot.macSrcNodeAddress, macLinkOptions.RX,
                                                slot.macLinkType, slot.macTimeslot, slot.macChannelOffset)
                            param_key_values = {
                                "IEEE802154e_macTimeslot": src_link.toTuple()}
                            ret = self.update_macconfiguration(
                                param_key_values, nodeID_radioplatform_map[slot.macDstNodeAddress])
                            if ret != -1:
                                my_ret[nodeID_radioplatform_map[slot.macDstNodeAddress]].append(
                                    ret["IEEE802154e_macTimeslot"])
                            else:
                                my_ret[nodeID_radioplatform_map[
                                    slot.macDstNodeAddress]].append(ret)
                                self.log.info('Error setting timeslot')
                    elif slot.macLinkType == macLinkType.ADVERTISING:
                        for nodeID in nodeID_radioplatform_map.keys():
                            param_key_values = {}
                            if nodeID == slot.macSrcNodeAddress:
                                param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                    slot.macDstNodeAddress, macLinkOptions.IEEE802154_BEACON, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()
                            else:
                                param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                    slot.macSrcNodeAddress, macLinkOptions.SYNC, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()
                            ret = self.update_macconfiguration(
                                param_key_values, nodeID_radioplatform_map[nodeID])
                            if ret != -1:
                                my_ret[nodeID_radioplatform_map[nodeID]].append(
                                    ret["IEEE802154e_macTimeslot"])
                            else:
                                my_ret[nodeID_radioplatform_map[
                                    nodeID]].append(ret)
                                self.log.info('Error setting timeslot')
                    else:
                        self.log.info('Unknown slot type: %s', str(
                            self.slotframe.slot_matrix[i][j]))
        return my_ret

    def blacklist_tschchannels(self, channel_lst):
        """This function allows to blacklist certain channels form the TSCH hopping sequence.

        Args:
            channel_lst (list): list of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        param_keys = ["IEEE802154e_macHoppingSequenceList"]
        ret = self.read_macconfiguration(param_keys, "wpan0,TAISC")
        if ret == -1:
            return -1
        hopping_sequence = TSCHHoppingSequence.fromTuple(
            ret["IEEE802154e_macHoppingSequenceList"])
        new_hopping_sequence = []
        for channel in hopping_sequence.TSCHHoppingSequenceList:
            if channel not in channel_lst:
                new_hopping_sequence.append(channel)
        for channel in channel_lst:
            new_hopping_sequence.append(0)
        # first change the length of the hopping sequence
        param_key_values = {
            "IEEE802154e_macHoppingSequenceLength": len(channel_lst)}
        ret = self.update_macconfiguration(param_key_values)
        if ret == -1:
            return -1
        # now change the hopping sequence
        param_key_values = {
            "IEEE802154e_macHoppingSequenceList": tuple(new_hopping_sequence)}
        ret = self.update_macconfiguration(param_key_values)
        if ret == -1:
            return -1
        return ret


class GlobalTSCHManager(GlobalMACManager):
    """This class implements a global TSCH MAC Manager.
    It extends the GlobalMACManager with TSCH specific functions.
    """

    def __init__(self, global_manager, slotframe_csv, slotframe_length, num_channels):
        """Creates a global TSCH manager

        Args:
            global_manager (GlobalManager): A reference to the WiSHFUL global manager.
            slotframe_csv (string): the filename and path to a slotframe CSV file. If empty, the default slotframe will be loaded
            slotframe_length (int): Number of slots in slotframe
            num_channels (int): number of hopping channels
        """
        super(GlobalTSCHManager, self).__init__(global_manager)
        self.slotframe = TSCHSlotFrame(slotframe_length, num_channels)
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tsch_slotframe.csv'
        self.slotframe.read_tsch_slotframe(slotframe_csv)
        pass

    def configure_tschschedule(self, nodes, nodeID_ipaddress_map, nodeID_radioplatform_map):
        """Configure the TSCH schedule on the nodes included in nodeID_radioplatform_map.
        The TSCH schedule is read from the CSV file given as argument during object creation.

        Args:
            nodes (list): List of nodes
            nodeID_ipaddress_map (dict): Key = node_id(mac_short_addr) and value = ip_address of the corresponding Wishful agent.
            nodeID_radioplatform_map (dict): Dictionary with keys = node_id (mac short addr) and values the corresponding radioplatforms.

        Returns:
            dict: for each node_id a list of error codes.
        """
        my_ret = {}
        for nodeID in nodeID_radioplatform_map.keys():
            my_ret[nodeID] = []
        for i in range(0, self.slotframe.num_channels):
            for j in range(0, self.slotframe.slotframe_length):
                slot = self.slotframe.slot_matrix[i][j]
                if slot.macSrcNodeAddress != 0:
                    if slot.macLinkType == macLinkType.NORMAL:
                        if slot.macSrcNodeAddress in nodeID_radioplatform_map.keys():
                            param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                slot.macDstNodeAddress, macLinkOptions.TX, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()  # error : shortened
                            ret = self.update_macconfiguration(param_key_values, [nodeID_ipaddress_map[
                                                               slot.macSrcNodeAddress]], nodeID_radioplatform_map[slot.macSrcNodeAddress])
                            if ret != -1:
                                error = ret[str(nodeID_ipaddress_map[slot.macSrcNodeAddress])][nodeID_radioplatform_map[
                                    slot.macSrcNodeAddress]]["IEEE802154e_macTimeslot"]  # error : corrected ret
                                self.log.info("Node %s, %s:%s  adding IEEE802154e_macTimeslot %s: error %s", nodeID, str(nodeID_ipaddress_map[
                                              slot.macSrcNodeAddress]), nodeID_radioplatform_map[slot.macSrcNodeAddress], param_key_values["IEEE802154e_macTimeslot"], error)
                                my_ret[slot.macSrcNodeAddress].append(error)
                            else:
                                my_ret[slot.macSrcNodeAddress].append(ret)
                                self.log.info('Error setting timeslot for node %s,%s,%s', str(nodeID_ipaddress_map[
                                              slot.macSrcNodeAddress]), nodeID_radioplatform_map[slot.macSrcNodeAddress], nodeID)
                        if slot.macDstNodeAddress in nodeID_radioplatform_map.keys():
                            param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                slot.macSrcNodeAddress, macLinkOptions.RX, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()  # error : shortened
                            ret = self.update_macconfiguration(param_key_values, [nodeID_ipaddress_map[
                                                               slot.macDstNodeAddress]], nodeID_radioplatform_map[slot.macDstNodeAddress])
                            if ret != -1:
                                error = ret[str(nodeID_ipaddress_map[slot.macDstNodeAddress])][nodeID_radioplatform_map[
                                    slot.macDstNodeAddress]]["IEEE802154e_macTimeslot"]  # error : corrected ret
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
                                param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                    slot.macDstNodeAddress, macLinkOptions.IEEE802154_BEACON, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()
                            else:
                                param_key_values["IEEE802154e_macTimeslot"] = TSCHLink(
                                    slot.macSrcNodeAddress, macLinkOptions.SYNC, slot.macLinkType, slot.macTimeslot, slot.macChannelOffset).toTuple()
                            ret = self.update_macconfiguration(param_key_values, [nodeID_ipaddress_map[
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
                        self.log.info('Unknown slot type: %s', str(
                            self.slotframe.slot_matrix[i][j]))
        return my_ret

    def blacklist_tschchannels(self, channel_lst, nodes):
        """This function allows to blacklist certain channels form the TSCH hopping sequence.

        Args:
            channel_lst (list): list of channels to be blacklisted
            nodes (list): list of nodes on which the channels must be blacklisted.

        Returns:
            dict: error codes from each node
        """
        param_keys = ["IEEE802154e_macHoppingSequenceList"]
        ret = self.read_macconfiguration(param_keys, nodes[0], "wpan0,TAISC")
        if ret == -1:
            return -1
        hopping_sequence = TSCHHoppingSequence.fromTuple(
            ret["IEEE802154e_macHoppingSequenceList"])
        new_hopping_sequence = []
        for channel in hopping_sequence.macHoppingSequenceList:
            if channel not in channel_lst:
                new_hopping_sequence.append(channel)
        for channel in channel_lst:
            new_hopping_sequence.append(0)
        # first change the length of the hopping sequence
        param_key_values = {
            "IEEE802154e_macHoppingSequenceLength": len(channel_lst)}
        ret = self.update_macconfiguration(param_key_values, nodes)
        if ret == -1:
            return -1
        # now change the hopping sequence
        param_key_values = {
            "IEEE802154e_macHoppingSequenceList": tuple(new_hopping_sequence)}
        ret = self.update_macconfiguration(param_key_values, nodes)
        if ret == -1:
            return -1
        return ret
