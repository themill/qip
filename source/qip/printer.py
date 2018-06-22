# :coding: utf-8

import colorama


class Printer():
    def __init__(self, level=0):
        self.level = level


    def error(self, text):
        print('' + colorama.Fore.RED + 'Error: ' + text + colorama.Fore.RESET + '\n')

    def warning(self, text):
        print('' + colorama.Fore.YELLOW + 'Warn: ' + text + colorama.Fore.RESET + '\n')

    def status(self, text):
        print('' + colorama.Style.BRIGHT + '[+] ' + text + colorama.Style.RESET_ALL)

    def info(self, text):
        print(colorama.Style.DIM + colorama.Fore.CYAN + text + colorama.Style.RESET_ALL)

    def data(self, text):
        print(colorama.Fore.CYAN + text + colorama.Style.RESET_ALL)

    def debug(self, text):
        if self.level > 0:
            print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + text + colorama.Style.RESET_ALL)
