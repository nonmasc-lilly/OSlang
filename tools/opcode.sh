echo "PROGRAM TO ASSEMBLE:"
read -e input
printf "$input" > tmp.asm
fasm tmp.asm tmp.bin && hexdump -X tmp.bin && rm tmp.asm tmp.bin
