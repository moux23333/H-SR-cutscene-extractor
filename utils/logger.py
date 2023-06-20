import colorama
import datetime


class log_init():
    def info(self, msg):
        print(f"{colorama.Fore.BLUE}[LOG][{datetime.datetime.now()}]{colorama.Style.RESET_ALL} {msg}")

    def err(self, err):
        return f"{colorama.Fore.RED}[ERROR][{datetime.datetime.now()}]{colorama.Style.RESET_ALL} {err}"
