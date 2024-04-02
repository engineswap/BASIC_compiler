from lexer import Lexer
from parse import Parser
from token_1 import TokenType
from emit import Emitter
import sys

if __name__ == "__main__":
    cliCommand = "python ./main.py target.yolo"
    if len(sys.argv) != 2:
        sys.exit("CLI usage: " + cliCommand)
    with open(sys.argv[1], "r") as sourceFile:
        sourceCode = sourceFile.read()

    lexer = Lexer(sourceCode)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()  # Start the parser
    emitter.writeFile()  # Write file to output
    print(emitter.header + emitter.code)
    print("Parsing complete")

    # token = lexer.getToken()
    # while token.kind != TokenType.EOF:
    #     if token.kind != TokenType.NEWLINE:
    #         print(token.kind, '"' + token.text + '"')
    #     else:
    #         print(token.kind)
    #     token = lexer.getToken()
