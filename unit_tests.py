from types import MethodType
import unittest
import os
from os import listdir
from lexer import Lexer
from parse import Parser
from emit import Emitter


def create_test_method(yolo_file_path, c_file_path):
    def test(self):
        print("Testing " + yolo_file_path)
        with open(yolo_file_path, "r") as file:
            sourceCode = file.read()
        with open(c_file_path, "r") as file:
            expectedOutput = file.read()

        lexer = Lexer(sourceCode)
        emitter = Emitter("test.c")
        parser = Parser(lexer, emitter)

        parser.program()  # Start the parser
        actualOutput = emitter.header + emitter.code
        self.assertEqual(expectedOutput, actualOutput)

    return test


class TestCompilerOutputs(unittest.TestCase):
    pass


def load_tests(loader, tests, pattern):
    base_dirs = ["./unitTests/yolo/", "./unitTests/c/"]

    yoloTestDirs = [x[0] for x in os.walk(base_dirs[0])]
    yoloTestDirs.pop(0)

    cTestDirs = [x[0] for x in os.walk("./unitTests/c/")]
    cTestDirs.pop(0)

    if len(cTestDirs) != len(yoloTestDirs):
        os._exit(
            "Unequal numbers of directories in ./unitTests/yolo/ and ./unitTests/c/"
        )
    suite = unittest.TestSuite()

    for dirPath in yoloTestDirs:
        # Get files in dirPath
        sourceCodeFiles = listdir(dirPath)
        for filePath in sourceCodeFiles:
            if not filePath.endswith(".yolo"):
                continue
            yoloFilePath = dirPath + "/" + filePath
            cFilePath = yoloFilePath.replace("yolo", "c")
            test_method = create_test_method(yoloFilePath, cFilePath)
            test_name = "test_{}".format(
                os.path.relpath(yoloFilePath, "./unitTests/yolo/")
                .replace("/", "_")
                .replace(".yolo", "")
            )
            print(test_name)
            test_case = TestCompilerOutputs()
            setattr(test_case, test_name, test_method)
            # Add a method called 'runTest' that is the test method we just added
            setattr(test_case, "runTest", MethodType(test_method, test_case))
            suite.addTest(test_case)
    return suite


unittest.main()
