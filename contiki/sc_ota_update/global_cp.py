#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_cp.py: Example Contiki global control program

Usage:
   global_cp.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path
   --nodes nodesFile   Config file with node info
   --measurements measurements Config file with measurement info
   --elf-files elfFiles ELF file that need to be linked, uploaded and installed (seperated with semicolons)
   --elf-firmware elfFirmware ELF firmware used to link the ELF file.

Example:
   python sc_ota_update/global_cp.py --config config/localhost/global_cp_config.yaml --nodes config/portable/nodes.yaml --measurements config/portable/measurement_config.yaml --elf-files tdma_uppermac.o;slotted_protocol.o -- elf-firmware udp-example.elf

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""
import datetime
import logging
from contiki.contiki_helpers.global_node_manager import GlobalNodeManager
from contiki.contiki_helpers.taisc_manager import TAISCMACManager
from contiki.contiki_helpers.app_manager import AppManager
import yaml
import gevent
from measurement_logger import MeasurementLogger
from elftools.elf.elffile import ELFFile
import subprocess

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2017, IMEC"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@intec.ugent.be"


def __calculate_alignment_overhead(size):
        if size % 4 == 0:
            return 0
        else:
            return 4 - (size % 4)


def calculate_elf_filesizes(elf_object_files):
    text_size = rodata_size = data_size = bss_size = 0
    elf_fileheader_size = 52
    elf_sectionheaders_size = 2 * 40  # NULL section header + shstrtab section header
    elf_shstrtab_size = 11  # NULL section header and shstrtab section header
    elf_programheaders_size = 0
    alignement_overhead = 0
    has_rom_program_header = False
    has_ram_program_header = False
    for elf_object_file in elf_object_files:
        with open(elf_object_file, 'rb') as f:
            elffile = ELFFile(f)
            # determine rom size
            text_section = elffile.get_section_by_name('.text')
            if text_section is not None:
                text_size += text_section['sh_size']
                elf_sectionheaders_size += 40  # section header
                elf_shstrtab_size += 6  # shstrtab
                has_rom_program_header = True
            rodata_section = elffile.get_section_by_name('.rodata')
            if rodata_section is not None:
                rodata_size += rodata_section['sh_size']
                elf_sectionheaders_size += 40  # section header
                elf_shstrtab_size += 8  # shstrtab
                has_rom_program_header = True
            # determine ram size
            data_section = elffile.get_section_by_name('.data')
            if data_section is not None:
                data_size += data_section['sh_size']
                elf_sectionheaders_size += 40  # section header
                elf_shstrtab_size += 6  # shstrtab
                has_ram_program_header = True
            bss_section = elffile.get_section_by_name('.bss')
            if bss_section is not None:
                bss_size += bss_section['sh_size']
                elf_sectionheaders_size += 40  # section header
                elf_shstrtab_size += 5  # shstrtab
                has_ram_program_header = True
            if has_rom_program_header:
                elf_programheaders_size += 32
            if has_ram_program_header:
                elf_programheaders_size += 32
    alignement_overhead += __calculate_alignment_overhead(text_size)
    alignement_overhead += __calculate_alignment_overhead(rodata_size)
    alignement_overhead += __calculate_alignment_overhead(data_size)
    alignement_overhead += __calculate_alignment_overhead(elf_shstrtab_size)
    elf_file_size = elf_fileheader_size + elf_programheaders_size + text_size + rodata_size + data_size + elf_shstrtab_size + elf_sectionheaders_size
    return [elf_file_size, text_size + rodata_size, data_size + bss_size]


def prepare_software_module(elf_firmware, elf_object_files, rom_start_addr, ram_start_addr, init_function):
    """This functions links a new software module to an existing firmware based on the memory allocated using the ‘allocate_memory’ function.

    Args:
        elf_firmware (file): The firmware running on the nodes.
        elf_object_file (file): The new/updated ELF object file.
        rom_start_addr (int): Start address in ROM for the new object file.
        ram_start_addr (int): Start address in RAM for the new object file.
        init_function (string): The init function that must be called when activating the module.

    Returns:
        int: Error value 0 = SUCCESS; -1 = FAIL
    """
    # first merge the elf object files
    elf_objects = []
    if type(elf_object_files) is str:
        elf_objects[0] = elf_object_files
    else:
        elf_objects = elf_object_files
    linker_cmd = '../../agent_modules/contiki/wishful_module_gitar/linker_script.sh ' + elf_objects[0] + ' ../../agent_modules/contiki/wishful_module_gitar/merge_rodata_script ' + elf_firmware + ' ' + init_function
    for elf_object in range(1, len(elf_objects)):
        linker_cmd = linker_cmd + ' ' + elf_object
    subprocess.call(linker_cmd)
    return


def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))


def event_cb(mac_address, event_name, event_value):
    measurement_logger.log_measurement(event_name, event_value)
    # print("{} Node {} Event {}: {} ".format(datetime.datetime.now(), mac_address, event_name, event_value))


def main(args, log, global_node_manager, measurement_logger):
    # get the elf files and firmware from the arguments
    elf_files = args['--elf-files'].split(';')
    elf_firmware = args['--elf-firmware']
    log.info(elf_files)
    log.info(elf_firmware)

    # now configure the nodes normally
    contiki_nodes = global_node_manager.get_mac_address_list()
    print("Connected nodes", [str(node) for node in contiki_nodes])
    taisc_manager = TAISCMACManager(global_node_manager, "CSMA")
    app_manager = AppManager(global_node_manager)
    ret = taisc_manager.update_slotframe('./mac_switching/taisc_slotframe.csv')
    log.info(ret)
    ret = taisc_manager.update_macconfiguration({'IEEE802154_macSlotframeSize': len(contiki_nodes)})
    log.info(ret)

    border_router_id = 1
    log.info("Set node %d as border router" % (border_router_id))
    app_manager.rpl_set_border_router([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01], border_router_id)

    global_node_manager.start_local_monitoring_cp()
    gevent.sleep(5)
    taisc_manager.subscribe_events(["IEEE802154_event_macStats"], event_cb, 0)
    gevent.sleep(5)

    log.info("Activating server")
    app_manager.update_configuration({"app_activate": 1}, [border_router_id])
    log.info("Activating clients")
    app_manager.update_configuration({"app_activate": 2}, range(2, len(global_node_manager.get_mac_address_list()) + 1))

    


if __name__ == "__main__":
    try:
        from docopt import docopt
    except Exception:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise
    args = docopt(__doc__, version=__version__)

    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']
    logging.basicConfig(filename=logfile, level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')
    log = logging.getLogger('SC OTA update')

    log.debug(args)
    try:
        config_file_path = args['--config']
        config = None
        with open(config_file_path, 'r') as f:
            config = yaml.load(f)
        global_node_manager = GlobalNodeManager(config)
        global_node_manager.set_default_callback(default_callback)

        nodes_file_path = args['--nodes']
        with open(nodes_file_path, 'r') as f:
            node_config = yaml.load(f)
        global_node_manager.wait_for_agents(node_config['ip_address_list'])

        measurements_file_path = args['--measurements']
        with open(measurements_file_path, 'r') as f:
            measurement_config = yaml.load(f)
        measurement_logger = MeasurementLogger.load_config(measurement_config)

        main(args, global_node_manager, measurement_logger)
    except KeyboardInterrupt:
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        measurement_logger.stop_logging()
        global_node_manager.stop()
