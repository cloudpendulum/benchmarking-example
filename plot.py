import sys
import json
import math
import matplotlib.pyplot as plt

data_dir = "output/" + sys.argv[1]
data_file = data_dir + "/data.json"
result_file = data_dir + "/result.json"
data = []
result = {}

with open(data_file, "r") as f:
    data = json.load(f)

with open(result_file, "r") as f:
    result = json.load(f)

disturbances = []
for it_result in result['iterations']:
    logs = it_result['logs']

    start_prefix = "LOG: Started disturbance "
    end_prefix = "LOG: Ended disturbance "

    disturbances.append([])
    for i in range(1, len(logs), 2):
        try:
            start_strs = logs[i - 1].split(start_prefix)[1].split(" after ")
            end_strs = logs[i].split(end_prefix)[1].split(" after ")
            disturbances[-1].append({
                "type": start_strs[0],
                "start_time": float(start_strs[1].split(" seconds")[0]),
                "end_time": float(end_strs[1].split(" seconds")[0]),
            })
        except Exception as e:
            print(e)

def plot_disturbances(iteration: int):
    disturbance_areas = {}
    for dist in disturbances[iteration]:
        d_areas = disturbance_areas.setdefault(dist['type'], [])
        d_areas += [dist['start_time'], dist['end_time'], dist['end_time']]

    for d_type, d_area in disturbance_areas.items():
        plt.fill_between(
            d_area, -10000.0, 100000.0,
            where = [(i % 3) != 2 for i in range(len(d_area))],
            alpha=0.2,
            label=d_type
        )

def iteration_plot(iteration: int):
    iteration_data = data['iterations'][iteration]
    position_history = iteration_data['position']
    velocity_history = iteration_data['velocity']
    torque_history = iteration_data['torque']
    controller_output_history = iteration_data['controller_output']
    time_history = iteration_data['time']

    n_joints = len(position_history)
    n_timesteps = len(time_history)
    T = time_history[-1]
    n_plots = 4

    joint_height_history = []
    joint_angle = [0.0] * n_timesteps
    for j in range(n_joints):
        height_history = [0.0] * n_timesteps
        for i in range(n_timesteps):
            joint_angle[i] += position_history[j][i]
            height_history[i] = -math.cos(joint_angle[i])
        joint_height_history.append(height_history)

    max_vpos = float(n_joints) * 1.1
    goal_height = float(n_joints) * 0.9
    plt.subplot(n_plots, 1, 1)
    plt.axis([0.0, T, -max_vpos, max_vpos])
    plt.ylabel("Vertical position")
    plt.xlabel("Time")
    plt.hlines(
        y=[goal_height], xmin=0, xmax=T,
        colors='r', linestyles='dashed', label="Goal threshold"
    )
    for j, height_history in enumerate(joint_height_history):
        plt.plot(time_history, height_history, label="Joint " + str(j))
    plot_disturbances(iteration)
    plt.legend(loc="upper right")

    max_vel = max([abs(v) for vs in velocity_history for v in vs]) * 1.1
    plt.subplot(n_plots, 1, 2)
    plt.axis([0.0, T, -max_vel, max_vel])
    plt.ylabel("Joint velocity")
    plt.xlabel("Time")
    for j, vel_history in enumerate(velocity_history):
        plt.plot(time_history, vel_history, label="Joint " + str(j))
    plot_disturbances(iteration)
    plt.legend(loc="upper right")

    max_torque = max([abs(v) for vs in torque_history for v in vs]) * 1.1
    plt.subplot(n_plots, 1, 3)
    plt.axis([0.0, T, -max_torque, max_torque])
    plt.ylabel("Joint torque")
    plt.xlabel("Time")
    for j, u_hist in enumerate(torque_history):
        plt.plot(time_history, u_hist, label="Joint " + str(j))
    plot_disturbances(iteration)
    plt.legend(loc="upper right")

    max_u = max([abs(v) for vs in controller_output_history for v in vs]) * 1.1
    plt.subplot(n_plots, 1, 4)
    plt.axis([0.0, T, -max_u, max_u])
    plt.ylabel("Controller output torque")
    plt.xlabel("Time")
    for j, u_out_hist in enumerate(controller_output_history):
        plt.plot(time_history, u_out_hist, label="Joint " + str(j))
    plot_disturbances(iteration)
    plt.legend(loc="upper right")

num_iterations = len(data['iterations'])
for i in range(num_iterations):
    iteration_result = result['iterations'][i]
    fig = plt.figure(i)
    fig.set_size_inches(32, 16)
    fig.suptitle(
        "Iteration: {} - Cell: {} - Result: {:.2f}".format(
            i, iteration_result['cell_id'], iteration_result['score']
        ),
        fontsize=16
    )
    iteration_plot(i)

from matplotlib.backends.backend_pdf import PdfPages
figs = list(range(num_iterations))
with PdfPages(data_dir + '/plots.pdf') as pdf:
    for fig in figs:
        pdf.savefig(fig, bbox_inches='tight') 

