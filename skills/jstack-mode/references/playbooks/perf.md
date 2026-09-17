# Performance

Choose the metric, representative workload, environment and acceptable regression
guard. Measure a baseline before optimizing. Repeat noisy measurements and keep
sample count plus spread; use the same data and warmup policy for comparison.

Find the dominant cost with a profile or targeted timing. Change one supported
hypothesis, then rerun correctness checks and the same benchmark. Report raw
before/after values and conditions, not an invented percentage. If the effect is
within noise, say the improvement is unproven. A cheaper workload is not a faster
implementation of the original workload.
