#!/usr/bin/env python3
import argparse
import sys

def text_to_binary(text: str) -> str:
    """Convert text to binary representation (8-bit ASCII)."""
    return ' '.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_str: str) -> str:
    """Convert binary string (space-separated 8-bit values) to text."""
    bits = binary_str.split()
    if not all(len(b) == 8 and set(b) <= {"0", "1"} for b in bits):
        raise ValueError("Invalid binary format. Use 8-bit binary values separated by spaces.")
    return ''.join(chr(int(b, 2)) for b in bits)

def save_binary_file(binary_str: str, filename: str = "binary_output.bin") -> None:
    """Save binary data to a file."""
    bits = binary_str.split()
    if not all(len(b) == 8 and set(b) <= {"0", "1"} for b in bits):
        raise ValueError("Output is not valid binary data.")
    with open(filename, "wb") as f:
        f.write(bytes(int(b, 2) for b in bits))
    print(f"? Binary file saved as {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Text ? Binary Converter CLI Tool"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Convert text to binary")
    group.add_argument("--binary", help="Convert binary to text")
    parser.add_argument("--save", help="Save binary output to file", action="store_true")
    parser.add_argument("--output", help="Specify output filename (default: binary_output.bin)")

    args = parser.parse_args()

    try:
        if args.text:
            binary_str = text_to_binary(args.text)
            print(f"Binary Output:\n{binary_str}")
            if args.save:
                filename = args.output if args.output else "binary_output.bin"
                save_binary_file(binary_str, filename)

        elif args.binary:
            text = binary_to_text(args.binary)
            print(f"Text Output:\n{text}")

    except Exception as e:
        print(f"? Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
