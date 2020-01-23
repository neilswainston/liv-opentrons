'''
(c) University of Liverpool 2020

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
import csv
import os.path

from opentrons import protocol_api, simulate


metadata = {'apiLevel': '2.0'}


def run(protocol: protocol_api.ProtocolContext):
    '''Run protocol.'''
    writer = ProtocolWriter(protocol,
                            csv_filename='data/worklist.csv',
                            tip_rack_type='opentrons_96_tiprack_300ul',
                            pipettes={'left': 'p1000_single'})
    writer.write()

    # p300.transfer(100, plate['A1'], plate['B1'])


class ProtocolWriter():
    '''Class to write protocol from CSV file.'''

    def __init__(self, protocol,
                 csv_filename,
                 tip_rack_type,
                 pipettes):
        self.__protocol = protocol

        # Parse csv file:
        self.__hdr_idxs, self.__rows = read_csv(csv_filename)

        self.__tip_rack_type = tip_rack_type
        self.__pipettes = pipettes

    def write(self):
        '''Write protocol.'''

        #`Setup tip_racks, ensuring a sufficient number:
        tip_racks = []

        while sum([len(tip_rack._wells) for tip_rack in tip_racks]) < len(self.__rows):
            tip_racks.append(self.__protocol.load_labware(self.__tip_rack_type,
                                                          next_empty_slot(self.__protocol)))

        # Setup pipettes:
        for mount, instrument_name in self.__pipettes.items():
            self.__protocol.load_instrument(
                instrument_name, mount, tip_racks=tip_racks)

        # Add functions:
        for row in self.__rows:
            src_plate, dest_plate = self.__add_plates(row)
            vol = float(row[self.__hdr_idxs['vol']])
            pipette = get_pipette(vol, self.__protocol)

            pipette.transfer(
                vol,
                src_plate[row[self.__hdr_idxs['src_well']]],
                dest_plate[row[self.__hdr_idxs['dest_well']]])

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
                                  for key in ['dest_plate_name', 'dest_plate_type']]

        obj = get_obj(row[name_idx], self.__protocol)

        if obj:
            return obj

        return self.__protocol.load_labware(row[type_idx],
                                            next_empty_slot(self.__protocol),
                                            row[name_idx])


def read_csv(filename, delimiter=','):
    '''Read csv.'''
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)

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


def get_pipette(vol, protocol):
    '''Get appropriate pipette for volume.'''
    valid_pipettes = [pip for pip in protocol.loaded_instruments.values()
                      if pip.min_volume <= vol <= pip.max_volume]

    return valid_pipettes[0] if valid_pipettes else None


def main():
    '''main method.'''
    filename = os.path.realpath(__file__)

    with open(filename) as protocol_file:
        runlog, _ = simulate.simulate(protocol_file, filename)
        print(simulate.format_runlog(runlog))


if __name__ == '__main__':
    main()
