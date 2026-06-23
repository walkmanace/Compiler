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


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: list[dict[str, str]] = []

    def analyze(self, program: ProgramNode) -> None:
        if not isinstance(program, ProgramNode):
            raise TypeError("语义分析输入必须是 ProgramNode 节点")

        self.scopes = [{}]
        self._analyze_statements(program.statements)

    def _analyze_statements(self, statements: list) -> None:
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement) -> None:
        if isinstance(statement, VarDeclNode):
            self._analyze_var_decl(statement)
            return

        if isinstance(statement, AssignmentNode):
            target_type = self._ensure_declared(statement.identifier.name)
            value_type = self._analyze_expression(statement.value)
            if target_type != value_type:
                raise SemanticError(
                    f"赋值类型不匹配: 变量 '{statement.identifier.name}' 是 {target_type}，表达式是 {value_type}"
                )
            return

        if isinstance(statement, IfStmtNode):
            condition_type = self._analyze_expression(statement.condition)
            if condition_type != "bool":
                raise SemanticError("if 条件表达式必须是 bool 类型")
            self._with_new_scope(statement.then_branch)
            self._with_new_scope(statement.else_branch)
            return

        if isinstance(statement, WhileStmtNode):
            condition_type = self._analyze_expression(statement.condition)
            if condition_type != "bool":
                raise SemanticError("while 条件表达式必须是 bool 类型")
            self._with_new_scope(statement.body)
            return

        if isinstance(statement, PrintStmtNode):
            self._analyze_expression(statement.value)
            return

        raise SemanticError(f"不支持的语句节点: {statement!r}")

    def _analyze_var_decl(self, statement: VarDeclNode) -> None:
        current_scope = self.scopes[-1]
        name = statement.identifier.name

        if name in current_scope:
            raise SemanticError(f"变量重复声明: '{name}'")

        if statement.initializer is not None:
            initializer_type = self._analyze_expression(statement.initializer)
            if initializer_type != statement.var_type:
                raise SemanticError(
                    f"变量初始化类型不匹配: 变量 '{name}' 是 {statement.var_type}，表达式是 {initializer_type}"
                )

        current_scope[name] = statement.var_type

    def _analyze_expression(self, expression) -> str:
        if isinstance(expression, NumNode):
            return "int"

        if isinstance(expression, BoolNode):
            return "bool"

        if isinstance(expression, IdentifierNode):
            return self._ensure_declared(expression.name)

        if isinstance(expression, BinaryOpNode):
            left_type = self._analyze_expression(expression.left)
            right_type = self._analyze_expression(expression.right)
            return self._binary_result_type(expression.operator, left_type, right_type)

        if isinstance(expression, UnaryOpNode):
            operand_type = self._analyze_expression(expression.operand)
            return self._unary_result_type(expression.operator, operand_type)

        raise SemanticError(f"不支持的表达式节点: {expression!r}")

    def _binary_result_type(self, operator: str, left_type: str, right_type: str) -> str:
        arithmetic_ops = {"+", "-", "*", "/"}
        relational_ops = {"<", ">", "<=", ">="}
        equality_ops = {"==", "!="}
        logical_ops = {"&&", "||"}

        if operator in arithmetic_ops:
            if left_type != "int" or right_type != "int":
                raise SemanticError(f"算术运算 '{operator}' 只支持 int 类型")
            return "int"

        if operator in relational_ops:
            if left_type != "int" or right_type != "int":
                raise SemanticError(f"关系运算 '{operator}' 只支持 int 类型")
            return "bool"

        if operator in equality_ops:
            if left_type != right_type:
                raise SemanticError(
                    f"相等运算 '{operator}' 两侧类型必须一致，当前是 {left_type} 和 {right_type}"
                )
            return "bool"

        if operator in logical_ops:
            if left_type != "bool" or right_type != "bool":
                raise SemanticError(f"逻辑运算 '{operator}' 只支持 bool 类型")
            return "bool"

        raise SemanticError(f"不支持的运算符: '{operator}'")

    def _unary_result_type(self, operator: str, operand_type: str) -> str:
        if operator == "!":
            if operand_type != "bool":
                raise SemanticError("逻辑非 '!' 只支持 bool 类型")
            return "bool"

        raise SemanticError(f"不支持的一元运算符: '{operator}'")

    def _ensure_declared(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"使用了未声明的变量: '{name}'")

    def _with_new_scope(self, statements: list) -> None:
        self.scopes.append({})
        try:
            self._analyze_statements(statements)
        finally:
            self.scopes.pop()