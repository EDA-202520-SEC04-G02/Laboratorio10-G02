from App import view as view
import sys
import csv

default_limit = 1000
sys.setrecursionlimit(default_limit*10)
csv.field_size_limit(2147483647)

# Main function
def main():
    view.main()


# Main function call to run the program
if __name__ == '__main__':
    main()
