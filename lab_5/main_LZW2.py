import argparse
from LZW_2 import lzw_compress, lzw_decompress


def main():
    p = argparse.ArgumentParser(description="LZW compressor with optional BWT / MTF")

    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("c", help="compress")
    c.add_argument("inp", help="input file")
    c.add_argument("-o", "--out", help="output file")

    c.add_argument("--bwt", action="store_true", help="enable BWT")
    c.add_argument("--mtf", action="store_true", help="enable MTF")
    c.add_argument("--block", type=int, default=4096, help="BWT block size")

    c.add_argument("--max-bits", type=int, default=16, help="max code width (9..16)")
    c.add_argument("--overflow", choices=["reset", "freeze"], default="reset",
                   help="dictionary overflow mode")

    d = sub.add_parser("d", help="decompress")
    d.add_argument("inp", help="input .lzw file")
    d.add_argument("-o", "--out", help="output file")

    args = p.parse_args()

    if args.cmd == "c":
        res = lzw_compress(
            input_path=args.inp,
            output_path=args.out,
            max_bits=args.max_bits,
            overflow_mode=args.overflow,
            use_bwt=args.bwt,
            use_mtf=args.mtf,
            block_size=args.block
        )
        print("OK ->", res)

    else:  # d
        res = lzw_decompress(
            input_path=args.inp,
            output_path=args.out
        )
        print("OK ->", res)


if __name__ == "__main__":
    main()
