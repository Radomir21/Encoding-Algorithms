import argparse
from Huffman_2 import encode_file, decode_file

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("c")
    c.add_argument("inp")
    c.add_argument("-o", "--out")
    c.add_argument("--bwt", action="store_true")
    c.add_argument("--mtf", action="store_true")
    c.add_argument("--block", type=int, default=4096)

    d = sub.add_parser("d")
    d.add_argument("inp")
    d.add_argument("-o", "--out")

    args = p.parse_args()

    if args.cmd == "c":
        res = encode_file(args.inp, args.out, use_bwt=args.bwt, use_mtf=args.mtf, block_size=args.block)
        print("OK ->", res)
    else:
        res = decode_file(args.inp, args.out)
        print("OK ->", res)

if __name__ == "__main__":
    main()
