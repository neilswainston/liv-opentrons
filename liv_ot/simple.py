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
import sys

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
        headers, self.__rows = _read_csv(csv_filename)

        self.__tip_rack_type = tip_rack_type
        self.__pipettes = pipettes

        # Get indexes of csv columns:
        self.__src_plate_name_idx = headers.index('src_plate_name')
        self.__dest_plate_name_idx = headers.index('dest_plate_name')
        self.__src_plate_type_idx = headers.index('src_plate_type')
        self.__dest_plate_type_idx = headers.index('dest_plate_type')

    def write(self):
        '''Write protocol.'''

        #`Setup tip_racks, ensuring a sufficient number:
        tip_racks = []

        while sum([len(tip_rack._wells) for tip_rack in tip_racks]) < len(self.__rows):
            tip_racks.append(self.__protocol.load_labware(self.__tip_rack_type,
                                                          _next_empty_slot(self.__protocol)))

        # Setup pipettes:
        for mount, instrument_name in self.__pipettes.items():
            self.__protocol.load_instrument(
                instrument_name, mount, tip_racks=tip_racks)

        # Add functions:
        for row in self.__rows:
            self.__add_plates(row)

    def __add_plates(self, row):
        '''Add plates.'''

        if not _is_added(row[self.__src_plate_name_idx], self.__protocol):
            # Add plate:
            self.__protocol.load_labware(row[self.__src_plate_type_idx],
                                         _next_empty_slot(self.__protocol),
                                         row[self.__src_plate_name_idx])
        if not _is_added(row[self.__dest_plate_name_idx], self.__protocol):
            # Add plate:
            self.__protocol.load_labware(row[self.__dest_plate_type_idx],
                                         _next_empty_slot(self.__protocol),
                                         row[self.__dest_plate_name_idx])


def _read_csv(filename):
    '''Read csv.'''
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        header_line = True
        headers = None
        rows = []

        for row in csv_reader:
            if header_line:
                headers = row
                header_line = False
            else:
                rows.append(row)

    return headers, rows


def _next_empty_slot(protocol):
    '''Get next empty slot.'''
    for slot, obj in protocol.deck.items():
        if not obj:
            return slot

    return None


def _is_added(obj_name, protocol):
    '''Check if named object has been added to the deck.'''
    obj_names = [val.name for val in protocol.deck.values() if val]
    return obj_name in obj_names


def main(args):
    '''main method.'''
    filename = os.path.realpath(__file__)

    with open(filename) as protocol_file:
        runlog = simulate.simulate(protocol_file, filename)
        print(simulate.format_runlog(runlog))


if __name__ == '__main__':
    main(sys.argv[1:])
