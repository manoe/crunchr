# R2MRP Analytic Model

`main.py` is a numerical implementation of the analytic, mean-field model of the
**R2MRP** (Resilient Reliable Multi-Path Routing Protocol) described in
[`tex/main.tex`](tex/main.tex). It places sensor nodes on a rectangular grid,
models the per-link packet-success / QoS-filter probabilities, and computes
either the expected number of disjoint paths `E[P]` (Chapter 2) or the
round-indexed path-membership matrix `alpha` (Chapter 3).

## Requirements

- Python 3.10+ (the code uses `match`/`case`)
- [NumPy](https://numpy.org/)

```bash
pip install numpy
```

## Usage

```bash
python3 main.py [options]
```

Examples:

```bash
# Expected number of paths on a 10x10 grid
python3 main.py -d e_p -n 100 -x 10 -y 10

# Path-membership matrix on a small grid, divergence radio model, 5 rounds
python3 main.py -d alpha -n 4 -x 2 -y 2 -rd 15 -r div -i 5
```

## Command-line arguments

| Short | Long | Type / choices | Default | Description |
|-------|------|----------------|---------|-------------|
| `-d`  | `--data` | `e_p` \| `alpha` | `alpha` | Which quantity to compute. `e_p` = expected number of paths `E[P]`; `alpha` = round-indexed path-membership matrix. |
| `-n`  | `--node-num` | int | `100` | Number of nodes `N` (including the sink, which is node 0). |
| `-x`  | `--x-num` | int | `10` | Number of grid points along the X axis. |
| `-y`  | `--y-num` | int | `10` | Number of grid points along the Y axis. |
| `-gd` | `--grid-distance` | float | `20` | Spacing between adjacent grid points, in meters. |
| `-q`  | `--qos` | float | `0.8` | QoS threshold `tau` for the packet-delivery ratio. A link passes the filter if at least `ceil(qos * num-test)` of the test messages succeed. |
| `-nt` | `--num-test` | int | `10` | Number `n` of RREQ/RRESP link-test messages used for the binomial QoS estimate. |
| `-rd` | `--ref_dist` | float | `1` | Reference distance `d0` used by the radio model. |
| `-a`  | `--alpha` | float | `2.5` | Attenuation coefficient `a`, used by the logistic (`log`) radio model. |
| `-r`  | `--radio` | `log` \| `div` | `log` | Link-reliability model (see below). |
| `-i`  | `--iter` | int | `100` | Number of construction rounds to iterate (only used for `-d alpha`). The loop runs rounds `2 .. iter-1`. |
| `-e`  | `--epsilon` | float | `1e-05` | Small regularization constant added to the denominator when normalizing the advertising probabilities `beta`, for numerical stability. |
| `-l`  | `--log-level` | `debug` \| `info` \| `none` | `none` | Verbosity of logging to stdout. `none` only logs errors. |

### Constraints

- `x * y` must be `>= n`; otherwise the grid cannot hold all nodes and the
  script exits with an error.
- Nodes are laid out in row-major order: node index `i * y + j` is placed at
  coordinates `(i * grid-distance, j * grid-distance)` for `i in [0, x)` and
  `j in [0, y)`. Node `0` (at the origin) is the sink.

## Radio models (`-r`)

The per-link success probability `p(d)` as a function of distance `d`:

- `log` — logistic model: `p(d) = 1 / (1 + exp(a * (d - d0)))`, using `-a` and `-rd`.
- `div` — log-distance model: `p(d) = 1 + log10(d0 / d)`, clamped to `0` when below `-1`, using `-rd`.

The QoS-filter / border probability is then
`q(d) = p(d) * P(X >= ceil(qos * num-test))`, with `X ~ Binomial(num-test, p(d))`.

## Output

- `-d e_p`: prints `E[P]`, the expected number of disjoint paths.
- `-d alpha`: prints the final `alpha` matrix as a labeled table, where rows are
  nodes (`Node i`) and columns are paths (`Path p`); entry `(i, p)` is the
  probability that node `i` belongs to the path originated by border node `p`.

## Known limitations

- `-d e_p` currently raises `KeyError` because it iterates `nodes[1:]` while
  `nodes` is a `dict`. The `-d alpha` path is the supported entry point.
- The mean-field recursion uses the instantaneous Learn probability rather than
  the finite Learn window (`W_L`) described in Chapter 3.2 of the document.
- The recursion sums over all nodes rather than restricting to a neighborhood
  radius (there is no neighbor-radius cutoff in the current implementation).
