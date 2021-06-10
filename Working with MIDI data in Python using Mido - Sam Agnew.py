import time
from pynput.keyboard import Controller
from mido import MidiFile

############# STEP 1 #############

note_to_key = {48: 'z', 50: 'x', 52: 'c', 53: 'v', 55: 'b', 57: 'n', 59: 'm', 60: 'a', 62: 's', 64: 'd', 65: 'f', 67: 'g', 69: 'h', 71: 'j', 72: 'q', 74: 'w', 76: 'e', 77: 'r', 79: 't', 81: 'y', 83: 'u'}
key_signatures = {"C": 0, "D": -2}
tracks_instructions = []
myMidiFile = MidiFile("Johann Pachelbel - Canon in D.mid")

## Iterate through each track in the MIDI file
for current_track_number, current_track in enumerate(myMidiFile.tracks):
    tracks_instructions.insert(current_track_number, [["", 0]])
    ticks = 0
    previous_time = 0

    ## Iterate through each MIDI message in the track we're currently looking at
    for message in current_track:
        ## This MIDI message is about a musical note
        if message.type == "note_on":
            if not message.dict()["velocity"] == 0: # The note is not being shut off

                ## Adjust the octave of the note so that it can be played on the Windsong Lyre
                note = message.dict()["note"]+key_signature
                while note < 48:
                    print("A note has been moved up one octave for being too low:", note)
                    note = note + 12
                while note > 83:
                    print("A note has been moved down one octave for being too high:", note)
                    note = note - 12
                    
                ## This is a new note
                if not message.dict()["time"] == 0:
                    tracks_instructions[current_track_number].append([note_to_key[note], message.dict()["time"]+previous_time+tracks_instructions[current_track_number][len(tracks_instructions[current_track_number]) - 1][1]])
                    previous_time = 0

                ## Add this note to the chord
                else:
                    tracks_instructions[current_track_number][len(tracks_instructions[current_track_number]) - 1][0] = tracks_instructions[current_track_number][len(tracks_instructions[current_track_number]) - 1][0] + note_to_key[note]

            ## We have (additional) information of when to end this note/chord
            else:
                previous_time = previous_time + message.dict()["time"]

        ## This MIDI message is about the key signature
        elif message.type == "key_signature":
            key_signature = key_signatures[message.dict()["key"]]

        ## This MIDI message is about the tempo
        elif message.type == "set_tempo":
            tempo = message.dict()["tempo"]



############# STEP 2 ############# Merge each list of instructions for each track into a single list of instructions
instructions = []

## While there are still instructions remaining in the tracks
while any(tracks_instructions):
    keys = ""
    smallest_tick = float("inf")
    for index, instruction_list in enumerate(tracks_instructions):
        if not instruction_list:
            continue
        if instruction_list[0][1] < smallest_tick:
            smallest_tick = instruction_list[0][1]
            keys = instruction_list[0][0]
            list_of_indices = [index]
        elif instruction_list[0][1] == smallest_tick:
            keys = keys + instruction_list[0][0]
            list_of_indices.append(index)
    for track in list_of_indices:
        tracks_instructions[track].pop(0) # doing inserts or pops from the beginning of a list is slow, try using collections.deque instead which was designed to have fast appends and pops from both ends (https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-queues)
    instructions.append([keys, smallest_tick])

for instruction in range(len(instructions) - 1, 0, -1):
    instructions[instruction][1] = (instructions[instruction][1] - instructions[instruction - 1][1]) * (tempo/1000000 / myMidiFile.ticks_per_beat)



############# STEP 3 #############

print("You have 5 seconds.")
time.sleep(5) # Allow the user 5 seconds to switch to Genshin Impact and take out the Windsong Lyre

# Create a Controller object
keyboard = Controller()

# Press keys
for instruction in instructions:
    time.sleep(instruction[1])
    keyboard.type(instruction[0])
