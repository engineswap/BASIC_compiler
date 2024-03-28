# Emitter tracks the generated code and outputs it
class Emitter:
    def __init__(self, fullPath) -> None:
        self.fullPath = fullPath
        self.header = ""
        self.code = ""  # The precious c code goes here

    def emit(self, code):
        self.code += code

    def emitLine(self, code):
        self.code += code + "\n"

    def headerLine(self, code):
        self.header += code + "\n"

    def writeFile(self):
        with open(self.fullPath, "w") as outputFile:
            outputFile.write(self.header + self.code)
