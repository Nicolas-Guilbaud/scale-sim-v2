from enum import Enum
import numpy as np


class df_mode(Enum):
    """
    Represents the different modes 
    for depth-first scheduling simulation.
    """
    FULL_RECOMPUTE = 1
    H_CACHED_V_RECOMPUTE = 2
    FULL_CACHED = 3

class Tile:
    """
    Represents a tile in the depth-first scheduling simulation.
    """
    
    def __init__(self, Ifsize, filter_size, OfSize, layer_id,cached_elements=0):
        self.Ifsize = Ifsize
        self.filter_size = filter_size
        self.OfSize = OfSize
        self.layer_id = layer_id
        self.cached_elements = cached_elements # Number of elements in the tile that are already cached

    def to_operands(self) -> tuple:
        """
        Convert the tile to a tuple containing the 3 matrices operands.
        """
        
        input = np.ones(self.Ifsize, dtype=int)
        filter = np.ones(self.filter_size, dtype=int)
        output = np.ones(self.OfSize, dtype=int)
        return input, filter, output

    def __str__(self):
        """Used for debug purposes."""
        return f"Ifsize: {self.Ifsize}, \
            Filter size: {self.filter_size}, \
            OfSize: {self.OfSize}, \
            Layer ID: {self.layer_id}, \
            Cached Elements: {self.cached_elements}"
