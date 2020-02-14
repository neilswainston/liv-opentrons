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


LABWARE_DEF = """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1"],["A2","B2","C2","D2","E2","F2","G2","H2"],["A3","B3","C3","D3","E3","F3","G3","H3"],["A4","B4","C4","D4","E4","F4","G4","H4"],["A5","B5","C5","D5","E5","F5","G5","H5"],["A6","B6","C6","D6","E6","F6","G6","H6"],["A7","B7","C7","D7","E7","F7","G7","H7"],["A8","B8","C8","D8","E8","F8","G8","H8"],["A9","B9","C9","D9","E9","F9","G9","H9"],["A10","B10","C10","D10","E10","F10","G10","H10"],["A11","B11","C11","D11","E11","F11","G11","H11"],["A12","B12","C12","D12","E12","F12","G12","H12"]],"brand":{"brand":"AxyGen","brandId":["Thermo Scientific AB-0564"]},"metadata":{"displayName":"AxyGen 96 Well Plate 1200 µL","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":42.5},"wells":{"A1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":74.24,"z":3.15},"B1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":65.24,"z":3.15},"C1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":56.24,"z":3.15},"D1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":47.24,"z":3.15},"E1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":38.24,"z":3.15},"F1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":29.24,"z":3.15},"G1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":20.24,"z":3.15},"H1":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":14.38,"y":11.24,"z":3.15},"A2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":74.24,"z":3.15},"B2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":65.24,"z":3.15},"C2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":56.24,"z":3.15},"D2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":47.24,"z":3.15},"E2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":38.24,"z":3.15},"F2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":29.24,"z":3.15},"G2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":20.24,"z":3.15},"H2":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":23.38,"y":11.24,"z":3.15},"A3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":74.24,"z":3.15},"B3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":65.24,"z":3.15},"C3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":56.24,"z":3.15},"D3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":47.24,"z":3.15},"E3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":38.24,"z":3.15},"F3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":29.24,"z":3.15},"G3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":20.24,"z":3.15},"H3":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":32.38,"y":11.24,"z":3.15},"A4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":74.24,"z":3.15},"B4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":65.24,"z":3.15},"C4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":56.24,"z":3.15},"D4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":47.24,"z":3.15},"E4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":38.24,"z":3.15},"F4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":29.24,"z":3.15},"G4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":20.24,"z":3.15},"H4":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":41.38,"y":11.24,"z":3.15},"A5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":74.24,"z":3.15},"B5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":65.24,"z":3.15},"C5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":56.24,"z":3.15},"D5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":47.24,"z":3.15},"E5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":38.24,"z":3.15},"F5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":29.24,"z":3.15},"G5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":20.24,"z":3.15},"H5":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":50.38,"y":11.24,"z":3.15},"A6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":74.24,"z":3.15},"B6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":65.24,"z":3.15},"C6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":56.24,"z":3.15},"D6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":47.24,"z":3.15},"E6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":38.24,"z":3.15},"F6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":29.24,"z":3.15},"G6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":20.24,"z":3.15},"H6":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":59.38,"y":11.24,"z":3.15},"A7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":74.24,"z":3.15},"B7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":65.24,"z":3.15},"C7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":56.24,"z":3.15},"D7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":47.24,"z":3.15},"E7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":38.24,"z":3.15},"F7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":29.24,"z":3.15},"G7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":20.24,"z":3.15},"H7":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":68.38,"y":11.24,"z":3.15},"A8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":74.24,"z":3.15},"B8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":65.24,"z":3.15},"C8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":56.24,"z":3.15},"D8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":47.24,"z":3.15},"E8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":38.24,"z":3.15},"F8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":29.24,"z":3.15},"G8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":20.24,"z":3.15},"H8":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":77.38,"y":11.24,"z":3.15},"A9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":74.24,"z":3.15},"B9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":65.24,"z":3.15},"C9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":56.24,"z":3.15},"D9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":47.24,"z":3.15},"E9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":38.24,"z":3.15},"F9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":29.24,"z":3.15},"G9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":20.24,"z":3.15},"H9":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":86.38,"y":11.24,"z":3.15},"A10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":74.24,"z":3.15},"B10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":65.24,"z":3.15},"C10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":56.24,"z":3.15},"D10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":47.24,"z":3.15},"E10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":38.24,"z":3.15},"F10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":29.24,"z":3.15},"G10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":20.24,"z":3.15},"H10":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":95.38,"y":11.24,"z":3.15},"A11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":74.24,"z":3.15},"B11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":65.24,"z":3.15},"C11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":56.24,"z":3.15},"D11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":47.24,"z":3.15},"E11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":38.24,"z":3.15},"F11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":29.24,"z":3.15},"G11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":20.24,"z":3.15},"H11":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":104.38,"y":11.24,"z":3.15},"A12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":74.24,"z":3.15},"B12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":65.24,"z":3.15},"C12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":56.24,"z":3.15},"D12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":47.24,"z":3.15},"E12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":38.24,"z":3.15},"F12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":29.24,"z":3.15},"G12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":20.24,"z":3.15},"H12":{"depth":39.35,"totalLiquidVolume":1200,"shape":"circular","diameter":7,"x":113.38,"y":11.24,"z":3.15}},"groups":[{"metadata":{"displayName":"AxyGen 96 Well Plate 1200 µL","displayCategory":"wellPlate","wellBottomShape":"u"},"brand":{"brand":"AxyGen","brandId":["Thermo Scientific AB-0564"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","A2","B2","C2","D2","E2","F2","G2","H2","A3","B3","C3","D3","E3","F3","G3","H3","A4","B4","C4","D4","E4","F4","G4","H4","A5","B5","C5","D5","E5","F5","G5","H5","A6","B6","C6","D6","E6","F6","G6","H6","A7","B7","C7","D7","E7","F7","G7","H7","A8","B8","C8","D8","E8","F8","G8","H8","A9","B9","C9","D9","E9","F9","G9","H9","A10","B10","C10","D10","E10","F10","G10","H10","A11","B11","C11","D11","E11","F11","G11","H11","A12","B12","C12","D12","E12","F12","G12","H12"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"axygen_96_wellplate_1200ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""

PIPETTE_MOUNT = 'right'
PIPETTE_NAME = 'P1000_Single'
TIPRACK_LOADNAME = 'opentrons_96_tiprack_1000ul'

run_custom_protocol(PIPETTE_NAME, PIPETTE_MOUNT,
                    TIPRACK_LOADNAME, json.loads(LABWARE_DEF))
