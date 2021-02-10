import sys
import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")

if __name__ == "__main__":
    shell.SendKeys(sys.argv[1], 0)
