from os import listdir
from os.path import isfile, join

serum_user_folder = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\Presets\\User"
serum_program_change_file = (
    "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"
)

serum_presets = [
    f for f in listdir(serum_user_folder) if isfile(join(serum_user_folder, f)) and f.endswith(".fxp")
]

with open(serum_program_change_file, "w") as f:
    [f.write("User\\%s\n" % preset) for preset in serum_presets]

print("%d serum presets wrote to %s" % (len(serum_presets), serum_program_change_file))
