from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    token_type: str
    lexeme: str
    line: int
    column: int


class Lexer:
    KEYWORDS = {
        "int": "INT",
        "bool": "BOOL",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "print": "PRINT",
        "true": "TRUE",
        "false": "FALSE",
    }

    SINGLE_CHAR_TOKENS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "!": "NOT",
        "=": "ASSIGN",
        "<": "LT",
        ">": "GT",
        ";": "SEMICOLON",
        "{": "LBRACE",
        "}": "RBRACE",
        "(": "LPAREN",
        ")": "RPAREN",
    }

    DOUBLE_CHAR_TOKENS = {
        "&&": "AND",
        "||": "OR",
        "==": "EQ",
        "<=": "LE",
        ">=": "GE",
        "!=": "NE",
    }

    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while not self._is_at_end():
            current = self._peek()

            if current in {" ", "\t", "\r"}:
                self._advance()
                continue

            if current == "\n":
                self._advance_newline()
                continue

            if current.isalpha() or current == "_":
                tokens.append(self._read_identifier())
                continue

            if current.isdigit():
                tokens.append(self._read_number())
                continue

            two_char = current + self._peek_next()
            token_type = self.DOUBLE_CHAR_TOKENS.get(two_char)
            if token_type is not None:
                tokens.append(self._make_token(token_type, two_char))
                self._advance()
                self._advance()
                continue

            token_type = self.SINGLE_CHAR_TOKENS.get(current)
            if token_type is not None:
                tokens.append(self._make_token(token_type, current))
                self._advance()
                continue

            raise SyntaxError(
                f"无法识别的字符 {current!r}，位置 {self.line}:{self.column}"
            )

        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens

    def _read_identifier(self) -> Token:
        start = self.index
        line = self.line
        column = self.column

        while not self._is_at_end() and (
            self._peek().isalnum() or self._peek() == "_"
        ):
            self._advance()

        lexeme = self.source[start:self.index]
        token_type = self.KEYWORDS.get(lexeme, "IDENT")
        return Token(token_type, lexeme, line, column)

    def _read_number(self) -> Token:
        start = self.index
        line = self.line
        column = self.column

        while not self._is_at_end() and self._peek().isdigit():
            self._advance()

        lexeme = self.source[start:self.index]
        return Token("NUMBER", lexeme, line, column)

    def _make_token(self, token_type: str, lexeme: str) -> Token:
        return Token(token_type, lexeme, self.line, self.column)

    def _peek(self) -> str:
        return self.source[self.index]

    def _peek_next(self) -> str:
        if self.index + 1 >= len(self.source):
            return ""
        return self.source[self.index + 1]

    def _advance(self) -> str:
        current = self.source[self.index]
        self.index += 1
        self.column += 1
        return current

    def _advance_newline(self) -> None:
        self.index += 1
        self.line += 1
        self.column = 1

    def _is_at_end(self) -> bool:
        return self.index >= len(self.source)