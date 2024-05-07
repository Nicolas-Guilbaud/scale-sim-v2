from scalesim.scale_config import scale_config as cfg
from scalesim.topology_utils import topologies as topo
from scalesim.compute.systolic_compute_os import systolic_compute_os
from scalesim.compute.systolic_compute_ws import systolic_compute_ws
from scalesim.compute.systolic_compute_is import systolic_compute_is
from scalesim.memory.double_buffered_scratchpad_mem import double_buffered_scratchpad as mem_dbsp
from report.report import report
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
        self.report = report()
        self.compute_system = systolic_compute_os()
        self.memory_system = mem_dbsp()
        self.total_report = report()

    def set_memory_system(self, mem_sys_obj=mem_dbsp()):
        self.memory_system = mem_sys_obj
        self.memory_system_ready_flag = True

    def set_params(self,
                    conf_file="",
                    topology_file="",
                    read_gemm_inputs=False,
                    df_mode=df_mode.FULL_RECOMPUTE,
                    tile_size=(1,1),
                    layer_fuse_cuts=[], #Format: [layer_1, layer_4]
                   ):
        """
        Set the parameters for the depth-first simulation.
        Args:
        - conf_file: path to the configuration file
        - topology_file: path to the topology file
        - read_gemm_inputs: whether to read GEMM inputs
        - df_mode: depth-first scheduling mode
        - tile_size: size of the tile
        - layer_fuse_cuts: list of layer ids to cut to form stacks.  
            Example with 5 layers: [1, 4]
            -> will split the topology into 3 stacks: [ [1], [2,3,4], [5] ]
        """
        # Setup depth-first simulation parameters
        self.df_mode = df_mode
        self.tile_size = tile_size
        self.layer_fuse_cuts = layer_fuse_cuts

        # Load the configuration and topology files
        self.config.read_conf_file(conf_file)
        self.config.set_topology_file(topology_file)
        self.topo.load_arrays(topofile=topology_file, mnk_inputs=read_gemm_inputs)

        # Setup the compute system
        self.dataflow = self.config.get_dataflow()

        if self.dataflow == 'os':
            self.compute_system = systolic_compute_os()
        elif self.dataflow == 'ws':
            self.compute_system = systolic_compute_ws()
        elif self.dataflow == 'is':
            self.compute_system = systolic_compute_is()

    
    def run(self):
        """
        Run the depth-first simulation.
        """
        scheduled_tiles = [] # tiles to compute
        
        # 1. Separate layers into stacks based on layer_fuse_cuts
        self.stack_list = self.create_stack_list()
        
        # 2. Divide each stack into tiles
        for stack in self.stack_list:
            tiles = self.stack_tiling(stack)
            scheduled_tiles.extend(tiles)
        
        #TODO: perform the following for each scheduled tiles !

        print("FOR 1 TILE:")


        # 3. Prepare demand for 1 tile
        # This part is a copy-paste from the run function inside single_layer_sim.py file

        #3.1 Setup compute system
        input_mat, filter_mat, output_mat = scheduled_tiles[0].to_operands()
        self.compute_system.set_params(config_obj=self.config,
                                       ifmap_op_mat=input_mat,
                                       filter_op_mat=filter_mat,
                                       ofmap_op_mat=output_mat)
        print("DEMANDS:")
        print(len(input_mat))
        print(len(filter_mat))
        print(len(output_mat))


        print("GETTING DEMAND")

        # 3.2 Get the demand for the first tile
        ifmap_prefetch_mat, filter_prefetch_mat = self.compute_system.get_prefetch_matrices()

        print("DEMANDS:")
        print(len(ifmap_prefetch_mat))
        print(len(filter_prefetch_mat))

        return
        ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat = self.compute_system.get_demand_matrices()

        print("SETTING UP MEMORY")
        # 3.3 Setup memory system
        self.setup_memory_if_not_ready()

        if self.config.use_user_dram_bandwidth() :
            self.memory_system.set_read_buf_prefetch_matrices(ifmap_prefetch_mat=ifmap_prefetch_mat,
                                                              filter_prefetch_mat=filter_prefetch_mat)

        # 4. Compute
        self.memory_system.service_memory_requests(ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat)
        self.runs_ready = True

        # 5. Generate report
        tile_report = report()
        tile_report.generate_report(self.compute_system,self.memory_system)

        # 5. Add results and repeat for next tile
        total_report = total_report + tile_report
        print(total_report)
        pass

    def setup_memory_if_not_ready(self):
        """
        Setup memory system if not ready.
        """
        # It is a copy-paste found in the run function inside single_layer_sim.py file
        if not self.memory_system_ready_flag:
            word_size = 1           # bytes, this can be incorporated in the config file
            active_buf_frac = 0.5   # This can be incorporated in the config as well

            ifmap_buf_size_kb, filter_buf_size_kb, ofmap_buf_size_kb = self.config.get_mem_sizes()
            ifmap_buf_size_bytes = 1024 * ifmap_buf_size_kb
            filter_buf_size_bytes = 1024 * filter_buf_size_kb
            ofmap_buf_size_bytes = 1024 * ofmap_buf_size_kb

            ifmap_backing_bw = 1
            filter_backing_bw = 1
            ofmap_backing_bw = 1
            estimate_bandwidth_mode = False
            if self.config.use_user_dram_bandwidth():
                bws = self.config.get_bandwidths_as_list()
                ifmap_backing_bw = bws[0]
                filter_backing_bw = bws[0]
                ofmap_backing_bw = bws[0]

            else:
                dataflow = self.config.get_dataflow()
                arr_row, arr_col = self.config.get_array_dims()
                estimate_bandwidth_mode = True

                # The number 10 elems per cycle is arbitrary
                ifmap_backing_bw = 10
                filter_backing_bw = 10
                ofmap_backing_bw = arr_col
            
            self.memory_system.set_params(
                    word_size=word_size,
                    ifmap_buf_size_bytes=ifmap_buf_size_bytes,
                    filter_buf_size_bytes=filter_buf_size_bytes,
                    ofmap_buf_size_bytes=ofmap_buf_size_bytes,
                    rd_buf_active_frac=active_buf_frac, wr_buf_active_frac=active_buf_frac,
                    ifmap_backing_buf_bw=ifmap_backing_bw,
                    filter_backing_buf_bw=filter_backing_bw,
                    ofmap_backing_buf_bw=ofmap_backing_bw,
                    verbose=self.verbose,
                    estimate_bandwidth_mode=estimate_bandwidth_mode
            )

    def request_tiles_computation(self):
        """
        Request a computation of tiles.
        """
        pass

    def create_stack_list(self):
        """
        Create a list of stacks of layers based on the layer_fuse_cuts.

        Example:
        (with 5 layers)
        layer_fuse_cuts = [1, 4]
        -> it will split the topology into 3 stacks: 
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
    import sys
    import os
    
    sys.path.append(os.getcwd())
    runner = depth_first_sim()
    runner.set_params(
        conf_file="./configs/scale.cfg",
        # topology_file="./topologies/conv_nets/test.csv",
        topology_file="./topologies/conv_nets/alexnet.csv",
        df_mode=df_mode.FULL_RECOMPUTE,
        tile_size=(1,1),
        layer_fuse_cuts=["Conv"+str(i) for i in range(1,6,2)])
    
    runner.run()


    # stack_cuts = runner.create_stack_list()
    # for s in stack_cuts:
    #     tiles = runner.stack_tiling(s)
    #     print(len(tiles))
    #     for t in tiles[0:5]:
    #         print(t)
    #     print()
    