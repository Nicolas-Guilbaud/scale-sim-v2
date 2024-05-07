from enum import Enum
from .memory_report import sram_report, dram_report, operand

class report:
    """
    Object used to store the values to report for the depth-first simulation.
    """
    def __init__(self) -> None:
        self.compute_report = compute_report()

        self.ifmap_sram_report = sram_report(operand.IFMAP)
        self.filter_sram_report = sram_report(operand.FILTER)
        self.ofmap_sram_report = sram_report(operand.OFMAP)

        self.ifmap_dram_report = dram_report(operand.IFMAP)
        self.filter_dram_report = dram_report(operand.FILTER)
        self.ofmap_dram_report = dram_report(operand.OFMAP)
    
    def generate_report(self,compute_system,memory_system):
        self.compute_report.generate_report(compute_system,memory_system)

        self.ifmap_sram_report.generate_report(memory_system,compute_system)
        self.filter_sram_report.generate_report(memory_system,compute_system)
        self.ofmap_sram_report.generate_report(memory_system,compute_system)

        self.ifmap_dram_report.generate_report(memory_system)
        self.filter_dram_report.generate_report(memory_system)
        self.ofmap_dram_report.generate_report(memory_system)
    
    def __add__(self, other):
        """
        Addition operator for the report object.
        
        It adds the values of the two report objects.
        """
        result = report()
        result.compute_report = self.compute_report + other.compute_report

        result.ifmap_sram_report = self.ifmap_sram_report + other.ifmap_sram_report
        result.filter_sram_report = self.filter_sram_report + other.filter_sram_report
        result.ofmap_sram_report = self.ofmap_sram_report + other.ofmap_sram_report

        result.ifmap_dram_report = self.ifmap_dram_report + other.ifmap_dram_report
        result.filter_dram_report = self.filter_dram_report + other.filter_dram_report
        result.ofmap_dram_report = self.ofmap_dram_report + other.ofmap_dram_report
        return result
    
    def __str__(self):
        return f"Compute Report: \n{self.compute_report}\n\n\
            IFMAP SRAM Report: \n{self.ifmap_sram_report}\n\n\
            FILTER SRAM Report: \n{self.filter_sram_report}\n\n\
            OFMAP SRAM Report: \n{self.ofmap_sram_report}\n\n\
            IFMAP DRAM Report: \n{self.ifmap_dram_report}\n\n\
            FILTER DRAM Report: \n{self.filter_dram_report}\n\n\
            OFMAP DRAM Report: \n{self.ofmap_dram_report}\n\n"

class compute_report:
    """
    Object used to store the values to report for the compute system.
    """
    def __init__(self) -> None:
        self.total_cycles = 0
        self.stall_cycles = 0
        self.num_compute = 0
        self.num_mac_unit = 0
        self.overall_util = 0
        self.mapping_eff = 0
        self.compute_util = 0
    
    def generate_report(self,compute_system, memory_system):
        self.total_cycles = memory_system.get_total_compute_cycles()
        self.stall_cycles = memory_system.get_stall_cycles()
        self.overall_util = (self.num_compute * 100) / (self.total_cycles * self.num_mac_unit)
        self.mapping_eff = compute_system.get_avg_mapping_efficiency() * 100
        self.compute_util = compute_system.get_avg_compute_utilization() * 100
    
    def __add__(self, other):
        """
        Addition operator for the compute_report object.
        
        It adds the values of the two compute_report objects.
        """
        result = compute_report()
        result.total_cycles = self.total_cycles + other.total_cycles
        result.stall_cycles = self.stall_cycles + other.stall_cycles
        result.num_compute = self.num_compute + other.num_compute
        result.num_mac_unit = self.num_mac_unit + other.num_mac_unit
        result.overall_util = self.overall_util + other.overall_util
        result.mapping_eff = self.mapping_eff + other.mapping_eff
        result.compute_util = self.compute_util + other.compute_util
        return result
    
    def __str__(self):
        return f"Total Cycles: {self.total_cycles}\n\
            Stall Cycles: {self.stall_cycles}\n\
            Overall Utilization: {self.overall_util}%\n\
            Mapping Efficiency: {self.mapping_eff}%\n\
            Compute Utilization: {self.compute_util}%\n"