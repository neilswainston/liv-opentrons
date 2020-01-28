'''
(c) University of Liverpool 2020

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
from functools import partial
import json
import os.path
import random
from urllib.request import urlopen

from opentrons import simulate

import pandas as pd


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
                 wrklst_url='http://bit.ly/genemill-ot-worklist',
                 random_dests=True):
        self.__protocol = protocol

        # Parse setup:
        with urlopen(setup_url) as setup_file:
            self.__setup = json.load(setup_file)

        # Parse csv file:
        self.__df = pd.read_csv(wrklst_url)

        # Set randomise destinations:
        self.__random_dests = random_dests

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
        self.__process_wklst()

        get_src_well = partial(
            _get_well, protocol=self.__protocol, is_src=True)

        get_dest_well = partial(
            _get_well, protocol=self.__protocol, is_src=False)

        pipette = self.__get_pipette()

        pipette.distribute(
            self.__df['vol'].tolist(),
            self.__df.apply(get_src_well, axis=1).tolist(),
            self.__df.apply(get_dest_well, axis=1).tolist(),
            touch_tip=True,
            disposal_volume=50)

    def __process_wklst(self):
        '''Process worklist.'''
        dfs = []

        if 'dest_well' not in self.__df:
            for plate, df in self.__df.groupby('dest_plate'):
                df = df.copy()
                plate = _get_obj(plate, self.__protocol)
                wells = [well for well in plate._ordering]

                if self.__random_dests:
                    random.shuffle(wells)

                df['dest_well'] = wells[:len(df.index)]
                dfs.append(df)

        self.__df = pd.concat(dfs)

    def __next_empty_slot(self):
        '''Get next empty slot.'''
        for slot, obj in self.__protocol.deck.items():
            if not obj:
                return slot

        return None

    def __get_pipette(self):
        '''Get appropriate pipette for volume.'''
        vols = self.__df['vol']

        # Ensure pipette is appropriate for minimum volume:
        valid_pipettes = \
            [pip for pip in self.__protocol.loaded_instruments.values()
             if pip.min_volume <= min(vols)]

        if not valid_pipettes:
            return None

        # Calculate number of operations per pipette:
        num_ops = {pip: sum([vol // pip.max_volume for vol in vols])
                   for pip in valid_pipettes}

        num_ops = {k: v for k, v in sorted(
            num_ops.items(), key=lambda item: item[1])}

        return next(iter(num_ops))


def _get_obj(obj_name, protocol):
    '''Get object.'''
    for val in protocol.deck.values():
        if val and val.name == obj_name:
            return val

    return None


def _get_well(row, protocol, is_src=True):
    '''Get well.'''
    prefix = 'src' if is_src else 'dest'
    plate = _get_obj(row['%s_plate' % prefix], protocol)
    well = plate[row['%s_well' % prefix]]

    top = '%s_top' % prefix
    bottom = '%s_bottom' % prefix

    if top in row:
        well.top(row[top])
    elif bottom in row:
        well.bottom(row[bottom])

    return well


def main():
    '''main method.'''
    filename = os.path.realpath(__file__)

    with open(filename) as protocol_file:
        runlog, _ = simulate.simulate(protocol_file, filename)
        print(simulate.format_runlog(runlog))


if __name__ == '__main__':
    main()
