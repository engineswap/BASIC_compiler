import sys
from token_1 import TokenType, Token


class Lexer:
    def __init__(self, source):
        self.source = source + "\n"
        # Track the current char we're at
        self.curChar = ""
        self.curPos = -1
        self.nextChar()

    # Process the next character.
    def nextChar(self) -> None:
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = "\0"  # End of text
        else:
            self.curChar = self.source[self.curPos]

    # Return the lookahead character.
    def peek(self) -> str:
        if self.curPos + 1 >= len(self.source):
            return "\0"  # End of text
        return self.source[self.curPos + 1]

    # Invalid token found, print error message and exit.
    def abort(self, message) -> None:
        sys.exit("Lexing error: " + message)

    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skipWhitespace(self) -> None:
        while self.curChar in [" ", "\t", "\r"]:
            self.nextChar()

    # Skip comments in the code.
    def skipComment(self) -> None:
        if self.curChar == "#":
            while self.curChar != "\n":
                self.nextChar()

    # Return the next token.
    def getToken(self) -> Token:
        self.skipWhitespace()
        self.skipComment()
        token = None

        # Operator tokens
        if self.curChar == "+":
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == "-":
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == "*":
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == "/":
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == "\n":
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == "=":
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == "\0":  # EOF token
            token = Token(self.curChar, TokenType.EOF)
        elif self.curChar == ">":
            # Could be >, >=
            if self.peek() == "=":  # >=
                lastChar = self.curChar
                self.nextChar()
                token = Token(self.curChar, TokenType.GTEQ)
            else:  # >
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == "<":
            # Could be <, <=
            if self.peek() == "=":  # <=
                lastChar = self.curChar
                self.nextChar()
                token = Token(self.curChar, TokenType.LTEQ)
            else:  # <
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == "!":
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == '"':
            self.nextChar()
            startPos = self.curPos
            while self.curChar != '"':
                if self.curChar in ["\r", "\n", "\t", "\\", "%"]:
                    self.abort("Illegal char in string")
                self.nextChar()
            tokText = self.source[startPos : self.curPos]
            token = Token(tokText, TokenType.STRING)
        elif self.curChar.isdigit():
            # Leading char is a digit, so this should be a number
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.curChar == ".":
                self.nextChar()
                # Check for legal decimal
                if not self.peek().isdigit():
                    self.abort("Number required after decimal point.")
                while self.peek().isdigit():
                    self.nextChar()
            tokText = self.source[startPos : self.curPos + 1]
            token = Token(tokText, TokenType.NUMBER)
        elif self.curChar.isalpha():
            # Keyword / variable name
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()
            tokText = self.source[startPos : self.curPos + 1]

            if Token.isKeyword(tokText):
                token = Token(tokText, TokenType[tokText])
            elif Token.isBoolean(tokText):
                token = Token(tokText, TokenType.BOOLEAN)
            else:
                token = Token(tokText, TokenType.IDENT)
        else:
            # Unknown token
            self.abort("Unknown token: " + self.curChar)
        self.nextChar()
        return token
