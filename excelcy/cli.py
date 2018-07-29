import sys

from excelcy import ExcelCy


def main(argv: list = None):
    # quick CLI execution
    args = argv or sys.argv
    if args[1] == 'execute':
        excelcy = ExcelCy.execute(file_path=args[2])


if __name__ == '__main__':
    main()
