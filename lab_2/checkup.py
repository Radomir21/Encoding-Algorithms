with open("test.bin", "rb") as f:
    print([hex(b) for b in f.read()])

#['0xe1', '0x77', '0x0']