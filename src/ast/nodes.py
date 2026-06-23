from dataclasses import dataclass, field


class Node:
    def __repr__(self) -> str:
        fields = ", ".join(
            f"{name}={value!r}" for name, value in vars(self).items()
        )
        return f"{self.__class__.__name__}({fields})"


@dataclass(repr=False)
class ProgramNode(Node):
    statements: list[Node] = field(default_factory=list)


@dataclass(repr=False)
class VarDeclNode(Node):
    var_type: str
    identifier: "IdentifierNode"
    initializer: Node | None = None


@dataclass(repr=False)
class AssignmentNode(Node):
    identifier: "IdentifierNode"
    value: Node


@dataclass(repr=False)
class IfStmtNode(Node):
    condition: Node
    then_branch: list[Node] = field(default_factory=list)
    else_branch: list[Node] = field(default_factory=list)


@dataclass(repr=False)
class WhileStmtNode(Node):
    condition: Node
    body: list[Node] = field(default_factory=list)


@dataclass(repr=False)
class PrintStmtNode(Node):
    value: Node


@dataclass(repr=False)
class BinaryOpNode(Node):
    left: Node
    operator: str
    right: Node


@dataclass(repr=False)
class UnaryOpNode(Node):
    operator: str
    operand: Node


@dataclass(repr=False)
class NumNode(Node):
    value: int


@dataclass(repr=False)
class BoolNode(Node):
    value: bool


@dataclass(repr=False)
class IdentifierNode(Node):
    name: str


@dataclass(repr=False)
class TokenNode(Node):
    token_type: str
    lexeme: str


Program = ProgramNode