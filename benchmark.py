import math
import os
import json
import time
from datetime import datetime

from cloudpendulumclient.benchmark.control_loop import ControlLoop
from cloudpendulumclient.benchmark.evaluators.goal_height_evaluator import GoalHeightEvaluator
from cloudpendulumclient.disturbance import StateDependentPositionDisturbance, StateDependentTorqueDisturbance

from controller.pid_controller import PointPIDController

user_token = "USER TOKEN"
cell_ids = [
    201, 202, 203, 204,
]
experiment_time = 20.0
experiment_type = "DoublePendulum"
delta_time = 0.002
num_actuators = 2
EvaluatorType = GoalHeightEvaluator
ControllerType = PointPIDController

disturbances = []
for i in range(8*3):
    i_inner = int(math.floor(i / 3))
    i_outer = int(i % 3)
    p_inner = float(i_inner) * math.pi / 4.0
    p_outer = [0.0, -math.pi/2.0, math.pi/2.0][i_outer]
    disturbances.append(StateDependentPositionDisturbance(
        wait_at_target_seconds=3.0,
        goal_position=[math.pi, 0.0],
        disturbance_position=[p_inner, p_outer],
        target_pos_threshold=0.3,
        target_vel_threshold=50.0,
    ))

for t in [0.02, 0.04, 0.06, 0.08, 0.1, -0.02, -0.04, -0.06, -0.08, -0.1]:
    disturbances.append(StateDependentTorqueDisturbance(
        wait_at_target_seconds=3.0,
        goal_position=[math.pi, 0.0],
        torque=[t, 0.0],
        duration=0.1,
        target_pos_threshold=0.3,
        target_vel_threshold=50.0,
    ))

for i in range(20):
    disturbances.append(StateDependentTorqueDisturbance(
        wait_at_target_seconds=0.2,
        goal_position=[0.0, 0.0],
        torque=[0.01, 0.0],
        duration=0.1,
        target_pos_threshold = 1000.0,
        target_vel_threshold=50.0,
    ))

out_dir = "output/" + "benchmark_" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
os.makedirs(out_dir, exist_ok=True)
with open(out_dir + "/params.json", "w") as f:
    f.write(json.dumps({
        "user_token": user_token,
        "cell_ids": cell_ids,
        "experiment_time": experiment_time,
        "experiment_type": experiment_type,
        "disturbances": str(disturbances),
    }))

iteration_data = []
results = []
for cell_id in cell_ids:
    position_history = [[] for _ in range(num_actuators)]
    velocity_history = [[] for _ in range(num_actuators)]
    torque_history = [[] for _ in range(num_actuators)]
    controller_output_history = [[] for _ in range(num_actuators)]
    time_history = []

    results.append({})
    results[-1]['cell_id'] = cell_id
    results[-1]['exception'] = None

    try:
        controller = ControllerType()
        evaluator = EvaluatorType()
        control_loop = ControlLoop(
            user_token = user_token,
            experiment_time = experiment_time,
            experiment_type = experiment_type,
            dt = delta_time,
            cell_id = cell_id,
            disturbances = disturbances,
        )
        control_loop.start()

        while not control_loop.finished():
            state = control_loop.get_state()
            torque = control_loop.get_torque()
            control_loop_time = control_loop.time()

            controller_output = controller.get_control_output(state)
            evaluator.evaluate(state, controller_output, control_loop_time)

            for i in range(0, num_actuators):
                position_history[i].append(float(state[i].position))
                velocity_history[i].append(float(state[i].velocity))
                torque_history[i].append(float(torque[i]))
            for i in range(0, len(controller_output)):
                controller_output_history[i].append(float(controller_output[i]))
            time_history.append(control_loop_time)

            control_loop.step(controller_output)

        results[-1]['result'] = "SUCCESS"
    except Exception as e:
        results[-1]['result'] = "FAILED"
        results[-1]['exception'] = str(e)
    finally:
        results[-1]['score'] = evaluator.get_score()

    try:
        video_url, logs = control_loop.stop()
        results[-1]['logs'] = logs
    except Exception as e:
        print(str(e))
    print(results[-1])

    iteration_data.append({
        "position": position_history,
        "velocity": velocity_history,
        "torque": torque_history,
        "controller_output": controller_output_history,
        "time": time_history,
    })

total_score = sum([it['score'] for it in results]) / float(len(results))
print("Total score:", total_score)

with open(out_dir + "/result.json", "w") as f:
    f.write(json.dumps({
        "iterations": results,
        "score": total_score,
    }))

with open(out_dir + "/data.json", "w") as f:
    f.write(json.dumps({"iterations": iteration_data}))
