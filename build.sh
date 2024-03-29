# Check if an argument was provided
if [ $# -eq 0 ]; then
    echo "Source code argument required."
    exit 1
fi

# Use the first argument with the Python script
python main.py "$1"

g++ -o out out.c

if [ $? -eq 0 ]; then
    echo "Compilation successful."
else
    echo "Compilation failed."
    exit 1
fi
