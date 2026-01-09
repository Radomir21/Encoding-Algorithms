# main.py
import sys
from huffman import encode_file, decode_file

# usage:
# python main.py c input_file [output_file]
# python main.py d input_file [output_file]

if len(sys.argv) < 3:
    print("Usage:")
    print("  python main.py c input_file [output_file]")
    print("  python main.py d input_file [output_file]")
    sys.exit(1)

cmd = sys.argv[1]
inp = sys.argv[2]
out = sys.argv[3] if len(sys.argv) >= 4 else None

if cmd == "c":
    res = encode_file(inp, out)
    print("OK compressed ->", res)
elif cmd == "d":
    res = decode_file(inp, out)
    print("OK decompressed ->", res)
else:
    print("Unknown command:", cmd)
