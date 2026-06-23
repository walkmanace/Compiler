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
from src.frontend.lexer import Token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ProgramNode:
        statements = []

        while not self._check("EOF"):
            statements.append(self._statement())

        return ProgramNode(statements=statements)

    def _statement(self):
        if self._match("INT", "BOOL"):
            return self._var_decl(self._previous().lexeme)
        if self._match("IF"):
            return self._if_stmt()
        if self._match("WHILE"):
            return self._while_stmt()
        if self._match("PRINT"):
            return self._print_stmt()
        if self._check("IDENT"):
            return self._assignment()
        raise self._error("无法识别的语句")

    def _var_decl(self, var_type: str) -> VarDeclNode:
        identifier = IdentifierNode(self._consume("IDENT", "变量声明缺少标识符").lexeme)
        initializer = None

        if self._match("ASSIGN"):
            initializer = self._expression()

        self._consume("SEMICOLON", "变量声明缺少分号")
        return VarDeclNode(var_type=var_type, identifier=identifier, initializer=initializer)

    def _assignment(self) -> AssignmentNode:
        identifier = IdentifierNode(self._consume("IDENT", "赋值语句缺少变量名").lexeme)
        self._consume("ASSIGN", "赋值语句缺少 '='")
        value = self._expression()
        self._consume("SEMICOLON", "赋值语句缺少分号")
        return AssignmentNode(identifier=identifier, value=value)

    def _if_stmt(self) -> IfStmtNode:
        self._consume("LPAREN", "if 条件缺少 '('")
        condition = self._expression()
        self._consume("RPAREN", "if 条件缺少 ')'")
        then_branch = self._block()

        else_branch = []
        if self._match("ELSE"):
            else_branch = self._block()

        return IfStmtNode(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def _while_stmt(self) -> WhileStmtNode:
        self._consume("LPAREN", "while 条件缺少 '('")
        condition = self._expression()
        self._consume("RPAREN", "while 条件缺少 ')'")
        body = self._block()
        return WhileStmtNode(condition=condition, body=body)

    def _print_stmt(self) -> PrintStmtNode:
        self._consume("LPAREN", "print 缺少 '('")
        value = self._expression()
        self._consume("RPAREN", "print 缺少 ')'")
        self._consume("SEMICOLON", "print 语句缺少分号")
        return PrintStmtNode(value=value)

    def _block(self) -> list:
        self._consume("LBRACE", "代码块缺少 '{'")
        statements = []

        while not self._check("RBRACE") and not self._check("EOF"):
            statements.append(self._statement())

        self._consume("RBRACE", "代码块缺少 '}'")
        return statements

    def _expression(self):
        return self._or()

    def _or(self):
        node = self._and()

        while self._match("OR"):
            operator = self._previous().lexeme
            right = self._and()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _and(self):
        node = self._equality()

        while self._match("AND"):
            operator = self._previous().lexeme
            right = self._equality()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _equality(self):
        node = self._comparison()

        while self._match("EQ", "NE"):
            operator = self._previous().lexeme
            right = self._comparison()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _comparison(self):
        node = self._term()

        while self._match("LT", "GT", "LE", "GE"):
            operator = self._previous().lexeme
            right = self._term()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _term(self):
        node = self._factor()

        while self._match("PLUS", "MINUS"):
            operator = self._previous().lexeme
            right = self._factor()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _factor(self):
        node = self._unary()

        while self._match("STAR", "SLASH"):
            operator = self._previous().lexeme
            right = self._unary()
            node = BinaryOpNode(left=node, operator=operator, right=right)

        return node

    def _unary(self):
        if self._match("NOT"):
            return UnaryOpNode(operator=self._previous().lexeme, operand=self._unary())

        return self._primary()

    def _primary(self):
        if self._match("NUMBER"):
            return NumNode(value=int(self._previous().lexeme))

        if self._match("TRUE"):
            return BoolNode(value=True)

        if self._match("FALSE"):
            return BoolNode(value=False)

        if self._match("IDENT"):
            return IdentifierNode(name=self._previous().lexeme)

        if self._match("LPAREN"):
            expression = self._expression()
            self._consume("RPAREN", "表达式缺少 ')'")
            return expression

        raise self._error("表达式不完整")

    def _match(self, *token_types: str) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self.current += 1
                return True
        return False

    def _consume(self, token_type: str, message: str) -> Token:
        if self._check(token_type):
            self.current += 1
            return self._previous()
        raise self._error(message)

    def _check(self, token_type: str) -> bool:
        if self._is_at_end():
            return token_type == "EOF"
        return self._peek().token_type == token_type

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().token_type == "EOF"

    def _error(self, message: str) -> SyntaxError:
        token = self._peek()
        return SyntaxError(
            f"{message}，位置 {token.line}:{token.column}，当前记号 {token.token_type}"
        )