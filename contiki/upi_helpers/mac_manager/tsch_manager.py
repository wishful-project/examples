import csv
from upi_helpers.mac_manager.taisc_manager import *


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

    def to_tuple(self):
        """Converts a hopping sequence to a tuple

        Returns:
            tuple: hopping sequnce in tuple format.
        """
        return tuple(self.TSCHHoppingSequenceList)

    @staticmethod
    def from_tuple(tpl):
        """Create a TSCH hopping sequence from tuple.

        Args:
            tpl (tuple): input tuple

        Returns:
            TSCHHoppingSequence: The TSCH hopping sequence
        """
        return TSCHHoppingSequence(list(tpl))

    def __str__(self):
        return str(self.TSCHHoppingSequenceList)


def read_tsch_slotframe(slotframe_csv):
    """Create TSCH slotframe from CSV file.
    """
    try:
        file_sf = open(slotframe_csv, 'rt')
        reader = csv.DictReader(file_sf)
        tsch_slotframe = taiscSlotFrame()
        for row in reader:
            # don't need to check if src and dst are in mac address list
            # reason: we update the slotframe for all nodes regardless if they are local
            src_address = int(row['macSrcNodeAddress'])
            dst_address = int(row['macDstNodeAddress'])
            tsch_slot = taiscLink(src_address, dst_address, int(row['macLinkType']), int(row['macChannelOffset']))
            tsch_slotframe.add_slot(tsch_slot)
        return tsch_slotframe
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


def read_tsch_slot_list_local(slot_list_csv, mac_adress_list):
    """Create TSCH slotlist from CSV file.
    """
    try:
        file_sf = open(slot_list_csv, 'rt')
        reader = csv.DictReader(file_sf)

        mac_address_slotlist_dict = {}
        for mac_address in mac_adress_list:
            mac_address_slotlist_dict[mac_address] = taiscSlotList()

        for row in reader:
            # check if the source address is known to the local control engine
            src_address = int(row['macSrcNodeAddress'])
            if src_address in mac_adress_list:
                if int(row['macLinkType']) == taiscLinkType.NORMAL:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.TX, int(row['macChannelOffset'])))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.BEACON, int(row['macChannelOffset'])))

            # check if the destination address is known to the local control engine or
            # equals the broadcast mac address (i.e. 0xFFFF)
            dst_address = int(row['macDstNodeAddress'])
            if dst_address in mac_adress_list or dst_address == 0xFFFF:
                if int(row['macLinkType']) == taiscLinkType.NORMAL:
                    if dst_address != 0xFFFF:
                        mac_address_slotlist_dict[dst_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.RX, int(row['macChannelOffset'])))
                    else:
                        for mac_address in mac_address_slotlist_dict.keys():
                            if mac_address != src_address:
                                mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                    int(row['macTimeslot']), taiscLinkType.RX, int(row['macChannelOffset'])))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    for mac_address in mac_address_slotlist_dict.keys():
                        if mac_address != src_address:
                            mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                int(row['macTimeslot']), taiscLinkType.SYNC, int(row['macChannelOffset'])))

            # special case for wifi beacons
            if int(row['macLinkType']) == taiscLinkType.COEXISTENCE:
                for mac_address in mac_address_slotlist_dict.keys():
                    mac_address_slotlist_dict[mac_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.IEEE80211_BEACON, int(row['macChannelOffset'])))

        return mac_address_slotlist_dict
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


def read_tsch_slot_list_global(slot_list_csv, mac_adress_list):
    """Create TSCH slotlist from CSV file.
    """
    try:
        file_sf = open(slot_list_csv, 'rt')
        reader = csv.DictReader(file_sf)

        mac_address_slotlist_dict = {}
        for mac_address in mac_adress_list:
            mac_address_slotlist_dict[mac_address] = taiscSlotList()

        for row in reader:
            # check if the mac address is known to the global control engine
            src_address = int(row['macSrcNodeAddress'])
            dst_address = int(row['macDstNodeAddress'])
            if (src_address in mac_adress_list and (dst_address in mac_adress_list or dst_address == 0xFFFF)):
                if int(row['macLinkType']) == taiscLinkType.NORMAL:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.TX, int(row['macChannelOffset'])))
                    if dst_address != 0xFFFF:
                        mac_address_slotlist_dict[dst_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.RX, int(row['macChannelOffset'])))
                    else:
                        for mac_address in mac_address_slotlist_dict.keys():
                            if mac_address != src_address:
                                mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                    int(row['macTimeslot']), taiscLinkType.RX, int(row['macChannelOffset'])))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.BEACON, int(row['macChannelOffset'])))
                    for mac_address in mac_address_slotlist_dict.keys():
                        if mac_address != src_address:
                            mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                int(row['macTimeslot']), taiscLinkType.SYNC, int(row['macChannelOffset'])))
                elif int(row['macLinkType']) == taiscLinkType.COEXISTENCE:
                    for mac_address in mac_address_slotlist_dict.keys():
                        mac_address_slotlist_dict[mac_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.IEEE80211_BEACON, int(row['macChannelOffset'])))
            else:
                print("Source {} or destination {} address unknown, skipping!!".format(src_address, dst_address))
        return mac_address_slotlist_dict
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


class LocalTSCHManager(LocalTAISCMACManager):
    """This class implements a local TSCH MAC Manager.
    It extends the LocalMACManager with TSCH specific functions.
    """

    def __init__(self, control_engine):
        """Creates a local TSCH manager
        """
        super(LocalTSCHManager, self).__init__(control_engine, "TSCH")
        pass

    def update_slotframe(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tsch_slotframe.csv'
        tsch_slotframe = read_tsch_slotframe(slotframe_csv)
        current_offset = 0
        ret_val = 0
        while(current_offset < tsch_slotframe.slotframe_length):
            slotframe_tpl = tsch_slotframe.to_tuple(current_offset, MAX_MSG_SIZE)
            param_key_values_dict = {'taiscSlotframe', slotframe_tpl}
            ret_val += self.update_macconfiguration(param_key_values_dict, self.get_hwaddr_list())
            current_offset += slotframe_tpl[1]
        return ret_val

    def add_slots(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tsch_slotframe.csv'
        current_offset = 0
        ret_val = 0
        tsch_mac_address_slot_list_dict = read_tsch_slot_list_local(slotframe_csv, self.get_hwaddr_list())
        for mac_address in tsch_mac_address_slot_list_dict.keys():
            tsch_slotlist = tsch_mac_address_slot_list_dict[mac_address]
            while(current_offset < tsch_slotlist.slot_list_length):
                slotlist_tpl = tsch_slotlist.to_tuple(current_offset, MAX_MSG_SIZE)
                param_key_values_dict = {'taiscSlotList', slotlist_tpl}
                ret_val += self.update_macconfiguration(param_key_values_dict, mac_address)
                current_offset += slotlist_tpl[0]
        return ret_val

    def blacklist_tschchannels(self, channel_lst):
        """This function allows to blacklist certain channels form the TSCH hopping sequence.

        Args:
            channel_lst (list): list of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        param_keys = ["IEEE802154e_macHoppingSequenceList"]
        ret = self.read_macconfiguration(param_keys, self.get_hwaddr_list[0])
        if ret == -1:
            return -1
        hopping_sequence = TSCHHoppingSequence.from_tuple(
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


class GlobalTSCHManager(GlobalTAISCMACManager):
    """This class implements a global TSCH MAC Manager.
    It extends the GlobalMACManager with TSCH specific functions.
    """

    def __init__(self, control_engine):
        """Creates a global TSCH manager

        Args:
            control_engine (GlobalManager): A reference to the WiSHFUL global control engine.
        """
        super(GlobalTSCHManager, self).__init__(control_engine, "TSCH")

    def update_slotframe(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tsch_slotframe.csv'
        tsch_slotframe = read_tsch_slotframe(slotframe_csv)
        current_offset = 0
        ret_val = 0
        while(current_offset < tsch_slotframe.slotframe_length):
            slotframe_tpl = tsch_slotframe.to_tuple(current_offset, MAX_MSG_SIZE)
            param_key_values_dict = {'taiscSlotframe', slotframe_tpl}
            ret_val += self.update_macconfiguration(param_key_values_dict)
            current_offset += slotframe_tpl[1]
        return ret_val

    def add_slots(self, slotframe_csv):
        current_offset = 0
        ret_val = 0
        tsch_mac_address_slot_list_dict = read_tsch_slot_list_global(slotframe_csv, self.get_hwaddr_list())
        for mac_address in tsch_mac_address_slot_list_dict.keys():
            tsch_slotlist = tsch_mac_address_slot_list_dict[mac_address]
            while(current_offset < tsch_slotlist.slot_list_length):
                slotlist_tpl = tsch_slotlist.to_tuple(current_offset, MAX_MSG_SIZE)
                param_key_values_dict = {'taiscSlotList', slotlist_tpl}
                ret_val += self.update_macconfiguration(param_key_values_dict, mac_address)
                current_offset += slotlist_tpl[0]
        return ret_val

    def blacklist_tschchannels(self, channel_lst):
        """This function allows to blacklist certain channels form the TSCH hopping sequence.

        Args:
            channel_lst (list): list of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        param_keys = ["IEEE802154e_macHoppingSequenceList"]
        ret = self.read_macconfiguration(param_keys, self.get_hwaddr_list[0])
        if ret == -1:
            return -1
        hopping_sequence = TSCHHoppingSequence.from_tuple(
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
