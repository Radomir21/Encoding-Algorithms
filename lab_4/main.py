# main.py
import argparse
from lzw import lzw_compress, lzw_decompress


def build_arg_parser():
    p = argparse.ArgumentParser(description="LZW compressor/decompressor")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("c", help="compress")
    c.add_argument("input", help="input file")
    c.add_argument("-o", "--output", default=None, help="output file (.lzw by default)")
    c.add_argument("--max-bits", type=int, default=16, help="9..16 (dict size = 2^max_bits)")
    c.add_argument("--overflow", choices=["freeze", "reset"], default="reset",
                   help="dictionary overflow behavior")

    d = sub.add_parser("d", help="decompress")
    d.add_argument("input", help="input .lzw file")
    d.add_argument("-o", "--output", default=None, help="output file (strip .lzw by default)")

    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.cmd == "c":
        out = lzw_compress(
            input_path=args.input,
            output_path=args.output,
            max_bits=args.max_bits,
            overflow_mode=args.overflow
        )
        print("Compressed to:", out)

    elif args.cmd == "d":
        out = lzw_decompress(
            input_path=args.input,
            output_path=args.output
        )
        print("Decompressed to:", out)


if __name__ == "__main__":
    main()
