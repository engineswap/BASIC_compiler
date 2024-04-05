import sys
from lexer import Lexer
from token_1 import TokenType, Token
import pydot


class Parser:
    def __init__(self, lexer, emitter) -> None:
        # Graph
        self.graph = pydot.Dot(graph_type="digraph")
        self.node_count = 0

        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # vars declared so far
        self.labelsDeclared = set()  # labels declared so far
        self.labelsGotoed = set()  # labels goto'ed so far

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def add_node(self, label, parent=None, leaf=False):
        if leaf:
            node = pydot.Node(
                self.node_count,
                label=label,
                style="filled",
                fillcolor="grey",
                fontcolor="white",
            )
        else:
            node = pydot.Node(
                self.node_count,
                label=label,
                shape="square",
                style="filled",
                fillcolor="black",
                fontcolor="white",
            )
        self.graph.add_node(node)
        if parent is not None:
            self.graph.add_edge(pydot.Edge(parent, node))
        self.parent = node
        self.node_count += 1
        return node

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

        program_node = self.add_node("Program")

        # Skip new lines at the start of our program
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        # Parse all statments in program
        while not self.checkToken(TokenType.EOF):
            self.statement(program_node)

        # Wrap up c file
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # Check that each GOTO calls a declared LABEL
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

        self.graph.write_png("parse_tree.png")

    def statement(self, parent_node: pydot.Node):
        # Check which kind of statement we have
        statement_node = self.add_node("Statement", parent_node)

        # "PRINT" (expression | string) nl
        if self.checkToken(TokenType.PRINT):
            self.add_node("PRINT", statement_node, True)
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                stringNode = self.add_node("String", statement_node)
                self.add_node(self.curToken.text, stringNode, True)
                # Print simple string
                self.emitter.emitLine('printf("' + self.curToken.text + '\\n");')
                self.nextToken()
            else:
                # We get an expression so lets print the resulting float
                self.emitter.emit('printf("%.2f\\n", (float)(')
                self.expression(statement_node)  # This will emit the expression result
                self.emitter.emitLine("));")

        # "IF" (comparison) "THEN" nl {statement} "ENDIF" nl
        elif self.checkToken(TokenType.IF):
            self.add_node("IF", statement_node, True)
            self.nextToken()

            self.match(TokenType.OPEN_PAREN)

            self.emitter.emit("if(")
            self.comparison(statement_node)

            self.match(TokenType.CLOSE_PAREN)

            self.match(TokenType.THEN)
            self.add_node("THEN", statement_node, True)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDIF):
                self.statement(statement_node)
            self.emitter.emitLine("}")
            self.match(TokenType.ENDIF)
            self.add_node("ENDIF", statement_node, True)
        # | "WHILE" (comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
        elif self.checkToken(TokenType.WHILE):
            self.add_node("WHILE", statement_node, True)
            self.nextToken()
            self.match(TokenType.OPEN_PAREN)

            self.emitter.emit("while(")
            self.comparison(statement_node)
            self.emitter.emitLine("){")

            self.match(TokenType.CLOSE_PAREN)
            self.add_node("REPEAT", statement_node, True)
            self.match(TokenType.REPEAT)
            self.nl()

            # >= 0 statements in the body of the loop
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement(statement_node)
            self.emitter.emitLine("}")
            self.match(TokenType.ENDWHILE)
        # "FOR" "(" for_assignment ";" comparison ";" for_declaration ")" "DO" nl {statement} "ENDFOR" nl
        elif self.checkToken(TokenType.FOR):
            self.add_node("FOR", statement_node, True)
            self.nextToken()
            self.match(TokenType.OPEN_PAREN)

            self.emitter.emit("for(")
            self.for_declaration(statement_node)
            self.match(TokenType.SEMICOLON)
            self.emitter.emit(";")
            self.comparison(statement_node)
            self.match(TokenType.SEMICOLON)
            self.emitter.emit(";")
            self.for_assignment(statement_node)
            self.match(TokenType.CLOSE_PAREN)
            self.match(TokenType.REPEAT)
            self.emitter.emitLine("){")
            self.nl()
            # >= 0 statements in the body of the loop
            while not self.checkToken(TokenType.ENDFOR):
                self.statement(statement_node)
            self.emitter.emitLine("}")
            self.match(TokenType.ENDFOR)

        # | "LABEL" ident nl
        elif self.checkToken(TokenType.LABEL):
            self.add_node("LABEL", statement_node, True)
            self.nextToken()
            # Make sure Not already declared
            if self.curToken.text in self.labelsDeclared:
                self.abort(self.curToken.text + " LABEL already declared!")
            self.labelsDeclared.add(self.curToken.text)

            self.add_node(self.curToken.text, statement_node, True)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)
        # | "GOTO" ident nl
        elif self.checkToken(TokenType.GOTO):
            self.add_node("GOTO", statement_node, True)
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.add_node(self.curToken.text, statement_node, True)
            self.match(TokenType.IDENT)
        # | "LET" ident "=" expression nl
        elif self.checkToken(TokenType.LET):
            self.add_node("LET", statement_node, True)
            self.nextToken()

            # Add INDENT to symbols if it doesnt already exist
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            ident_node = self.add_node("Ident", statement_node)
            self.add_node(self.curToken.text, ident_node, True)
            self.add_node("=", statement_node, True)

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression(statement_node)
            self.emitter.emitLine(";")
        # | "INPUT" ident nl
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()
            self.add_node("INPUT", statement_node, True)

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
            ident_node = self.add_node("Ident", statement_node)
            self.add_node(self.curToken.text, ident_node, True)
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

    # assignment ::= "LET" ident "=" expression
    def for_declaration(self, parent_node: pydot.Node):
        for_declaration_node = self.add_node("for_declaration", parent_node)

        self.match(TokenType.LET)
        self.add_node(self.curToken.text, for_declaration_node, True)
        self.emitter.emit("int " + self.curToken.text)
        self.symbols.add(self.curToken.text)
        self.match(TokenType.IDENT)
        self.add_node(self.curToken.text, for_declaration_node, True)
        self.emitter.emit("=")
        self.match(TokenType.EQ)
        self.expression(for_declaration_node)

    # declaration ::= ident "=" expression
    def for_assignment(self, parent_node: pydot.Node):
        for_assignment_node = self.add_node("for_assignment", parent_node)
        self.emitter.emit(self.curToken.text)
        self.symbols.add(self.curToken.text)
        self.add_node(self.curToken.text, for_assignment_node, True)
        self.match(TokenType.IDENT)
        self.add_node(self.curToken.text, for_assignment_node, True)
        self.emitter.emit("=")
        self.match(TokenType.EQ)
        self.expression(for_assignment_node)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self, parent_node: pydot.Node):
        expression_node = self.add_node("Expression", parent_node)
        self.expression(expression_node)
        # at least 1 comparison operator should be here
        if self.isComparisonOperator():
            comparison_node = self.add_node("Comparison", expression_node)
            self.add_node(self.curToken.text, comparison_node, True)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression(expression_node)
        else:
            self.abort(
                "Expected comparison operator after expression at: "
                + self.curToken.text
            )

        # Possibly more comparison + expressions
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression(expression_node)

    # expression ::= term {( "-" | "+" ) term}
    def expression(self, parent_node: pydot.Node):
        expression_node = self.add_node("Expression", parent_node)
        self.term(expression_node)

        # Can have 0+ ("-"|"+") term
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.add_node(self.curToken.text, expression_node, True)
            self.nextToken()
            self.term(expression_node)

    # term ::= unary {( "/" | "*" ) unary}
    def term(self, parent_node: pydot.Node):
        term_node = self.add_node("Term", parent_node)
        self.unary(term_node)

        while self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.ASTERISK):
            self.add_node(self.curToken.text, term_node, True)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary(term_node)

    # unary ::= ["+" | "-"] primary
    def unary(self, parent_node: pydot.Node):
        unary_node = self.add_node("Unary", parent_node)

        # Optional sign
        if self.checkToken(TokenType.MINUS) or self.checkToken(TokenType.PLUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary(unary_node)

    # primary ::= number | ident
    def primary(self, parent_node: pydot.Node):
        primary_node = self.add_node("Primary", parent_node)

        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            number_node = self.add_node("Number", primary_node)
            self.add_node(self.curToken.text, number_node, True)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Make sure IDENT exists
            if self.curToken.text not in self.symbols:
                self.abort(
                    "Referencing variable before assignment: " + self.curToken.text
                )
            ident_node = self.add_node("Ident", primary_node)
            self.add_node(self.curToken.text, ident_node, True)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.OPEN_PAREN):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.add_node("(", primary_node, True)
            self.expression(primary_node)
            self.emitter.emit(self.curToken.text)
            self.match(TokenType.CLOSE_PAREN)
            self.add_node(")", primary_node, True)
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):

        self.match(TokenType.NEWLINE)
        # We can have more new lines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
