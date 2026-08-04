# Benchmarking Example

An example showing how to use the Cloud Pendulum benchmarking interface.

## Requirements

```
cloudpendulumclient pyzmq requests matplotlib ffmpeg-python
```

## Usage

Update the experiment parameters in `benchmark.py`, specifically the
`user_token` needs to be set to your Cloud Pendulum user token.

Run `python benchmark.py` to run the benchmark. It will run one benchmarking
iteration on each cell specified in the `cell_ids` list. The results from the
benchmark will be saved in `output/benchmark_<TIMESTAMP>/`.

To plot the benchmark results, run `python plot.py benchmark_<TIMESTAMP>`. The
plots will be saved as a .pdf file in the specified benchmark output directory.
