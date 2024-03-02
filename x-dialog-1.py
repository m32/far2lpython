#!/usr/bin/env vpython3
from far2l.fardialogbuilder import (
    Spacer,
    TEXT, EDIT, PASSWORD, MASKED, MEMOEDIT,
    BUTTON, CHECKBOX, RADIOBUTTON, COMBOBOX,
    LISTBOX, USERCONTROL,
    HLine,
    HSizer, VSizer,
    DialogBuilder
)

def main():
    def DialogProc(*args):
        pass
    b = DialogBuilder(
        None,
        DialogProc,
        "ADB Config",
        "adb config",
        0,
        VSizer(
            HSizer(
                VSizer(
                    TEXT(None, "Shell:"),
                    RADIOBUTTON('default', "default"),
                    RADIOBUTTON('busybox', "busybox"),
                    RADIOBUTTON('toybox', "toybox"),
                    RADIOBUTTON('toolbox', "toolbox"),
                ),
                Spacer(),
                HSizer(
                    CHECKBOX('rexec', "Allow remote execute"),
                ),
            ),
            HLine(),
            HSizer(
                BUTTON('OK', "OK", default=True),
                BUTTON('CANCEL', "Cancel"),
            ),
        ),
    )
    dlg = b.build(-1, -1)
main()
