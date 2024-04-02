import unittest
import os
from os import listdir
from lexer import Lexer
from parse import Parser
from emit import Emitter


class TestCompilerOutputs(unittest.TestCase):
    def testAll(self):
        # get all directories in /unitTests/c and /unitTests/yolo
        yoloTestDirs = [x[0] for x in os.walk("./unitTests/yolo/")]
        yoloTestDirs.pop(0)

        cTestDirs = [x[0] for x in os.walk("./unitTests/c/")]
        cTestDirs.pop(0)

        if len(cTestDirs) != len(yoloTestDirs):
            os._exit(
                "Unequal numbers of directories in ./unitTests/yolo/ and ./unitTests/c/"
            )

        for dirPath in yoloTestDirs:
            # Get files in dirPath
            sourceCodeFiles = listdir(dirPath)
            for filePath in sourceCodeFiles:
                fullFilePath = dirPath + "/" + filePath
                print("Testing " + fullFilePath)
                with open(fullFilePath, "r") as file:
                    sourceCode = file.read()
                with open(fullFilePath.replace("yolo", "c"), "r") as file:
                    expectedOutput = file.read()

                lexer = Lexer(sourceCode)
                emitter = Emitter("test.c")
                parser = Parser(lexer, emitter)

                parser.program()  # Start the parser
                actualOutput = emitter.header + emitter.code
                self.assertEqual(expectedOutput, actualOutput)


unittest.main()
