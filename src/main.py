import sys;
import io;
import typing;
import re;
import enum;

class Segment:
    def __init__(self, name: str, code: bytes) -> None:
        self.name: str = name;
        self.code: bytes = code;
    def __repr__(self) -> str:
        return f"(({self.name}))";

class Link:
    def __init__(self, name: str, size: int, prefix: bytes, suffix: bytes) -> None:
        self.name: str = name;
        self.size: int = size;
        self.prefix: bytes = prefix;
        self.suffix: bytes = suffix;
    def __repr__(self) -> str:
        return f"(({self.name}, {self.size}))";

class CompilationMode(enum.Enum):
    Code = 0;
    Link = 1;

def comp_str(source: str) -> bytes:
    ret:      bytes;
    src:      list[str];
    segments: list[Segment];
    linker:   list[Link];
    Mode:     CompilationMode;
    i:        int;
    V:        int;
    x:        int;
    sign:     int;
    line:     int;
    identifer_regex: re.Pattern;

    segments  = [Segment("$", b'')];
    linker    = [Link("$", -1, b'', b'')];
    Mode      = CompilationMode.Code;
    src = [ a for a in re.split("(\n)+|[\r\t\f ]+|(;)|(\".*\")|('.')", source) if a != '' and a != None ];

    identifier_regex = re.compile("[A-Z|a-z][A-Z|a-z|0-9|_]+");

    line      = 0;
    i = 0;
    while i < len(src):
        match src[i]:
            case "\n":
                line += 1;
            case "CODE:":
                Mode = CompilationMode.Code;
            case "LINK:":
                Mode = CompilationMode.Link;
            case "HEX":
                if Mode != CompilationMode.Code:
                    print(f"Invalid instruction `HEX` in non CODE mode: on line {line}");
                    exit(1);
                while i < len(src):
                    i += 1;
                    if src[i] == ';': break;
                    V = 0;
                    try:
                        sign = int(src[i], 0x10)//abs(int(src[i], 0x10)) if int(src[i], 0x10) != 0 else 0;
                        x =  (abs(int(src[i], 0x10)) & 0xFF);
                        if sign < 0:
                            x = ((~x) + 1) & 0xFF;
                        segments[-1].code += x.to_bytes(1);
                    except ValueError:
                        if src[i][0] == '\'':
                            segments[-1].code += bytes(src[i][1], 'utf-8')[0:1];
                        elif src[i][0] == '"':
                            src[i] = src[i][1:-1];
                            segments[-1].code += bytes(src[i], 'utf-8');
                        else:
                            print(f"Expected integer/string/char for HEX: on line {line}");
                            exit(1);

                if i == len(src):
                    print(f"Expected end on HEX: on line {line}");
                    exit(1);
            case "SEGMENT":
                i += 1;
                if i >= len(src) or identifier_regex.match(src[i]) == None:
                    print(f"SEGMENT expected identifier argument: on line {line}");
                    exit(1);
                match Mode:
                    case CompilationMode.Code:
                        if len([a for a in segments if a.name == src[i]]):
                            print(f"SEGMENT redefines `{src[i]}`: on line {line}");
                            exit(1);
                        segments.append(Segment(src[i], b''));
                    case CompilationMode.Link:
                        if len([a for a in linker if a.name == src[i]]):
                            print(f"SEGMENT redefines `{src[i]}`: on line {line}");
                            exit(1);
                        linker.append(Link(src[i], -1, b'', b''));
            case ".SIZEOF":
                i += 1;
                if i >= len(src):
                    print(f".SIZEOF expected integer argument: on line {line}");
                    exit(1);
                if Mode != CompilationMode.Link:
                    print(f"Invalid instruction `.SIZEOF` in non LINK mode: on line {line}");
                    exit(1);
                if src[i] == "-1":
                    linker[-1].size = -1;
                else:
                    try:
                        x = int(src[i], 0x10);
                        if x < 0:
                            print(f".SIZEOF must be `-1` or any positive hex: on line {line}");
                            exit(1);
                        linker[-1].size = x;
                    except ValueError:
                        print(f".SIZEOF expected integer argument: on line {line}");
                        exit(1);
            case ".SUFFIX":
                if i+1 >= len(src):
                    print(f".SUFFIX expected integer argument: on line {line}");
                    exit(1);
                if Mode != CompilationMode.Link:
                    print(f"Invalid instruction `.SUFFIX` in non LINK mode: on line {line}");
                    exit(1);
                while i < len(src):
                    i += 1;
                    if src[i] == ';': break;
                    V = 0;
                    try:
                        sign = int(src[i], 0x10)//abs(int(src[i], 0x10)) if int(src[i], 0x10) != 0 else 0;
                        x =  (abs(int(src[i], 0x10)) & 0xFF);
                        if sign < 0:
                            x = ((~x) + 1) & 0xFF;
                        linker[-1].suffix += x.to_bytes(1);
                    except ValueError:
                        if src[i][0] == '\'':
                            linker[-1].suffix += bytes(src[i][1], 'utf-8')[0:1];
                        elif src[i][0] == '"':
                            src[i] = src[i][1:-1];
                            linker[-1].suffix += bytes(src[i], 'utf-8');
                        else:
                            print(f"Expected integer/string/char for .SUFFIX: on line {line}");
                            exit(1);
            case ".PREFIX":
                if i+1 >= len(src):
                    print(f".PREFIX expected integer argument: on line {line}");
                    exit(1);
                if Mode != CompilationMode.Link:
                    print(f"Invalid instruction `.PREFIX` in non LINK mode: on line {line}");
                    exit(1);
                while i < len(src):
                    i += 1;
                    if src[i] == ';': break;
                    V = 0;
                    try:
                        sign = int(src[i], 0x10)//abs(int(src[i], 0x10)) if int(src[i], 0x10) != 0 else 0;
                        x =  (abs(int(src[i], 0x10)) & 0xFF);
                        if sign < 0:
                            x = ((~x) + 1) & 0xFF;
                        linker[-1].prefix += x.to_bytes(1);
                    except ValueError:
                        if src[i][0] == '\'':
                            linker[-1].prefix += bytes(src[i][1], 'utf-8')[0:1];
                        elif src[i][0] == '"':
                            src[i] = src[i][1:-1];
                            linker[-1].prefix += bytes(src[i], 'utf-8');
                        else:
                            print(f"Expected integer/string/char for .PREFIX: on line {line}");
                            exit(1);
        i += 1;

    print(segments);
    print(linker);

    ret = b'';
    s: Segment;
    jdx: int;
    for s in segments:
        j: Link;
        jdx = 0;
        for j in linker:
            if j.name == s.name: break;
            jdx += 1;
        if jdx == len(linker):
            print(f"LINK for SEGMENT {s.name} does not exist.");
            exit(1);
        if len(s.code) == 0: continue;
        if len(s.code) > linker[jdx].size and linker[jdx].size >= 0:
            print(f"SEGMENT {s.name} has larger size than its link, reduce amount of code in segment or increase size of link.");
            exit(1);
        print(hex(linker[jdx].size));
        print(hex(len(s.code)));
        print(hex(linker[jdx].size-len(s.code)));
        ret += linker[jdx].prefix + s.code + (b'\x00' * (linker[jdx].size-len(s.code))) + linker[jdx].suffix;

    return ret;

def main(argc: int, argv: list[str]) -> int:
    file: typing.TextIO;
    ofile: io.BufferedWriter;
    file_content: str;
    out: bytes;
    if argc < 3:
        print(f"Usage: {argv[0]} <input file> <output file>")
        return 1;
    file = open(argv[1], "r");
    file_content = file.read();
    file.close();
    out = comp_str(file_content);
    print(f"0000:: ", end="");
    for index, i in enumerate(out):
        print("%02X" % i, end=" ");
        if (index+1) % 0x10 == 0: print(f"\n%04X:: " % (index+1), end="");
    print("\n");
    ofile = open(argv[2], "wb");
    ofile.write(out);
    ofile.close();
    return 0;

if __name__ == "__main__": exit(main(len(sys.argv), sys.argv));
