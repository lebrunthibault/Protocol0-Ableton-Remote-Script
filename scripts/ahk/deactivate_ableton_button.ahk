#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

activated_button_color := "0x32B5FF"
deactivated_button_color := "0x2D2D2D"

x := A_Args[1]
y := A_Args[2]
activate := A_Args[3]

PixelGetColor, color, x, y

if (not activate and color = activated_button_color) {
    MouseClick, left, x, y
} else if (activate and color = deactivated_button_color) {
    MouseClick, left, x, y
}