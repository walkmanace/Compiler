from src.ast.nodes import (
    AssignmentNode,
    BinaryOpNode,
    BoolNode,
    IdentifierNode,
    IfStmtNode,
    NumNode,
    PrintStmtNode,
    ProgramNode,
    UnaryOpNode,
    VarDeclNode,
    WhileStmtNode,
)


class CodeGenerator:
    def __init__(self) -> None:
        self.label_count = 0

    def generate(self, program: ProgramNode) -> list[str]:
        if not isinstance(program, ProgramNode):
            raise TypeError("代码生成输入必须是 ProgramNode 节点")

        instructions: list[str] = []
        for statement in program.statements:
            instructions.extend(self._generate_statement(statement))
        return instructions

    def _generate_statement(self, statement) -> list[str]:
        if isinstance(statement, VarDeclNode):
            instructions = []
            if statement.initializer is not None:
                instructions.extend(self._generate_expression(statement.initializer))
            else:
                instructions.append("PUSH 0")
            instructions.append(f"STORE {statement.identifier.name}")
            return instructions

        if isinstance(statement, AssignmentNode):
            instructions = self._generate_expression(statement.value)
            instructions.append(f"STORE {statement.identifier.name}")
            return instructions

        if isinstance(statement, PrintStmtNode):
            instructions = self._generate_expression(statement.value)
            instructions.append("PRINT")
            return instructions

        if isinstance(statement, IfStmtNode):
            return self._generate_if(statement)

        if isinstance(statement, WhileStmtNode):
            return self._generate_while(statement)

        raise TypeError(f"不支持的语句节点: {statement!r}")

    def _generate_if(self, statement: IfStmtNode) -> list[str]:
        else_label = self._new_label("else")
        end_label = self._new_label("endif")
        instructions = self._generate_expression(statement.condition)
        instructions.append(f"JMP_IF_FALSE {else_label}")

        for node in statement.then_branch:
            instructions.extend(self._generate_statement(node))

        if statement.else_branch:
            instructions.append(f"JMP {end_label}")
            instructions.append(f"LABEL {else_label}")
            for node in statement.else_branch:
                instructions.extend(self._generate_statement(node))
            instructions.append(f"LABEL {end_label}")
        else:
            instructions.append(f"LABEL {else_label}")

        return instructions

    def _generate_while(self, statement: WhileStmtNode) -> list[str]:
        start_label = self._new_label("while_start")
        end_label = self._new_label("while_end")
        instructions = [f"LABEL {start_label}"]
        instructions.extend(self._generate_expression(statement.condition))
        instructions.append(f"JMP_IF_FALSE {end_label}")

        for node in statement.body:
            instructions.extend(self._generate_statement(node))

        instructions.append(f"JMP {start_label}")
        instructions.append(f"LABEL {end_label}")
        return instructions

    def _generate_expression(self, expression) -> list[str]:
        if isinstance(expression, NumNode):
            return [f"PUSH {expression.value}"]

        if isinstance(expression, BoolNode):
            return [f"PUSH {1 if expression.value else 0}"]

        if isinstance(expression, IdentifierNode):
            return [f"LOAD {expression.name}"]

        if isinstance(expression, UnaryOpNode):
            instructions = self._generate_expression(expression.operand)
            instructions.append(self._opcode_for_unary_operator(expression.operator))
            return instructions

        if isinstance(expression, BinaryOpNode):
            instructions = self._generate_expression(expression.left)
            instructions.extend(self._generate_expression(expression.right))
            instructions.append(self._opcode_for_operator(expression.operator))
            return instructions

        raise TypeError(f"不支持的表达式节点: {expression!r}")

    def _opcode_for_operator(self, operator: str) -> str:
        opcodes = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "<": "LT",
            ">": "GT",
            "<=": "LE",
            ">=": "GE",
            "==": "EQ",
            "!=": "NE",
            "&&": "AND",
            "||": "OR",
        }
        if operator not in opcodes:
            raise ValueError(f"不支持的运算符: {operator}")
        return opcodes[operator]

    def _opcode_for_unary_operator(self, operator: str) -> str:
        opcodes = {
            "!": "NOT",
        }
        if operator not in opcodes:
            raise ValueError(f"不支持的一元运算符: {operator}")
        return opcodes[operator]

    def _new_label(self, prefix: str) -> str:
        self.label_count += 1
        return f"{prefix}_{self.label_count}"