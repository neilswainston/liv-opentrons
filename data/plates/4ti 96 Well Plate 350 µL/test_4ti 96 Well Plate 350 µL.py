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


LABWARE_DEF = """{"ordering":[["A1","B1","C1","D1","E1","F1","G1","H1","I1","J1","K1","L1"],["A2","B2","C2","D2","E2","F2","G2","H2","I2","J2","K2","L2"],["A3","B3","C3","D3","E3","F3","G3","H3","I3","J3","K3","L3"],["A4","B4","C4","D4","E4","F4","G4","H4","I4","J4","K4","L4"],["A5","B5","C5","D5","E5","F5","G5","H5","I5","J5","K5","L5"],["A6","B6","C6","D6","E6","F6","G6","H6","I6","J6","K6","L6"],["A7","B7","C7","D7","E7","F7","G7","H7","I7","J7","K7","L7"],["A8","B8","C8","D8","E8","F8","G8","H8","I8","J8","K8","L8"]],"brand":{"brand":"4ti","brandId":["4ti-0116"]},"metadata":{"displayName":"4ti 96 Well Plate 350 µL","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.8,"yDimension":85.5,"zDimension":14.4},"wells":{"A1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":74.25,"z":2},"B1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":65.25,"z":2},"C1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":56.25,"z":2},"D1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":47.25,"z":2},"E1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":38.25,"z":2},"F1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":29.25,"z":2},"G1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":20.25,"z":2},"H1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":11.25,"z":2},"I1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":2.25,"z":2},"J1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":-6.75,"z":2},"K1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":-15.75,"z":2},"L1":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":14.4,"y":-24.75,"z":2},"A2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":74.25,"z":2},"B2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":65.25,"z":2},"C2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":56.25,"z":2},"D2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":47.25,"z":2},"E2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":38.25,"z":2},"F2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":29.25,"z":2},"G2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":20.25,"z":2},"H2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":11.25,"z":2},"I2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":2.25,"z":2},"J2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":-6.75,"z":2},"K2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":-15.75,"z":2},"L2":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":23.4,"y":-24.75,"z":2},"A3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":74.25,"z":2},"B3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":65.25,"z":2},"C3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":56.25,"z":2},"D3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":47.25,"z":2},"E3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":38.25,"z":2},"F3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":29.25,"z":2},"G3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":20.25,"z":2},"H3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":11.25,"z":2},"I3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":2.25,"z":2},"J3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":-6.75,"z":2},"K3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":-15.75,"z":2},"L3":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":32.4,"y":-24.75,"z":2},"A4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":74.25,"z":2},"B4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":65.25,"z":2},"C4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":56.25,"z":2},"D4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":47.25,"z":2},"E4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":38.25,"z":2},"F4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":29.25,"z":2},"G4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":20.25,"z":2},"H4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":11.25,"z":2},"I4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":2.25,"z":2},"J4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":-6.75,"z":2},"K4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":-15.75,"z":2},"L4":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":41.4,"y":-24.75,"z":2},"A5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":74.25,"z":2},"B5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":65.25,"z":2},"C5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":56.25,"z":2},"D5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":47.25,"z":2},"E5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":38.25,"z":2},"F5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":29.25,"z":2},"G5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":20.25,"z":2},"H5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":11.25,"z":2},"I5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":2.25,"z":2},"J5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":-6.75,"z":2},"K5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":-15.75,"z":2},"L5":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":50.4,"y":-24.75,"z":2},"A6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":74.25,"z":2},"B6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":65.25,"z":2},"C6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":56.25,"z":2},"D6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":47.25,"z":2},"E6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":38.25,"z":2},"F6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":29.25,"z":2},"G6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":20.25,"z":2},"H6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":11.25,"z":2},"I6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":2.25,"z":2},"J6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":-6.75,"z":2},"K6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":-15.75,"z":2},"L6":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":59.4,"y":-24.75,"z":2},"A7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":74.25,"z":2},"B7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":65.25,"z":2},"C7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":56.25,"z":2},"D7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":47.25,"z":2},"E7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":38.25,"z":2},"F7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":29.25,"z":2},"G7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":20.25,"z":2},"H7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":11.25,"z":2},"I7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":2.25,"z":2},"J7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":-6.75,"z":2},"K7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":-15.75,"z":2},"L7":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":68.4,"y":-24.75,"z":2},"A8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":74.25,"z":2},"B8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":65.25,"z":2},"C8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":56.25,"z":2},"D8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":47.25,"z":2},"E8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":38.25,"z":2},"F8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":29.25,"z":2},"G8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":20.25,"z":2},"H8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":11.25,"z":2},"I8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":2.25,"z":2},"J8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":-6.75,"z":2},"K8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":-15.75,"z":2},"L8":{"depth":12.4,"totalLiquidVolume":350,"shape":"circular","diameter":85,"x":77.4,"y":-24.75,"z":2}},"groups":[{"metadata":{"displayName":"4ti 96 Well Plate 350 µL","displayCategory":"wellPlate","wellBottomShape":"u"},"brand":{"brand":"4ti","brandId":["4ti-0116"]},"wells":["A1","B1","C1","D1","E1","F1","G1","H1","I1","J1","K1","L1","A2","B2","C2","D2","E2","F2","G2","H2","I2","J2","K2","L2","A3","B3","C3","D3","E3","F3","G3","H3","I3","J3","K3","L3","A4","B4","C4","D4","E4","F4","G4","H4","I4","J4","K4","L4","A5","B5","C5","D5","E5","F5","G5","H5","I5","J5","K5","L5","A6","B6","C6","D6","E6","F6","G6","H6","I6","J6","K6","L6","A7","B7","C7","D7","E7","F7","G7","H7","I7","J7","K7","L7","A8","B8","C8","D8","E8","F8","G8","H8","I8","J8","K8","L8"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"4ti_96_wellplate_350ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""

PIPETTE_MOUNT = 'right'
PIPETTE_NAME = 'P1000_Single'
TIPRACK_LOADNAME = 'opentrons_96_tiprack_1000ul'

run_custom_protocol(PIPETTE_NAME, PIPETTE_MOUNT,
                    TIPRACK_LOADNAME, json.loads(LABWARE_DEF))
