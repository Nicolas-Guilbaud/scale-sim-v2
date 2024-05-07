from enum import Enum

class operand(Enum):
    """Used to represent the different operands in the memory system."""
    IFMAP = 1
    FILTER = 2
    OFMAP = 3

class memory_report:
    """
    Object used to store the values to report for memory usage.
    """
    def __init__(self, operand: operand) -> None:
        self.start_cycle = 0
        self.stop_cycle = 0
        self.access = 0 # represents a read or write
        self.avg_bw = 0
        self.operand = operand
    
    def __add__(self, other):
        """
        Addition operator for the memory report object.
        
        It adds the values of the two memory report objects.
        """
        result = memory_report(self.operand)
        result.start_cycle = self.start_cycle + other.start_cycle
        result.stop_cycle = self.stop_cycle + other.stop_cycle
        result.access = self.access + other.access
        result.avg_bw = self.avg_bw + other.avg_bw
        return result
    
    def generate_report(self,memory_system):

        self.start_cycle = memory_system.start_cycle
        self.stop_cycle = memory_system.stop_cycle
        self.access = memory_system.access
        self.avg_bw = memory_system.avg_bw
    
    def __str__(self):
        return f"Start Cycle: {self.start_cycle}, \
            Stop Cycle: {self.stop_cycle}, \
            Access: {self.access}, \
            Average Bandwidth: {self.avg_bw}\n"

class sram_report(memory_report):
    """
    Object used to store the values to report for SRAM usage.
    """
    def __init__(self,operand) -> None:
        super().__init__(operand)
    
    def __add__(self, other):
        return super().__add__(other)
    
    def __str__(self):
        return super().__str__()
    
    def generate_report(self,memory_system,compute_system):

        total_cycles = memory_system.get_total_compute_cycles()

        match self.operand:
            case operand.IFMAP:
                self.access = compute_system.get_ifmap_requests()
            case operand.FILTER:
                self.access = compute_system.get_filter_requests()
            case operand.OFMAP:
                self.access = compute_system.get_ofmap_requests()
        
        self.avg_bw = self.access / total_cycles

class dram_report(memory_report):
    """
    Object used to store the values to report for DRAM usage.
    """
    def __init__(self,operand) -> None:
        super().__init__(operand)
    
    def __add__(self, other):
        return super().__add__(other)
    
    def __str__(self):
        return super().__str__()
    
    def generate_report(self,memory_system):

        match self.operand:
            case operand.IFMAP:
                self.start_cycle, self.stop_cycle, self.access \
                = memory_system.get_ifmap_dram_details()
            case operand.FILTER:
                self.start_cycle, self.stop_cycle, self.access \
                = memory_system.get_filter_dram_details()
            case operand.OFMAP:
                self.start_cycle, self.stop_cycle, self.access \
                = memory_system.get_ofmap_dram_details()
        
        self.avg_bw = self.access / (self.stop_cycle - self.start_cycle + 1)