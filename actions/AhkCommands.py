import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")


class AhkCommands(object):
    @classmethod
    def select_first_vst(cls):
        shell.SendKeys("%{F1}", 0)

    @classmethod
    def show_and_activate_rev2_editor(cls):
        shell.SendKeys("%{F3}", 0)
