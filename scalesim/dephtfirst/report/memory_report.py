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
        self.sum = 1 # used to store the sum of the values
    
    def __add__(self, other):
        """
        Addition operator for the memory report object.
        
        It adds the values of the two memory report objects.
        """
        result = memory_report(self.operand)
        result.start_cycle = self.start_cycle + other.start_cycle
        result.stop_cycle = self.stop_cycle + other.stop_cycle
        result.access = self.access + other.access

        result.sum = self.sum + other.sum
        result.avg_bw = (self.avg_bw*self.sum + other.avg_bw*other.sum)/result.sum
        return result
    
    def get_detailed_report(self):
        return f"{self.start_cycle}, \
            {self.stop_cycle}, \
            {self.access}"
    
    def generate_report(self,memory_system):

        self.start_cycle = memory_system.start_cycle
        self.stop_cycle = memory_system.stop_cycle
        self.access = memory_system.access
        self.avg_bw = memory_system.avg_bw
    
    def __str__(self):
        # Format: start_cycle, stop_cycle, access, avg_bw
        return f"{self.start_cycle}, \
            {self.stop_cycle}, \
            {self.access}, \
            {self.avg_bw}"

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