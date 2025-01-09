mypy src && python src/main.py test.osl test.bin && qemu-system-x86_64 -drive file=test.bin,format=raw
