from typing import Dict
from slither.core.cfg.node import NodeType
from slither.formatters.utils.patches import create_patch
from slither.tools.mutator.mutators.abstract_mutator import AbstractMutator, FaultNature, FaultClass
import re
from slither.core.variables.variable import Variable

solidity_rules = [
    "abi\.encode\( ==> abi.encodePacked(",
    "abi\.encodePacked\( ==> abi.encode(",
    "\.call([({]) ==> .delegatecall\\1",
    "\.call([({]) ==> .staticcall\\1",
    "\.delegatecall([({]) ==> .call\\1",
    "\.delegatecall([({]) ==> .staticcall\\1",
    "\.staticcall([({]) ==> .delegatecall\\1",
    "\.staticcall([({]) ==> .call\\1",
    "^now$ ==> 0",
    "block.timestamp ==> 0",
    "msg.value ==> 0",
    "msg.value ==> 1",
    "(\s)(wei|gwei) ==> \\1ether",
    "(\s)(ether|gwei) ==> \\1wei",
    "(\s)(wei|ether) ==> \\1gwei",
    "(\s)(minutes|days|hours|weeks) ==> \\1seconds",
    "(\s)(seconds|days|hours|weeks) ==> \\1minutes",
    "(\s)(seconds|minutes|hours|weeks) ==> \\1days",
    "(\s)(seconds|minutes|days|weeks) ==> \\1hours",
    "(\s)(seconds|minutes|days|hours) ==> \\1weeks",
    "(\s)(memory) ==> \\1storage",
    "(\s)(storage) ==> \\1memory",
    "(\s)(constant) ==> \\1immutable",
    "addmod ==> mulmod",
    "mulmod ==> addmod",
    "msg.sender ==> tx.origin",
    "tx.origin ==> msg.sender",
    "([^u])fixed ==> \\1ufixed",
    "ufixed ==> fixed",
    "(u?)int16 ==> \\1int8",
    "(u?)int32 ==> \\1int16",
    "(u?)int64 ==> \\1int32",
    "(u?)int128 ==> \\1int64",
    "(u?)int256 ==> \\1int128"
    "while ==> if",   
]


class SBR(AbstractMutator):  # pylint: disable=too-few-public-methods
    NAME = "SBR"
    HELP = 'Solidity Based Replacements'
    FAULTCLASS = FaultClass.Checking
    FAULTNATURE = FaultNature.Missing

    def _mutate(self) -> Dict:

        result: Dict = {}
        variable: Variable

        for function in self.contract.functions_and_modifiers_declared:
            for node in function.nodes:
                if node.type != NodeType.ENTRYPOINT:
                    # Get the string
                    start = node.source_mapping.start
                    stop = start + node.source_mapping.length
                    old_str = self.in_file_str[start:stop] 
                    line_no = node.source_mapping.lines
                    for value in solidity_rules:
                        left_value = value.split(" ==> ")[0]
                        right_value = value.split(" ==> ")[1]
                        if re.search(re.compile(left_value), old_str) != None:
                            new_str = re.sub(re.compile(left_value), right_value, old_str)
                            create_patch(result, self.in_file, start, stop, old_str, new_str, line_no[0])

        for variable in self.contract.state_variables_declared:
            node = variable.node_initialization
            if node:
                start = node.source_mapping.start
                stop = start + node.source_mapping.length
                old_str = self.in_file_str[start:stop] 
                line_no = node.source_mapping.lines
                for value in solidity_rules:
                    left_value = value.split(" ==> ")[0]
                    right_value = value.split(" ==> ")[1]
                    if re.search(re.compile(left_value), old_str) != None:
                        new_str = re.sub(re.compile(left_value), right_value, old_str)
                        create_patch(result, self.in_file, start, stop, old_str, new_str, line_no[0])
        return result

    

    
        
    