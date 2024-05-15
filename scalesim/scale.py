import argparse

from scalesim.scale_sim import scalesim
from scalesim.dephtfirst.utils import df_mode
from scalesim.dephtfirst.depth_first import depth_first_sim

def df_mode_parse(arg):
    if isinstance(arg, str):
        return df_mode[arg.upper()]
    elif isinstance(arg, int):
        return df_mode(arg)
    else:
        raise ValueError("Invalid argument type for df_mode")

if __name__ == '__main__':
    #TODO: add .. instead of . in paths
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', metavar='Topology file', type=str,
                        default="./topologies/conv_nets/test.csv",
                        help="Path to the topology file"
                        )
    parser.add_argument('-c', metavar='Config file', type=str,
                        default="./configs/scale.cfg",
                        help="Path to the config file"
                        )
    parser.add_argument('-p', metavar='log dir', type=str,
                        default="./test_runs",
                        help="Path to log dir"
                        )
    parser.add_argument('-i', metavar='input type', type=str,
                        default="conv",
                        help="Type of input topology, gemm: MNK, conv: conv"
                        )
    #Tuple(int,int)
    parser.add_argument('-tile_size', metavar='size', type=int, nargs=2,
                        default=[3,3],
                        help="Tile size for the input layer"
                        )
    parser.add_argument('-df_mode', metavar='depth first', type=df_mode_parse,
                        default=df_mode.FULL_RECOMPUTE,
                        help="Depth first scheduling mode"
                        )
    parser.add_argument('-stack_cut', metavar='layer_name', type=str, nargs='*',
                        default=[],
                        help="List of layers to cut the stack at"
                        )

    args = parser.parse_args()
    topology = args.t
    config = args.c
    logpath = args.p
    inp_type = args.i

    #depth-first args
    tile_size = args.tile_size
    df_mode_arg = args.df_mode
    stack_cut = args.stack_cut

    gemm_input = False
    if inp_type == 'gemm':
        gemm_input = True
    
    if df_mode_arg and tile_size:
        parsed_tile_size = tuple(tile_size)

        runner = depth_first_sim()
        runner.set_params(
            conf_file=config,
            topology_file=topology,
            df_mode=df_mode_arg,
            tile_size=parsed_tile_size,
            layer_fuse_cuts=stack_cut)
        
        runner.run()

        #TODO: add depth-first runner
    else:
        s = scalesim(save_disk_space=True, verbose=True,
                    config=config,
                    topology=topology,
                    input_type_gemm=gemm_input
                    )
        s.run_scale(top_path=logpath)
