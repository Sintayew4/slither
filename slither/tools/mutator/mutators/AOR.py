from typing import Dict
from slither.slithir.operations import Binary, BinaryType
from slither.formatters.utils.patches import create_patch
from slither.tools.mutator.mutators.abstract_mutator import AbstractMutator, FaultNature, FaultClass

arithmetic_operators = [
    BinaryType.ADDITION,
    BinaryType.DIVISION,
    BinaryType.MULTIPLICATION,
    BinaryType.SUBTRACTION,
    BinaryType.MODULO
]

class AOR(AbstractMutator):  # pylint: disable=too-few-public-methods
    NAME = "AOR"
    HELP = "Arithmetic operator replacement"
    FAULTCLASS = FaultClass.Checking
    FAULTNATURE = FaultNature.Missing

    def _mutate(self) -> Dict:
        result: Dict = {}

        for function in self.contract.functions_and_modifiers_declared:
            for node in function.nodes:
                for ir in node.irs:
                    if isinstance(ir, Binary) and ir.type in arithmetic_operators:
                        alternative_ops = arithmetic_operators[:]
                        alternative_ops.remove(ir.type)
                        for op in alternative_ops:
                            # Get the string
                            start = node.source_mapping.start
                            stop = start + node.source_mapping.length
                            old_str = self.in_file_str[start:stop]
                            line_no = node.source_mapping.lines
                            # Replace the expression with true
                            new_str = f"{old_str.split(ir.type.value)[0]}{op.value}{old_str.split(ir.type.value)[1]}"
                            create_patch(result, self.in_file, start, stop, old_str, new_str, line_no[0])
        return result