import json
from opentrons import robot, labware, instruments

CALIBRATION_CROSS_COORDS = [380.87, 9.0, 0.0]
CALIBRATION_CROSS_SLOT = '3'
TEST_LABWARE_SLOT = CALIBRATION_CROSS_SLOT
TIPRACK_SLOT = '5'

RATE = 0.25  # % of default speeds
SLOWER_RATE = 0.1


def uniq(l):
    res = []
    for i in l:
        if i not in res:
            res.append(i)
    return res


def set_speed(rate):
    robot.head_speed(x=(600 * rate), y=(400 * rate),
                      z=(125 * rate), a=(125 * rate))


def run_custom_protocol(pipette_name, mount, tiprack_load_name, labware_def):
    tiprack = labware.load(tiprack_load_name, TIPRACK_SLOT)
    pipette = getattr(instruments, pipette_name)(mount, tip_racks=[tiprack])
    test_labware = robot.add_container_by_definition(
        labware_def,
        TEST_LABWARE_SLOT,
        label=labware_def.get('metadata', {}).get(
            'displayName', 'test labware')
    )

    num_cols = len(labware_def.get('ordering', [[]]))
    num_rows = len(labware_def.get('ordering', [[]])[0])
    well_locs = uniq([
        'A1',
        '{}{}'.format(chr(ord('A') + num_rows - 1), str(num_cols))])

    pipette.pick_up_tip()
    set_speed(RATE)

    pipette.move_to((robot.deck, CALIBRATION_CROSS_COORDS))
    robot.pause(
        f"Confirm {mount} pipette is at slot {CALIBRATION_CROSS_SLOT} calibration cross")

    pipette.retract()
    robot.pause(f"Place your labware in Slot {TEST_LABWARE_SLOT}")

    for well_loc in well_locs:
        well = test_labware.wells(well_loc)
        all_4_edges = [
            [well.from_center(x=-1, y=0, z=1), 'left'],
            [well.from_center(x=1, y=0, z=1), 'right'],
            [well.from_center(x=0, y=-1, z=1), 'front'],
            [well.from_center(x=0, y=1, z=1), 'back']
        ]

        set_speed(RATE)
        pipette.move_to(well.top())
        robot.pause("Moved to the top of the well")

        for edge_pos, edge_name in all_4_edges:
            set_speed(SLOWER_RATE)
            pipette.move_to((well, edge_pos))
            robot.pause(f'Moved to {edge_name} edge')

        set_speed(RATE)
        pipette.move_to(well.bottom())
        robot.pause("Moved to the bottom of the well")

        # need to interact with labware for it to show on deck map
        pipette.blow_out(well)


    set_speed(1.0)
    pipette.return_tip()


LABWARE_DEF = """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"4ti","brandId":["4ti-0116"]},"metadata":{"displayName":"4ti 96 Well Plate 350 µL","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.8,"yDimension":85.5,"zDimension":14.4},"wells":{"A1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":74.25,"z":2.4},"B1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":65.25,"z":2.4},"C1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":56.25,"z":2.4},"D1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":47.25,"z":2.4},"E1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":38.25,"z":2.4},"F1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":29.25,"z":2.4},"G1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":20.25,"z":2.4},"H1":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":11.25,"z":2.4},"A2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":74.25,"z":2.4},"B2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":65.25,"z":2.4},"C2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":56.25,"z":2.4},"D2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":47.25,"z":2.4},"E2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":38.25,"z":2.4},"F2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":29.25,"z":2.4},"G2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":20.25,"z":2.4},"H2":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":11.25,"z":2.4},"A3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":74.25,"z":2.4},"B3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":65.25,"z":2.4},"C3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":56.25,"z":2.4},"D3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":47.25,"z":2.4},"E3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":38.25,"z":2.4},"F3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":29.25,"z":2.4},"G3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":20.25,"z":2.4},"H3":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":11.25,"z":2.4},"A4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":74.25,"z":2.4},"B4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":65.25,"z":2.4},"C4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":56.25,"z":2.4},"D4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":47.25,"z":2.4},"E4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":38.25,"z":2.4},"F4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":29.25,"z":2.4},"G4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":20.25,"z":2.4},"H4":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":11.25,"z":2.4},"A5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":74.25,"z":2.4},"B5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":65.25,"z":2.4},"C5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":56.25,"z":2.4},"D5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":47.25,"z":2.4},"E5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":38.25,"z":2.4},"F5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":29.25,"z":2.4},"G5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":20.25,"z":2.4},"H5":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":11.25,"z":2.4},"A6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":74.25,"z":2.4},"B6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":65.25,"z":2.4},"C6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":56.25,"z":2.4},"D6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":47.25,"z":2.4},"E6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":38.25,"z":2.4},"F6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":29.25,"z":2.4},"G6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":20.25,"z":2.4},"H6":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":11.25,"z":2.4},"A7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":74.25,"z":2.4},"B7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":65.25,"z":2.4},"C7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":56.25,"z":2.4},"D7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":47.25,"z":2.4},"E7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":38.25,"z":2.4},"F7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":29.25,"z":2.4},"G7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":20.25,"z":2.4},"H7":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":11.25,"z":2.4},"A8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":74.25,"z":2.4},"B8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":65.25,"z":2.4},"C8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":56.25,"z":2.4},"D8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":47.25,"z":2.4},"E8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":38.25,"z":2.4},"F8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":29.25,"z":2.4},"G8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":20.25,"z":2.4},"H8":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":11.25,"z":2.4},"A9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":74.25,"z":2.4},"B9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":65.25,"z":2.4},"C9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":56.25,"z":2.4},"D9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":47.25,"z":2.4},"E9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":38.25,"z":2.4},"F9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":29.25,"z":2.4},"G9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":20.25,"z":2.4},"H9":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":86.4,"y":11.25,"z":2.4},"A10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":74.25,"z":2.4},"B10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":65.25,"z":2.4},"C10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":56.25,"z":2.4},"D10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":47.25,"z":2.4},"E10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":38.25,"z":2.4},"F10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":29.25,"z":2.4},"G10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":20.25,"z":2.4},"H10":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":95.4,"y":11.25,"z":2.4},"A11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":74.25,"z":2.4},"B11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":65.25,"z":2.4},"C11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":56.25,"z":2.4},"D11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":47.25,"z":2.4},"E11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":38.25,"z":2.4},"F11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":29.25,"z":2.4},"G11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":20.25,"z":2.4},"H11":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":104.4,"y":11.25,"z":2.4},"A12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":74.25,"z":2.4},"B12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":65.25,"z":2.4},"C12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":56.25,"z":2.4},"D12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":47.25,"z":2.4},"E12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":38.25,"z":2.4},"F12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":29.25,"z":2.4},"G12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":20.25,"z":2.4},"H12":{"depth":12,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":113.4,"y":11.25,"z":2.4}},"groups":[{"metadata":{"displayName":"4ti 96 Well Plate 350 µL","displayCategory":"wellPlate","wellBottomShape":"u"},"brand":{"brand":"4ti","brandId":["4ti-0116"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"4ti_96_wellplate_350ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""

PIPETTE_MOUNT = 'right'
PIPETTE_NAME = 'P1000_Single'
TIPRACK_LOADNAME = 'opentrons_96_tiprack_1000ul'

run_custom_protocol(PIPETTE_NAME, PIPETTE_MOUNT,
                    TIPRACK_LOADNAME, json.loads(LABWARE_DEF))
