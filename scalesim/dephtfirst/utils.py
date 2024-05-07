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

class Queue:
    """
    Represents a queue data structure.
    This is used to store the tiles in the depth-first simulation.
    """
    def __init__(self):
        self.items = []
    
    def is_empty(self):
        return self.size() == 0
    
    def peek(self):
        if self.is_empty():
            return None
        return self.items[0]
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items.pop(0)

    def size(self):
        return len(self.items)

class Layer:
    def __init__(self,layer_id, input, output, filter, stride):
        self.input = input
        self.output = output
        self.filter = filter
        self.stride = stride
        self.layer_id = layer_id
    
    @staticmethod
    def from_array(array):
        input = (array[1], array[2], array[5])
        filter = (array[3], array[4], array[6])
        stride = (array[7], array[8])
        return Layer(array[0], input, None, filter, stride)
    
    def __str__(self):
        """Used for debug purposes."""
        return f"Layer ID: {self.layer_id}, \
            Input: {self.input}, \
            Output: {self.output}, \
            Filter: {self.filter}, \
            Stride: {self.stride}"

class Tile:
    """
    Represents a tile in the depth-first scheduling simulation.
    """

    @staticmethod
    def from_layer(layer):
        """
        Create a tile from a layer.
        """
        return Tile(layer.input, layer.filter, layer.output, layer.layer_id)
    
    def __init__(self, Ifsize, filter_size, OfSize, layer_id,):
        self.Ifsize = Ifsize
        self.filter_size = filter_size
        self.OfSize = OfSize
        self.layer_id = layer_id

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
            Layer ID: {self.layer_id}"
