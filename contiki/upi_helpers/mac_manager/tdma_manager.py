"""Summary
"""
import csv
from upi_helpers.mac_manager.taisc_manager import *


def read_tdma_slotframe(slotframe_csv):
    """Create TSCH slotframe from CSV file.
    """
    try:
        file_sf = open(slotframe_csv, 'rt')
        reader = csv.DictReader(file_sf)
        tdma_slotframe = taiscSlotFrame()
        for row in reader:
            # don't need to check if src and dst are in mac address list
            # reason: we update the slotframe for all nodes regardless if they are local
            src_address = int(row['macSrcNodeAddress'])
            dst_address = int(row['macDstNodeAddress'])
            tdma_slot = taiscLink(src_address, dst_address, int(row['macLinkType']), 0)
            tdma_slotframe.add_slot(tdma_slot)
        return tdma_slotframe
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


def read_tdma_slot_list_local(slot_list_csv, mac_adress_list):
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
                        int(row['macTimeslot']), taiscLinkType.TX, 0))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.BEACON, 0))

            # check if the destination address is known to the local control engine or
            # equals the broadcast mac address (i.e. 0xFFFF)
            dst_address = int(row['macDstNodeAddress'])
            if dst_address in mac_adress_list or dst_address == 0xFFFF:
                if int(row['macLinkType']) == taiscLinkType.NORMAL:
                    if dst_address != 0xFFFF:
                        mac_address_slotlist_dict[dst_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.RX, 0))
                    else:
                        for mac_address in mac_address_slotlist_dict.keys():
                            if mac_address != src_address:
                                mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                    int(row['macTimeslot']), taiscLinkType.RX, 0))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    for mac_address in mac_address_slotlist_dict.keys():
                        if mac_address != src_address:
                            mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                int(row['macTimeslot']), taiscLinkType.SYNC, 0))

            # special case for wifi beacons
            if int(row['macLinkType']) == taiscLinkType.COEXISTENCE:
                for mac_address in mac_address_slotlist_dict.keys():
                    mac_address_slotlist_dict[mac_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.IEEE80211_BEACON, 0))

        return mac_address_slotlist_dict
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


def read_tdma_slot_list_global(slot_list_csv, mac_adress_list):
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
                        int(row['macTimeslot']), taiscLinkType.TX, 0))
                    if dst_address != 0xFFFF:
                        mac_address_slotlist_dict[dst_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.RX, 0))
                    else:
                        for mac_address in mac_address_slotlist_dict.keys():
                            if mac_address != src_address:
                                mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                    int(row['macTimeslot']), taiscLinkType.RX, 0))
                elif int(row['macLinkType']) == taiscLinkType.ADVERTISING:
                    mac_address_slotlist_dict[src_address].append(taiscSlot(
                        int(row['macTimeslot']), taiscLinkType.BEACON, 0))
                    for mac_address in mac_address_slotlist_dict.keys():
                        if mac_address != src_address:
                            mac_address_slotlist_dict[mac_address].append(taiscSlot(
                                int(row['macTimeslot']), taiscLinkType.SYNC, 0))
                elif int(row['macLinkType']) == taiscLinkType.COEXISTENCE:
                    for mac_address in mac_address_slotlist_dict.keys():
                        mac_address_slotlist_dict[mac_address].append(taiscSlot(
                            int(row['macTimeslot']), taiscLinkType.IEEE80211_BEACON, 0))
            else:
                print("Source {} or destination {} address unknown, skipping!!".format(src_address, dst_address))
        return mac_address_slotlist_dict
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


class LocalTDMAManager(LocalTAISCMACManager):
    """This class implements a local TDMA MAC Manager. It extends the LocalMACManager with TDMA specific functions.
    """

    def __init__(self, control_engine):
        """Creates a local TDMA manager
        """
        super(LocalTDMAManager, self).__init__(control_engine, "TDMA")
        pass

    def update_slotframe(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tdma_slotframe.csv'
        tdma_slotframe = read_tdma_slotframe(slotframe_csv)
        current_offset = 0
        ret_val = 0
        while(current_offset < tdma_slotframe.slotframe_length):
            slotframe_tpl = tdma_slotframe.to_tuple(current_offset, MAX_MSG_SIZE)
            param_key_values_dict = {'taiscSlotframe', slotframe_tpl}
            ret_val += self.update_macconfiguration(param_key_values_dict, self.get_hwaddr_list())
            current_offset += slotframe_tpl[1]
        return ret_val

    def add_slots(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tdma_slotframe.csv'
        current_offset = 0
        ret_val = 0
        tdma_mac_address_slot_list_dict = read_tdma_slot_list_local(slotframe_csv, self.get_hwaddr_list())
        for mac_address in tdma_mac_address_slot_list_dict.keys():
            tdma_slotlist = tdma_mac_address_slot_list_dict[mac_address]
            while(current_offset < tdma_slotlist.slot_list_length):
                slotlist_tpl = tdma_slotlist.to_tuple(current_offset, MAX_MSG_SIZE)
                param_key_values_dict = {'taiscSlotList', slotlist_tpl}
                ret_val += self.update_macconfiguration(param_key_values_dict, mac_address)
                current_offset += slotlist_tpl[0]
        return ret_val


class GlobalTDMAManager(GlobalTAISCMACManager):
    """This class implements a global TDMA MAC Manager. It extends the GlobalMACManager with TDMA specific functions.
    """

    def __init__(self, control_engine):
        """Creates a global TDMA manager

        Args:
            control_engine (Global Control Engine): A reference to the WiSHFUL global control engine.
        """
        super(GlobalTDMAManager, self).__init__(control_engine, "TDMA")

    def update_slotframe(self, slotframe_csv):
        if slotframe_csv == '':
            slotframe_csv = 'upi_helpers/mac_manager/default_tdma_slotframe.csv'
        tdma_slotframe = read_tdma_slotframe(slotframe_csv)
        current_offset = 0
        ret_val = 0
        while(current_offset < tdma_slotframe.slotframe_length):
            slotframe_tpl = tdma_slotframe.to_tuple(current_offset, MAX_MSG_SIZE)
            param_key_values_dict = {'taiscSlotframe', slotframe_tpl}
            ret_val += self.update_macconfiguration(param_key_values_dict)
            current_offset += slotframe_tpl[1]
        return ret_val

    def add_slots(self, slotframe_csv):
        current_offset = 0
        ret_val = 0
        tdma_mac_address_slot_list_dict = read_tsch_slot_list_global(slotframe_csv, self.get_hwaddr_list())
        for mac_address in tdma_mac_address_slot_list_dict.keys():
            tdma_slotlist = tdma_mac_address_slot_list_dict[mac_address]
            while(current_offset < tdma_slotlist.slot_list_length):
                slotlist_tpl = tdma_slotlist.to_tuple(current_offset, MAX_MSG_SIZE)
                param_key_values_dict = {'taiscSlotList', slotlist_tpl}
                ret_val += self.update_macconfiguration(param_key_values_dict, mac_address)
                current_offset += slotlist_tpl[0]
        return ret_val
