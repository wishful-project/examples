from enum import IntEnum
from .mac_manager import MACManager
import csv

MAX_MSG_SIZE = 64


class TAISCMACManager(MACManager):

    def __init__(self, node_manager, mac_mode):
        super(TAISCMACManager, self).__init__(node_manager, mac_mode)
        self.hopping_sequence = None
        pass

    def update_slotframe(self, slotframe_csv, mac_protocol="TDMA"):
        if mac_protocol is not "TDMA" and mac_protocol is not "TSCH":
            self.log.error("Configuring slotframe not possible for {}".format(mac_protocol))
            return -1
        if self.mac_mode is not mac_protocol:
            self.log.warning("Configuring {} slotframe in different mac mode {}".format(mac_protocol, self.mac_mode))
        param_name = ""
        if mac_protocol == "TDMA":
            param_name = "IEEE802154_macSlotframe"
        elif mac_protocol == "TSCH":
            param_name = "IEEE802154e_macSlotframe"
        if slotframe_csv == '':
            slotframe_csv = './mac_managers/default_taisc_slotframe.csv'
        taisc_slotframe = read_taisc_slotframe(slotframe_csv)
        current_offset = 0
        ret_val = 0
        ret_dict = {}
        for mac_address in self.node_manager.mac_address_list:
            ret_dict[mac_address] = 0
        while(current_offset < taisc_slotframe.slotframe_length):
            slotframe_tpl = taisc_slotframe.to_tuple(current_offset, MAX_MSG_SIZE)
            param_key_values_dict = {param_name: slotframe_tpl}
            print("UPDATE : %s" % (param_key_values_dict))
            ret = self.update_macconfiguration(param_key_values_dict)
            for mac_address in ret:
                if type(ret[mac_address]) is dict:
                    ret_dict[mac_address] += ret[mac_address][param_name]
                    ret_val += ret[mac_address][param_name]
                else:
                    ret_dict[mac_address] += ret[mac_address]
                    ret_val += ret[mac_address]
            current_offset += slotframe_tpl[1]
        return ret_val

    def add_slots(self, slotframe_csv, mac_protocol="TDMA"):
        if mac_protocol is not "TDMA" and mac_protocol is not "TSCH":
            self.log.error("Configuring slotframe not possible for {}".format(mac_protocol))
            return -1
        if self.mac_mode is not mac_protocol:
            self.log.warning("Configuring {} slotframe in different mac mode {}".format(mac_protocol, self.mac_mode))
        param_name = ""
        if mac_protocol == "TDMA":
            param_name = "IEEE802154_macSlotlist"
        elif mac_protocol == "TSCH":
            param_name = "IEEE802154e_macSlotlist"
        if slotframe_csv == '':
            slotframe_csv = './mac_managers/default_taisc_slotframe.csv'
        current_offset = 0
        ret_val = 0
        taisc_mac_address_slot_list_dict = read_taisc_slot_list(slotframe_csv, self.node_manager.mac_address_list)
        for mac_address in taisc_mac_address_slot_list_dict.keys():
            taisc_slotlist = taisc_mac_address_slot_list_dict[mac_address]
            while(current_offset < taisc_slotlist.slot_list_length):
                slotlist_tpl = taisc_slotlist.to_tuple(current_offset, MAX_MSG_SIZE)
                param_key_values_dict = {param_name: slotlist_tpl}
                ret = self.update_macconfiguration(param_key_values_dict, mac_address)
                if type(ret[mac_address]) is dict:
                    ret_val += ret[mac_address][param_name]
                else:
                    ret_val += ret[mac_address]
                current_offset += slotlist_tpl[0]
        return ret_val

    def blacklist_channels(self, channel_lst, mac_address_list=None):
        """This function allows to blacklist certain channels.

        Args:
            channel_lst (list): list of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        if self.mac_mode == "TSCH":
            if mac_address_list is None:
                mac_address_list = self.node_manager.mac_address_list
            param_keys = ["IEEE802154e_macHoppingSequenceList"]
            if self.hopping_sequence is None:
                ret = self.read_macconfiguration(param_keys, [mac_address_list[0]])
                if ret == -1:
                    return -1
                self.hopping_sequence = TAISCHoppingSequence.from_tuple(ret[mac_address_list[0]]["IEEE802154e_macHoppingSequenceList"])

            for channel in channel_lst:
                self.hopping_sequence[channel] = 0;

            new_hopping_sequence = [ channel for channel, available in self.hopping_sequence.items() if available ]

            # first change the length of the hopping sequence
            log.info("IEEE802154e_macHoppingSequenceLength")
            param_key_values = {"IEEE802154e_macHoppingSequenceLength": len(new_hopping_sequence)}
            ret = self.update_macconfiguration(param_key_values, mac_address_list)
            if ret == -1:
                return -1
            # now change the hopping sequence
            log.info("IEEE802154e_macHoppingSequenceList")
            log.info("New hopping scheme: {} blacklisted {}, new len {}".format(str(new_hopping_sequence), str(channel_lst), len(new_hopping_sequence)))
            param_key_values = {"IEEE802154e_macHoppingSequenceList": tuple(new_hopping_sequence)}
            ret = self.update_macconfiguration(param_key_values, mac_address_list)
            return ret
        else:
            return -1
            
    def whitelist_channels(self, channel_lst, mac_address_list=None):
        """This function allows to whitelist certain channels.

        Args:
            channel_lst (list): list of channels to be whitelisted

        Returns:
            dict: error codes from each node
        """
        if self.mac_mode == "TSCH":
            if mac_address_list is None:
                mac_address_list = self.node_manager.mac_address_list
            param_keys = ["IEEE802154e_macHoppingSequenceList"]
            if self.hopping_sequence is None:
                ret = self.read_macconfiguration(param_keys, [mac_address_list[0]])
                if ret == -1:
                    return -1
                self.hopping_sequence = TAISCHoppingSequence.from_tuple(ret[mac_address_list[0]]["IEEE802154e_macHoppingSequenceList"])

            for channel in channel_lst:
                self.hopping_sequence[channel] = 1;

            new_hopping_sequence = [ channel for channel, available in self.hopping_sequence.items() if available ]

            # first change the length of the hopping sequence
            log.info("IEEE802154e_macHoppingSequenceLength")
            param_key_values = {"IEEE802154e_macHoppingSequenceLength": len(new_hopping_sequence)}
            ret = self.update_macconfiguration(param_key_values, mac_address_list)
            if ret == -1:
                return -1
            # now change the hopping sequence
            log.info("IEEE802154e_macHoppingSequenceList")
            log.info("New hopping scheme: {} blacklisted {}, new len {}".format(str(new_hopping_sequence), str(channel_lst), len(new_hopping_sequence)))
            param_key_values = {"IEEE802154e_macHoppingSequenceList": tuple(new_hopping_sequence)}
            ret = self.update_macconfiguration(param_key_values, mac_address_list)
            return ret
        else:
            return -1
    
    def update_hopping_sequence_from_list(self, hopping_sequence_lst, mac_address_list=None):
        """This function allows to create a new hopping sequence

        Args:
            channel_lst (list): list of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        current_offset = 0
        ret_val = 0
        ret_dict = {}
        param_name = "IEEE802154e_macHoppingSequenceList"
        if self.mac_mode == "TSCH":
            if mac_address_list is None:
                mac_address_list = self.node_manager.mac_address_list
            for mac_address in self.node_manager.mac_address_list:
                ret_dict[mac_address] = 0
            
            while(current_offset < len(hopping_sequence_lst)):
                hoppingsequence_tpl = (current_offset,) + tuple(hopping_sequence_lst[current_offset:current_offset + MAX_MSG_SIZE -1])
                
                param_key_values_dict = {param_name: hoppingsequence_tpl}
                print("UPDATE : %s" % (param_key_values_dict))
                ret = self.update_macconfiguration(param_key_values_dict)
                for mac_address in ret:
                    if type(ret[mac_address]) is dict:
                        ret_dict[mac_address] += ret[mac_address][param_name]
                        ret_val += ret[mac_address][param_name]
                    else:
                        ret_dict[mac_address] += ret[mac_address]
                        ret_val += ret[mac_address]
                current_offset += len(hoppingsequence_tpl) - 1
            return ret_val
        else:
            return -1
            
    def update_hopping_sequence(self, hopping_sequence_csv, mac_address_list=None):
        """This function allows to create a new hopping sequence

        Args:
            channel_lst (list): csv of channels to be blacklisted

        Returns:
            dict: error codes from each node
        """
        hopping_sequence_lst = read_taisc_hoppingsequence(hopping_sequence_csv)
        self.update_hopping_sequence_from_list(hopping_sequence_lst, mac_address_list)
      


class taiscLinkOptions(IntEnum):
    """Possible MACLinkOptions
    """
    NOPI = 1
    IEEE802154_BEACON = 2
    SYNC = 3
    TX = 4
    RX = 5
    OFF = 6
    IEEE80211_BEACON = 8


class taiscLinkType(IntEnum):
    """Possible MacLinkTypes
    """
    NORMAL = 0
    ADVERTISING = 1
    COEXISTENCE = 2


class taiscLink(object):

    SLOT_SIZE = 6

    def __init__(self, src_address, dst_address, slot_type, channel_offset):
        self.src_address = src_address
        self.dst_address = dst_address
        self.slot_type = slot_type
        self.channel_offset = channel_offset

    def to_tuple(self):
        return (self.src_address, self.dst_address, self.slot_type, self.channel_offset)

    @staticmethod
    def from_tuple(tpl):
        return taiscLink(tpl[0], tpl[1], tpl[2], tpl[3])

    def __str__(self):
        return "{" + self.src_address + "->" + self.dst_address + ":" + str(self.slot_type) + "," + str(self.channel_offset) + "}"


class taiscSlotFrame(object):

    def __init__(self, slotframe=None):
        self.slotframe = []
        self.mac_address_list = []
        self.slotframe_length = 0
        if slotframe is not None:
            self.slotframe_length = len(slotframe)
            self.slotframe = slotframe
            for slot in self.slotframe:
                if slot.src_address not in self.mac_address_list:
                    self.mac_address_list.append(slot.src_address)
                if slot.dst_address not in self.mac_address_list and slot.dst_address != 0xFFFF:
                    self.mac_address_list.append(slot.dst_address)

    def add_slot(self, taisc_slot):
        self.slotframe.append(taisc_slot)
        self.slotframe_length += 1
        if taisc_slot.src_address not in self.mac_address_list:
            self.mac_address_list.append(taisc_slot.src_address)
        if taisc_slot.dst_address not in self.mac_address_list and taisc_slot.dst_address != 0xFFFF:
            self.mac_address_list.append(taisc_slot.dst_address)

    def to_tuple(self, slotframe_offset, max_size):
        num_slots = (max_size - 2) // taiscLink.SLOT_SIZE
        if slotframe_offset + num_slots > self.slotframe_length:
            num_slots = self.slotframe_length - slotframe_offset
        ret_tuple = (slotframe_offset, num_slots)
        for i in range(slotframe_offset, slotframe_offset + num_slots):
            ret_tuple = ret_tuple + self.slotframe[i].to_tuple()
        return ret_tuple

    @staticmethod
    def from_tuple_create(tpl):
        slotframe_offset = tpl(0)
        num_slots = tpl(1)
        taisc_slot_frame = taiscSlotFrame()
        tpl_offset = 2
        for i in range(slotframe_offset, slotframe_offset + num_slots):
            taisc_slot_frame.add_slot(taiscLink.from_tuple(tpl[tpl_offset:tpl_offset + 4]))
            tpl_offset += 4
        return taisc_slot_frame

    def from_tuple_append(self, tpl):
        slotframe_offset = tpl(0)
        num_slots = tpl(1)
        tpl_offset = 2
        for i in range(slotframe_offset, slotframe_offset + num_slots):
            self.add_slot(taiscLink.from_tuple(tpl[tpl_offset:tpl_offset + 4]))
            tpl_offset += 4
        return self

    def __str__(self):
        ret_str = "["
        for slot in self.slotframe:
            ret_str = ret_str + str(slot) + ";"
        ret_str[-1] = "]"
        return ret_str


class taiscSlot(object):

    SLOT_ITEM_SIZE = 3

    def __init__(self, slot_index, slot_option, channel_offset):
        self.slot_index = slot_index
        self.slot_option = slot_option
        self.channel_offset = channel_offset

    def to_tuple(self):
        return (self.slot_index, self.slot_option, self.channel_offset)

    @staticmethod
    def from_tuple(tpl):
        return taiscSlot(tpl[0], tpl[1], tpl[2])

    def __str__(self):
        return "{" + self.slot_index + "," + self.slot_option + "," + self.channel_offset + "}"


class taiscSlotList(object):

    def __init__(self, slot_list=None):
        self.slot_list_length = 0
        self.slot_list = []
        if slot_list is not None:
            self.slot_list_length = len(slot_list)
            self.slot_list = slot_list
        pass

    def add_slot(self, slotListItem):
        self.slot_list_length += 1
        self.slot_list.append(slotListItem)

    def clear_slot_list(self):
        self.slot_list_length = 0
        self.slot_list = []

    def to_tuple(self, slotlist_offset, max_size):
        num_slots = (max_size - 1) // taiscSlot.SLOT_ITEM_SIZE
        if slotlist_offset + num_slots > self.slot_list_length:
            num_slots = self.slot_list_length - slotlist_offset
        ret_tuple = (num_slots,)
        for i in range(slotlist_offset, slotlist_offset + num_slots):
            ret_tuple = ret_tuple + self.slot_list[i].to_tuple()
        return ret_tuple

    @staticmethod
    def from_tuple_create(tpl):
        slot_list = taiscSlotList()
        num_slots = tpl(0)
        tpl_offset = 1
        for i in range(0, num_slots):
            slot_list.add_slot(taiscSlot.from_tuple(tpl[tpl_offset:tpl_offset + 3]))
            tpl_offset += 3
        return slot_list

    def from_tuple_append(self, tpl):
        num_slots = tpl(0)
        tpl_offset = 1
        for i in range(0, num_slots):
            self.slot_list.add_slot(taiscSlot.from_tuple(tpl[tpl_offset:tpl_offset + 3]))
            tpl_offset += 3
        return self.slot_list

    def __str__(self):
        ret_string = "#slot_list_length: " + str(self.slot_list_length) + ": ["
        for i in range(0, self.slot_list_length):
            ret_string + str(self.slot_list[i]) + ","
        ret_string[-1] = "]"
        return ret_string


class TAISCHoppingSequence(object):
    """A Class representing A TSCH hopping sequence

    Attributes:
        TSCHHoppingSequenceList (list): a hopping sequence containing 802.15.4 channels.
    """

    def __init__(self, hopping_sequence_list):
        """Create a TSCH hopping sequence object.

        Args:
            TSCHHoppingSequenceList (list): a hopping sequence containing 802.15.4 channels.
        Remark:
            Hopping_sequence_dict is a dict, with key a channel, and the value to elaborate if
            the channel is available to use
        """
        self.hopping_sequence_dict = {}
        for channel in hopping_sequence_list:
            self.hopping_sequence_dict[channel] = 1

    def to_tuple(self):
        """Converts a hopping sequence to a tuple

        Returns:
            tuple: hopping sequnce in tuple format.
        """
        return tuple(self.hopping_sequence_dict.keys())

    @staticmethod
    def from_tuple(tpl):
        """Create a TSCH hopping sequence from tuple.

        Args:
            tpl (tuple): input tuple

        Returns:
            TSCHHoppingSequence: The TSCH hopping sequence
        """
        return TAISCHoppingSequence(list(tpl))

    def __str__(self):
        return str(self.hopping_sequence_dict.keys())


def read_taisc_slotframe(slotframe_csv):
    """Create TSCH slotframe from CSV file.
    """
    file_sf = None
    try:
        file_sf = open(slotframe_csv, 'rt')
        reader = csv.DictReader(file_sf)
        taisc_slotframe = taiscSlotFrame()
        for row in reader:
            # don't need to check if src and dst are in mac address list
            # reason: we update the slotframe for all nodes regardless if they are local
            src_address = int(row['macSrcNodeAddress'])
            dst_address = int(row['macDstNodeAddress'])
            taisc_slot = taiscLink(src_address, dst_address, int(row['macLinkType']), int(row['macChannelOffset']))
            taisc_slotframe.add_slot(taisc_slot)
        return taisc_slotframe
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        if file_sf is not None:
            file_sf.close()

def read_taisc_hoppingsequence(hoppingsequence_csv):
    """Create TSCH hopping sequence from CSV file.
    """
    file_sf = None
    try:
        file_sf = open(hoppingsequence_csv, 'rt')
        reader = csv.reader(file_sf, delimiter=',')
        hopping_sequence = []
        for row in reader:
            channel = int(row[0])
            hopping_sequence.append(channel)
        return hopping_sequence
    except Exception as e:
        print("An error occurred while reading parameters: %s" % e)
        return -1
    finally:
        file_sf.close()


def read_taisc_slot_list(slot_list_csv, mac_adress_list):
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
