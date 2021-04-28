# slc_analysis

Script to automatize coarsening experiments with cCuda.

## Usage

```bash
python coarsening_full_range_experiment.py [device-id] [kernel-1] [kernel-2] [coarsening-1] [coarsening-2]
```

`coarsening-1` and `coarsening-2` can be single numbers or comma-separated lists of numbers (i.e. `1,2,4,8`)
