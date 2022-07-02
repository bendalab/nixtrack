import os
import nixio as nix

from .util import AxisType


class Dataset(object):

    def __init__(self, filename:str) -> None:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename}")
        self._filename = filename
        self._nixfile = None
        self._block = None
        self._mapping_version = None

        self.open_file()


    def open_file(self):
        nf = nix.File.open(self._filename, nix.FileMode.ReadOnly)
        valid = True
        sections = nf.find_sections(lambda s: s.type == "nix.tracking.metadata")
        valid = valid & len(sections) > 0
        if valid:
            s = sections[0]
            valid = valid & ("format" in s.props and s["format"] == "nix.tracking")
            if valid:
                self._mapping_version = s["version"]
        if not valid:
            ValueError(f"File {self._filename} is and invalid nix file that does not contain tracking data.")
        self._nixfile = nf
        self._block = nf.blocks[0]

    @property
    def is_open(self) -> bool:
        """Returns whether the nix file is still open.

        Returns
        -------
        bool
            True if the file is open, False otherwise.
        """
        return self._nixfile is not None and self._nixfile.is_open()

    def close(self):
        """Close the nix file, if open. Note: Once the file is closed accessing the data via one of the repro run classes will not work!
        """
        if self._nixfile is not None and self._nixfile.is_open():
            self._nixfile.flush()
            self._nixfile.close()
        self._nixfile = None
        self._metadata_buffer.clear(False)
        self._feature_buffer.clear(False)

    @property
    def is_open(self) -> bool:
        """Returns whether the nix file is still open.

        Returns
        -------
        bool
            True if the file is open, False otherwise.
        """
        return self._nixfile is not None and self._nixfile.is_open()

    @property
    def name(self) -> str:
        """Returns the name of the dataset (i.e. the full filename)
        
        Returns
        -------
        str
            The full filename
        """
        return self._filename

    @property
    def nix_file(self) -> nix.File:
        """Returns the nix-file.

        Returns
        -------
        nixio.File
            The nix file, if open, None otherwise.
        """
        return self._nixfile if self.is_open else None

    @property
    def positions(self, track=None, node=None, start_frame=0, end_frame=None, axis_type=AxisType.Index):
        if axis_type == AxisType.Time:
            dt = 1. if axis_type == AxisType.Index else 1./self.fps

        track_id = None
        if track is not None:
            tnames, tids = self.tracks
            if isinstance(track, str):
                if track in tnames:
                    track_id = tids[tnames == track]
                else:
                    raise ValueError(f"Given track {track} is inalid! Options are {tnames}.")
            track_id = int(track)

        node_id = None
        if node is not None:
            nnames = self.nodes
            n_ids = list(range(len(nnames)))
            if isinstance

        p = self._block.data_arrays["positions"]
        pass

    @property
    def nodes(self):
        positions = self._block.data_arrays["position"]
        return positions.dimensions[-1].labels

    def _read_map(self, df):
        names = [r[0] for r in df]
        ids = [r[1] for r in df]
        return names, ids

    @property
    def tracks(self):
        df = self._block.data_frames["track map"]
        return self._read_map(df)

    @property
    def skeletons(self):
        df = self._block.data_frames["skeleton map"]
        return self._read_map(df)

    @property
    def frame_width(self):
        return self._block.sources[0].metadata["width"]

    @property
    def frame_height(self):
        return self._block.sources[0].metadata["height"]

    @property
    def frame_count(self):
        return self._block.sources[0].metadata["frames"]

    @property
    def video_info(self):
        return self._block.sources[0].metadata

    @property
    def fps(self):
        return self._block.sources[0].metadata["fps"]

    @property
    def video_name(self):
        return self._block.sources[0].metadata["filename"]

    def __str__(self) -> str:
        info = "{n:s}\n\tlocation: {l:s}\n\tfile size {s:.2f} MB"
        return info.format(**{"n": self.name.split(os.sep)[-1],
                              "l": os.sep.join(self.name.split(os.sep)[:-1]),
                              "s": os.path.getsize(self._filename)/1e+6})

    def __repr__(self) -> str:
        repr = "Dataset object for file {name:s} at {id}"
        return repr.format(name=self.name, id=hex(id(self)))

