import fluidsynth

fs = fluidsynth.Synth()
fs.start()
sfid = fs.sfload("/Users/bhuman/soundfonts/GeneralUser.sf2")

# sfid = fs.sfload("/path/to/your/soundfont.sf2")
fs.program_select(0, sfid, 0, 0)
fs.noteon(0, 60, 100)
import time; time.sleep(1)
fs.noteoff(0, 60)
fs.delete()


