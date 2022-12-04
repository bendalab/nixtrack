# nixtrack
Format definition for representing video tracking data in nix with the respective python package

## basic usage

```
import nixtrack as nt

if __name__ == "__main__":
    filename = "nofins.v002.010_2020.12.04_lepto03-converted_cropped.analysis.nix"
    d = nt.Dataset(filename)
    print(d.nodes)

```