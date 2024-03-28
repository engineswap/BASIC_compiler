import sys
from lexer import Lexer
from token_1 import TokenType, Token


class Parser:
    def __init__(self, lexer, emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # vars declared so far
        self.labelsDeclared = set()  # labels declared so far
        self.labelsGotoed = set()  # labels goto'ed so far

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    # Return true if current token matches a type
    def checkToken(self, kind: TokenType) -> bool:
        return kind == self.curToken.kind

    # Return true if next token matches a type
    def checkPeek(self, kind: TokenType) -> bool:
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind: TokenType):
        if not self.checkToken(kind):
            self.abort("Excepted: " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advance the current token
    def nextToken(self) -> None:
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message) -> None:
        sys.exit("Error. " + message)

    # Production rules
    # --------------------------------------

    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(){")

        print("PROGRAM")
        # Skip new lines at the start of our program
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        # Parse all statments in program
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # Wrap up c file
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # Check that each GOTO calls a declared LABEL
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    def statement(self):
        # Check which kind of statement we have

        # "PRINT" (expression | string) nl
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Print simple string
                self.emitter.emitLine('printf("' + self.curToken.text + '\\n");')
                self.nextToken()
            else:
                # We get an expression so lets print the resulting float
                self.emitter.emit('printf("%.2f\\n", (float)(')
                self.expression()  # This will emit the expression result
                self.emitter.emitLine("));")

        # "IF" comparison "THEN" nl {statement} "ENDIF" nl
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()  # this will emit code

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDIF):
                self.statement()
            self.emitter.emitLine("}")
            self.match(TokenType.ENDIF)
        # | "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()
            self.emitter.emitLine("){")

            self.match(TokenType.REPEAT)
            self.nl()

            # >= 0 statements in the body of the loop
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
            self.emitter.emitLine("}")
            self.match(TokenType.ENDWHILE)
        # | "LABEL" ident nl
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            # Make sure Not already declared
            if self.curToken.text in self.labelsDeclared:
                self.abort(self.curToken.text + " LABEL already declared!")
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)
        # | "GOTO" ident nl
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)
        # | "LET" ident "=" expression nl
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()

            # Add INDENT to symbols if it doesnt already exist
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")
        # | "INPUT" ident nl
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()

            # If var doesnt exist, lets add it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")
            # Emit scanf, but check the input. If invalid, set var to 0 and clear input.
            self.emitter.emitLine('if(0==scanf("%f", &' + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit('scanf("%')  # Clean input buffer
            self.emitter.emitLine('*s");')
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)
        else:
            self.abort(
                "Invalid statement: "
                + self.curToken.text
                + " ("
                + self.curToken.kind.name
                + ")"
            )

        # New line after a statement
        self.nl()

    def isComparisonOperator(self):
        return (
            self.checkToken(TokenType.GT)
            or self.checkToken(TokenType.GTEQ)
            or self.checkToken(TokenType.LT)
            or self.checkToken(TokenType.LTEQ)
            or self.checkToken(TokenType.EQEQ)
            or self.checkToken(TokenType.NOTEQ)
        )

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")
        self.expression()
        # at least 1 comparison operator should be here
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort(
                "Expected comparison operator after expression at: "
                + self.curToken.text
            )

        # Possibly more comparison + expressions
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")
        self.term()

        # Can have 0+ ("-"|"+") term
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("TERM")
        self.unary()

        while self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.ASTERISK):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")

        # Optional sign
        if self.checkToken(TokenType.MINUS) or self.checkToken(TokenType.PLUS):
            emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        print("PRIMARY: " + self.curToken.text)
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Make sure IDENT exists
            if self.curToken.text not in self.symbols:
                self.abort(
                    "Referencing variable before assignment: " + self.curToken.text
                )
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")

        self.match(TokenType.NEWLINE)
        # We can have more new lines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
