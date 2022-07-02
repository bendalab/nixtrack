from enum import Enum

class AxisType(Enum):
    """Enumeration to control the time axis returned by the positions function.
    Options are:
        * Time: the axis is given in seconds
        * Index: the axis contains the frame indices
    """
    Time = 0
    Index = 1