import os
import nixtrack as nt
import matplotlib.pyplot as plt


def main():
    filename= "test/test.nix"
    d = nt.Dataset(filename)

    # get basic video related information
    print(f"File {os.path.split(d.name)[-1]}. Basic frame props.\n\timage size {d.frame_width}, {d.frame_height}\n\tframe count: {d.frame_count}\n\trecorded at {d.fps} fps")
    d.video_info.pprint()

    # get the number of instances and their positions
    print(f"Number of instances: {d.instance_count}")
    print(f"Nodes used for tracking: {d.nodes}")

    # get the positions for node "snout" and plot it with the color representing time
    pos, t, i_score, n_score = d.positions(node="snout", axis_type=nt.AxisType.Time)
    plt.scatter(pos[:, 0], pos[:, 1], c=t, s=n_score * 20 + 1)
    plt.gca().yaxis.set_inverted(True)
    plt.show()

if __name__ == "__main__":
    main()