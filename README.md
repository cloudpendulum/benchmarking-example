# Benchmarking Example

An example showing how to use the Cloud Pendulum benchmarking interface.

## Requirements

```
pycloudpendulum pycloudpendulumbenchmark requests matplotlib ffmpeg-python
```

## Usage

Update the experiment parameters in `benchmark.py`, specifically the
`user_token` needs to be set to your Cloud Pendulum user token.

Run `python benchmark.py` to run the benchmark. It will run one benchmarking
iteration on each cell specified in the `cell_ids` list. The results from the
benchmark will be saved in `output/benchmark_<TIMESTAMP>/`.

To plot the benchmark results, run `python plot.py benchmark_<TIMESTAMP>`. The
plots will be saved as a .pdf file in the specified benchmark output directory.

## Writing a controller

To be used with the benchmarking interface, a controller class must inherit
from `ControllerBase` (from `pycloudpendulumbenchmark`) and implement both of
its abstract methods:

- `__init__(self)`: takes no arguments. A new instance is created for each
  cell, so set gains, limits and internal state here.
- `get_control_output(self, state: list[MotorState]) -> list[float]`: called
  once per control step. `state` has one `MotorState` (`.position`,
  `.velocity`) per actuator. Return one torque command per actuator.

```python
from pycloudpendulumbenchmark import ControllerBase, MotorState

class ZeroController(ControllerBase):
    def __init__(self):
        pass

    def get_control_output(self, state: list[MotorState]) -> list[float]:
        return [0.0, 0.0]
```

See `controller/pid_controller.py` for a full example. To benchmark your
controller, set `ControllerType` in `benchmark.py` (or the notebook) to your
class.

## Notebook

`benchmark.ipynb` runs the same benchmark step by step, with explanations, and
plots the results at the end (score per cell, the `plot.py` time series, and the
recorded videos). Set `user_token` in the configuration cell before running it.
