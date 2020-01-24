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
        src_plates = []
        dst_plates = []
        src_wells = []
        dst_wells = []
        vols = []

        for row in self.__rows:
            src_plate, dst_plate = self.__add_plates(row)
            src_plates.append(src_plate)
            dst_plates.append(dst_plate)
            src_wells.append(row[self.__hdr_idxs['src_well']])
            dst_wells.append(row[self.__hdr_idxs['dst_well']])
            vols.append(float(row[self.__hdr_idxs['vol']]))

        pipette = get_pipette(vols, self.__protocol)

        # if len(set(src_plates)) == 1 and len(set(src_wells)):

        pipette.transfer(
            vols,
            [plate[well] for plate, well in zip(src_plates, src_wells)],
            [plate[well] for plate, well in zip(dst_plates, dst_wells)])

    def __do_setup(self):
        '''Setup.'''
        #`Setup tip_racks, ensuring a sufficient number:
        tip_racks = []

        while sum([len(tip_rack._wells) for tip_rack in tip_racks]) < len(self.__rows):
            tip_racks.append(self.__protocol.load_labware(self.__setup['tip_rack_type'],
                                                          next_empty_slot(self.__protocol)))

        # Setup pipettes:
        for mount, instrument_name in self.__setup['pipettes'].items():
            self.__protocol.load_instrument(
                instrument_name, mount, tip_racks=tip_racks)

    def __add_plates(self, row):
        '''Add plates.'''
        src = self.__add_plate(row, True)
        dest = self.__add_plate(row, False)

        return src, dest

    def __add_plate(self, row, is_src):
        '''Add plate.'''
        if is_src:
            name_idx, type_idx = [self.__hdr_idxs[key]
                                  for key in ['src_plate_name', 'src_plate_type']]
        else:
            name_idx, type_idx = [self.__hdr_idxs[key]
                                  for key in ['dst_plate_name', 'dst_plate_type']]

        obj = get_obj(row[name_idx], self.__protocol)

        if obj:
            return obj

        return self.__protocol.load_labware(row[type_idx],
                                            next_empty_slot(self.__protocol),
                                            row[name_idx])


def read_csv(wrklst_url):
    '''Read csv.'''
    with urlopen(wrklst_url) as wrklst_file:
        csv_reader = csv.reader(wrklst_file.read().decode().splitlines())

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


def next_empty_slot(protocol):
    '''Get next empty slot.'''
    for slot, obj in protocol.deck.items():
        if not obj:
            return slot

    return None


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
