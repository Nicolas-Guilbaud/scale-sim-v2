from scalesim.scale_config import scale_config as cfg
from scalesim.topology_utils import topologies as topo
from utils import Tile, Queue, Layer, df_mode
from math import ceil

class depth_first_sim:
    """
    class to run depth-first scheduling simulation.
    See https://github.com/KULeuven-MICAS/defines
    """
    def __init__(self):
        self.topo = topo()
        self.config = cfg()


    def set_params(self,
                    conf_file="",
                    topology_file="",
                    read_gemm_inputs=False,
                    df_mode=df_mode.FULL_RECOMPUTE,
                    tile_size=(1,1),
                    layer_fuse_cuts=[], #Format: [layer_id_1, layer_id_5, layer_id_9]
                   ):
        """
        Set the parameters for the depth-first simulation.
        Args:
        conf_file: path to the configuration file
        topology_file: path to the topology file
        read_gemm_inputs: whether to read GEMM inputs
        df_mode: depth-first scheduling mode
        tile_size: size of the tile
        layer_fuse_cuts: list of layer ids to cut to form stacks
            example with 5 layers: [1, 4]
            will split the topology into stacks: [ [1], [2,3,4], [5] ]
        """
        self.df_mode = df_mode
        self.tile_size = tile_size
        self.layer_fuse_cuts = layer_fuse_cuts
        self.config.read_conf_file(conf_file)
        self.config.set_topology_file(topology_file)
        self.topo.load_arrays(topofile=topology_file, mnk_inputs=read_gemm_inputs)

    
    def run(self):
        """
        Run the depth-first simulation.
        """
        # 1. Separate layers into stacks based on layer_fuse_cuts
        self.stack_list = self.create_stack_list()
        # 2. Divide each stack into tiles
        # 3. Fill compute_system with tiles (data movement)
        # 4. Compute
        # 5. Add results
        pass

    def create_stack_list(self):
        """
        Create a list of stacks of layers based on the layer_fuse_cuts.

        Example:
        (with 5 layers)
        layer_fuse_cuts = [1, 4]
        will split the topology into 3 stacks: 
            - [1]
            - [2,3,4]
            - [5]

        Returns:
        a list of stacks
        """
        layers = self.topo.topo_arrays
        stack_list = []
        stack = []
        for l in layers:
            stack.append(l)
            if l[0] in self.layer_fuse_cuts:
                stack_list.append(stack)
                stack = []
        return stack_list
    
    def stack_tiling(self,stack):
        """
        returns a list of tiles given a stack.
        the tiles are expressed as follow:
        - layer Args, nber of tiles
        
        """

        #TODO: make it work with cached mode

        last_layer = stack[-1]

        #nber of tiles on the last layer to create
        nb_tiles_x = ceil(last_layer[1]/self.tile_size[0])
        nb_tiles_y = ceil(last_layer[2]/self.tile_size[1])

        tiles = [] # store the tiles
        for _ in range(nb_tiles_x*nb_tiles_y):

            output_size = self.tile_size

            # Backward loop to create the tiles
            for i,layer in enumerate(stack[::-1]):
                filter_size = (layer[3], layer[4])
                stride = (layer[7], layer[8])
                input_size = []
                for i in range(2):
                    input_size.append(filter_size[i] + (output_size[i]-1)*stride[i])
                input_size = tuple(input_size)
                
                tiles.append(Tile(input_size, filter_size, output_size, layer[0]))
                output_size = input_size # input of current layer = size of the tile of the next layer

        # Reverse the construction to process the tiles in the order according to layer
        return tiles[::-1]

        

        # Get the dimensions of the last layer




        # TODO: return a list of list of tiles

if __name__ == "__main__":
    runner = depth_first_sim()
    runner.set_params(
        conf_file="./configs/scale.cfg",
        # topology_file="./topologies/conv_nets/test.csv",
        topology_file="./topologies/conv_nets/alexnet.csv",
        df_mode=df_mode.FULL_RECOMPUTE,
        tile_size=(1,1),
        layer_fuse_cuts=["Conv"+str(i) for i in range(1,6,2)])
    

    stack_cuts = runner.create_stack_list()
    for s in stack_cuts:
        tiles = runner.stack_tiling(s)
        print(len(tiles))
        for t in tiles[0:5]:
            print(t)
        print()
    