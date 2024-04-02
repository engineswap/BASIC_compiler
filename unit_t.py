import unittest
import os
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
    # Base directories
    base_dirs = ["./unitTests/yolo/", "./unitTests/c/"]

    for yolo_base, c_base in zip(*[os.walk(base_dir) for base_dir in base_dirs]):
        print(yolo_base)
        for yolo_dir, _, yolo_files in yolo_base:
            for yolo_file in yolo_files:
                if yolo_file.endswith(".yolo"):
                    yolo_file_path = os.path.join(yolo_dir, yolo_file)
                    c_file_path = yolo_file_path.replace("yolo", "c")
                    test_method = create_test_method(yolo_file_path, c_file_path)
                    test_name = "test_{}".format(
                        os.path.relpath(yolo_file_path, "./unitTests/yolo/")
                        .replace("/", "_")
                        .replace(".yolo", "")
                    )
                    setattr(TestCompilerOutputs, test_name, test_method)


if __name__ == "__main__":
    unittest.main()
