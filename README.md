# nixtrack

Format specification and reader library for tracking data stored in NIX files.

Read the docs/format.md for more information.

## Installation

So far the package needs to be installed manually from source.

``` bash
git clone https://github.com/bendalab/nixtrack.git
cd nixtrack
pip3 install . --user
```

## Basic usage

See ``test/test.py`` for a little more extensive example.

``` python
import nixtrack as nt
import matplotlib.pyplot as plt

filename = "test/test.nix"
d = nt.Dataset(filename)
print(d)
print(d.nodes)

pos, time, _, _ = d.positions(node="snout")
plt.scatter(pos[:, 0], pos[:, 1])
plt.show()
```
