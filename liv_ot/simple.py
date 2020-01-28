'''
(c) University of Liverpool 2020

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
import csv
import json
import os.path
from urllib.request import urlopen

from opentrons import simulate


metadata = {'apiLevel': '2.0',
            'author': 'Neil Swainston <neil.swainston@liverpool.ac.uk>',
            'description': 'simple'}


def run(protocol):
    '''Run protocol.'''
    writer = ProtocolWriter(protocol)
    writer.write()


class ProtocolWriter():
    '''Class to write protocol from CSV file.'''

    def __init__(self, protocol,
                 setup_url='http://bit.ly/genemill-ot-setup',
                 wrklst_url='http://bit.ly/genemill-ot-worklist'):
        self.__protocol = protocol

        # Parse setup:
        with urlopen(setup_url) as setup_file:
            self.__setup = json.load(setup_file)

        # Parse csv file:
        self.__hdr_idxs, self.__rows = read_csv(wrklst_url)

    def write(self):
        '''Write protocol.'''

        # Setup:
        self.__do_setup()

        # Add functions:
        self.__add_funcs()

    def __do_setup(self):
        '''Setup.'''

        # Setup tip racks:
        tip_racks = self.__add_tip_racks()

        # Setup pipettes:
        self.__add_pipettes(tip_racks)

        # Setup plates:
        self.__add_plates()

    def __add_tip_racks(self):
        '''Add tip racks.'''
        tip_racks = {}

        for tip_rack_def in self.__setup['tip_racks']:
            tip_rack = self.__protocol.load_labware(
                tip_rack_def['type'],
                self.__next_empty_slot())
            tip_racks[tip_rack] = tip_rack_def.get('start_at_tip', 'A1')

        return tip_racks

    def __add_pipettes(self, tip_racks):
        '''Add pipettes.'''
        for mount, instrument_name in self.__setup['pipettes'].items():
            pipette = self.__protocol.load_instrument(
                instrument_name, mount, tip_racks=list(tip_racks))

            for tip_rack, start_at_tip in tip_racks.items():
                pipette.starting_tip = tip_rack[start_at_tip]

    def __add_plates(self):
        '''Add plates.'''
        for plate in self.__setup['plates']:
            self.__protocol.load_labware(plate['type'],
                                         self.__next_empty_slot(),
                                         plate['name'])

    def __add_funcs(self):
        '''Add functions.'''
        src_plates = []
        dest_plates = []
        src_wells = []
        dest_wells = []
        vols = []
        tops = []

        for row in self.__rows:
            src_plate = get_obj(
                row[self.__hdr_idxs['src_plate']], self.__protocol)
            dest_plate = get_obj(
                row[self.__hdr_idxs['dest_plate']], self.__protocol)
            src_plates.append(src_plate)
            dest_plates.append(dest_plate)
            src_wells.append(row[self.__hdr_idxs['src_well']])
            dest_wells.append(row[self.__hdr_idxs['dest_well']])
            vols.append(float(row[self.__hdr_idxs['vol']]))

            if 'dest_top' in self.__hdr_idxs:
                tops.append(float(row[self.__hdr_idxs['dest_top']]))

        pipette = get_pipette(vols, self.__protocol)

        if tops:
            dests = \
                [plate[well].top(top)
                 for plate, well, top in zip(dest_plates, dest_wells, tops)]
        else:
            dests = [plate[well]
                     for plate, well in zip(dest_plates, dest_wells)]

        pipette.distribute(
            vols,
            [plate[well] for plate, well in zip(src_plates, src_wells)],
            dests,
            touch_tip=True,
            disposal_volume=50)

    def __next_empty_slot(self):
        '''Get next empty slot.'''
        for slot, obj in self.__protocol.deck.items():
            if not obj:
                return slot

        return None


def read_csv(csv_url):
    '''Read csv.'''
    with urlopen(csv_url) as csv_file:
        csv_reader = csv.reader(csv_file.read().decode().splitlines())

        header_line = True
        headers = None
        rows = []

        for row in csv_reader:
            if header_line:
                headers = row
                header_line = False
            else:
                rows.append(row)

        return {header: idx for idx, header in enumerate(headers)}, rows


def get_obj(obj_name, protocol):
    '''Get object.'''
    for val in protocol.deck.values():
        if val and val.name == obj_name:
            return val

    return None


def get_pipette(vols, protocol):
    '''Get appropriate pipette for volume.'''

    # Ensure pipette is appropriate for minimum volume:
    valid_pipettes = [pip for pip in protocol.loaded_instruments.values()
                      if pip.min_volume <= min(vols)]

    if not valid_pipettes:
        return None

    # Calculate number of operations per pipette:
    num_ops = {pip: sum([vol // pip.max_volume for vol in vols])
               for pip in valid_pipettes}

    num_ops = {k: v for k, v in sorted(
        num_ops.items(), key=lambda item: item[1])}

    return next(iter(num_ops))


def main():
    '''main method.'''
    filename = os.path.realpath(__file__)

    with open(filename) as protocol_file:
        runlog, _ = simulate.simulate(protocol_file, filename)
        print(simulate.format_runlog(runlog))


if __name__ == '__main__':
    main()
