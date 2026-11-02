import time

def run_placement_simulation(robot, storage, chemical):
    log = []

    log.append({"step": "arm_move_to_storage", "robot": robot.name, "target": f"rack_{storage.id}", "duration": 1.2})
    time.sleep(0.05)

    log.append({"step": "pick_chemical", "chemical": chemical.name, "duration": 0.8})
    time.sleep(0.05)

    log.append({"step": "conveyor_transfer", "from": f"rack_{storage.id}", "to": "delivery_point", "duration": 2.0})
    time.sleep(0.05)

    log.append({"step": "place_on_conveyor", "duration": 0.5})
    time.sleep(0.05)

    log.append({"step": "arm_return_home", "robot": robot.name, "duration": 1.0})
    time.sleep(0.05)

    return log

def run_slab_placement_simulation(robot, storage, chemical):
    log = []

    log.append({"step": "arm_move_to_slab", "robot": robot.name, "duration": 1.2})
    time.sleep(0.05)

    log.append({"step": "pick_from_slab", "chemical": chemical.name, "duration": 0.8})
    time.sleep(0.05)

    log.append({"step": "arm_move_to_storage", "robot": robot.name, "target": f"rack_{storage.id}", "duration": 1.2})
    time.sleep(0.05)

    log.append({"step": "place_in_rack", "chemical": chemical.name, "duration": 0.6})
    time.sleep(0.05)

    log.append({"step": "arm_return_home", "robot": robot.name, "duration": 1.0})
    time.sleep(0.05)

    return log

def run_fetch_simulation(robot, storage, chemical):
    log = []

    log.append({"step": "arm_move_to_storage", "robot": robot.name, "target": f"rack_{storage.id}", "duration": 1.2})
    time.sleep(0.05)

    log.append({"step": "pick_chemical", "chemical": chemical.name, "duration": 0.8})
    time.sleep(0.05)

    log.append({"step": "arm_move_to_conveyor", "robot": robot.name, "duration": 1.0})
    time.sleep(0.05)

    log.append({"step": "place_on_conveyor", "chemical": chemical.name, "duration": 0.6})
    time.sleep(0.05)

    log.append({"step": "arm_return_home", "robot": robot.name, "duration": 1.0})
    time.sleep(0.05)

    return log
