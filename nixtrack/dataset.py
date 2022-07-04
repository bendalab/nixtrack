import os
import nixio as nix
import numpy as np

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

    def positions(self, track=None, node=None, axis_start=0, axis_end=None, axis_type=AxisType.Index):
        """reads the positions data from file. Additional arguments can be used to filter the data.

        Parameters
        ----------
        track : str or int, optional
            the track name or id, by default None
        node : str or int, optional
            the node name or id, by default None
        axis_start : int or float, optional
            the start frame or time. Interpretation is controlled via the axis_type argument. , by default 0
        axis_end : int or float, optional
            the end frame or time. Interpretation is controlled via the axis_type argument. by default None
        axis_type : AxisType, optional
            Controls whether the axis is in frame indices (AxisType.Index) or seconds (AxisType.Time), by default AxisType.Index

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        ValueError
            if an invalid node or track is given
        """
        if axis_type == AxisType.Time:
            dt = 1. if axis_type == AxisType.Index else 1./self.fps

        track_id = None
        if track is not None:
            tnames, tids = self.tracks
            if isinstance(track, str):
                if track in tnames:
                    track_id = tids[tnames.index(track)]
                else:
                    raise ValueError(f"Given track {track} is invalid! Options are {tnames} or {tids}.")
            else:
                track_id = int(track)
            if track_id not in tids:
                raise ValueError(f"Given track {track} is invalid! Options are {tnames} or {tids}.")

        node_id = None
        if node is not None:
            nnames = self.nodes
            nids = list(range(len(nnames)))
            if isinstance(node, str):
                if node in nnames:
                    node_id = nids[nnames.index(node)]
                else:
                    raise ValueError(f"Given node {node} is invalid! Options are {nnames}.")
            else:
                node_id = int(node)

        track_data = self._block.data_arrays["track"][:]

        pos_array = self._block.data_arrays["position"]
        axis = np.array(pos_array.dimensions[0].ticks)
        time_axis = axis / self.fps

        if node_id is None:
            pos_data = pos_array[:]
        else:
            pos_data = np.squeeze(pos_array[:, :, node_id])

        start_index = 0
        if axis_start is not None:
            if axis_type == AxisType.Index:
                start_index = np.where(axis >= axis_start)[0][0]
            else:
                start_index = np.where(time_axis >= axis_start)[0][0]
        end_index = len(axis)
        if axis_end is not None:
            if axis_type == AxisType.Index:
                end_index = np.where(axis < axis_end)[0][-1]
            else:
                end_index = np.where(time_axis < axis_end)[0][-1]
        pos_data = pos_data[start_index:end_index+1]

        axis = axis[start_index:end_index+1]
        time_axis = time_axis[start_index:end_index+1]
        track_data = track_data[start_index:end_index+1]
        if track_id is not None:
            pos_data = pos_data[track_data == track_id]
            axis = axis[track_data == track_id]
            time_axis = time_axis[track_data == track_id]

        return pos_data, axis if axis_type == AxisType.Index else time_axis

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
    def instance_count(self):
        return self._block.data_arrays["position"].shape[0]

    @property
    def video_info(self):
        return self._block.sources[0].metadata

    @property
    def fps(self):
        return self._block.sources[0].metadata["fps"]

    @property
    def video_name(self):
        return self._block.sources[0].metadata["filename"]

    @property
    def _position_array(self):
        return self._block.data_arrays["position"]

    def __str__(self) -> str:
        info = "{n:s}\n\tlocation: {l:s}\n\tfile size {s:.2f} MB"
        return info.format(**{"n": self.name.split(os.sep)[-1],
                              "l": os.sep.join(self.name.split(os.sep)[:-1]),
                              "s": os.path.getsize(self._filename)/1e+6})

    def __repr__(self) -> str:
        repr = "Dataset object for file {name:s} at {id}"
        return repr.format(name=self.name, id=hex(id(self)))

