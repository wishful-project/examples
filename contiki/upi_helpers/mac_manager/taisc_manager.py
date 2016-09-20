from enum import IntEnum
from upi_helpers.mac_manager.mac_manager import *

MAX_MSG_SIZE = 64

class LocalTAISCMACManager(LocalMACManager):

    def __init__(self, control_engine, mac_mode):
        super(LocalTAISCMACManager, self).__init__(control_engine)
        self.mac_mode = mac_mode
        pass


class GlobalTAISCMACManager(GlobalMACManager):

    def __init__(self, control_engine, mac_mode):
        super(GlobalTAISCMACManager, self).__init__(control_engine)
        self.mac_mode = mac_mode
        pass


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
    NORMAL = 0,
    ADVERTISING = 1,
    COEXISTENCE = 2,


class taiscSlot(object):

    SLOT_SIZE = 6

    def __init__(self, src_address, dst_address, slot_type, channel_offset):
        self.src_address = src_address
        self.dst_address = dst_address
        self.slot_type = slot_type
        self.channel_offset = channel_offset

    def to_tuple(self):
        return (self.src_address, dst_address, self.slot_type, self.channel_offset)

    @staticmethod
    def from_tuple(tpl):
        return taiscSlot(tpl[0], tpl[1], tpl[2], tpl[3])

    def __str__(self):
        return "{" + format(self.src_address, '#04x') + "->" + format(self.dst_address, '#04x') + ":" + str(self.slot_type) + "," + str(self.channel_offset) + "}"


class taiscSlotFrame(object):

    def __init__(self, slotframe=None):
        self.slotframe = []
        self.mac_address_list = []
        if slotframe is not None:
            self.slotframe_length = len(slotframe)
            self.slotframe = slotframe
            for slot in slotframe:
                if slot.src_address not in mac_address_list:
                    mac_address_list.append(src_address)
                if slot.dst_address not in mac_address_list and slot.dst_address != 0xFFFF:
                    mac_address_list.append(dst_address)

    def add_slot(self, taisc_slot):
        self.slotframe.append(taisc_slot)
        self.slotframe_length += 1
        if taisc_slot.src_address not in mac_address_list:
            mac_address_list.append(src_address)
        if taisc_slot.dst_address not in mac_address_list and taisc_slot.dst_address != 0xFFFF:
            mac_address_list.append(dst_address)

    def to_tuple(self, slotframe_offset, max_size):
        num_slots = (max_size - 2) // taiscSlot.SLOT_SIZE
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
            taisc_slot_frame.add_slot(taiscSlot(tpl[tpl_offset], tpl[tpl_offset + 1],
                                                tpl[tpl_offset + 2], tpl[tpl_offset + 3]))
            tpl_offset += 4
        return taisc_slot_frame

    def from_tuple_append(self, tpl):
        slotframe_offset = tpl(0)
        num_slots = tpl(1)
        tpl_offset = 2
        for i in range(slotframe_offset, slotframe_offset + num_slots):
            self.add_slot(taiscSlot(tpl[tpl_offset], tpl[tpl_offset + 1], tpl[tpl_offset + 2], tpl[tpl_offset + 3]))
            tpl_offset += 4
        return self

    def __str__(self):
        ret_str = "["
        for slot in self.slotframe:
            ret_str = ret_str + str(slot) + ";"
        ret_str[-1] = "]"
        return ret_str


class taiscSlotListItem(object):

    SLOT_ITEM_SIZE = 3

    def __init__(self, slot_index, slot_option, channel_offset):
        self.slot_index = slot_index
        self.slot_option = slot_option
        self.channel_offset = channel_offset

    def to_tuple(self):
        return (self.slot_index, self.slot_option, self.channel_offset)

    @staticmethod
    def from_tuple(tpl):
        return taiscSlotListItem(tpl[0], tpl[1], tpl[2])

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
        num_slots = (max_size - 1) // taiscSlotListItem.SLOT_ITEM_SIZE
        if slotlist_offset + t_num_slots > self.slot_list_length:
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
            slot_list.add_slot(taiscSlotListItem.from_tuple(tpl[tpl_offset:tpl_offset + 3]))
            tpl_offset += 3
        return slot_list

    def from_tuple_append(self, tpl):
        num_slots = tpl(0)
        tpl_offset = 1
        for i in range(0, num_slots):
            self.slot_list.add_slot(taiscSlotListItem.from_tuple(tpl[tpl_offset:tpl_offset + 3]))
            tpl_offset += 3
        return self.slot_list

    def __str__(self):
        ret_string = "#slot_list_length: " + str(self.slot_list_length) + ": ["
        for i in range(0, self.slot_list_length):
            ret_string + str(self.slot_list[i]) + ","
        ret_string[-1] = "]"
        return ret_string
