import cv2
import fluidsynth
import numpy as np
import os
from midiutil import MIDIFile

file_path=r"C:\Users\Mi\PycharmProjects\MOSH\FlaskWebProject1\static\pic\nuty2.png"

img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)



_, img_thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)

img_height=img.shape[0]
img_width=img.shape[1]

#detecting horizontal lines
horizontal=img_thresh.copy()

kernel_horizontal=np.ones((1,int(10*img_width/1294)))

horizontal=cv2.dilate(horizontal, kernel_horizontal, iterations=1)

horizontal=img_thresh-horizontal+255

#detecting vertical lines
vertical=img_thresh.copy()

kernel_vertical=np.ones((int(10*img_height/160),1))

vertical=cv2.dilate(vertical, kernel_vertical, iterations=1)

vertical=img_thresh-vertical+255

img_only_notes = vertical+horizontal

#close notes
img_only_notes = cv2.erode(img_only_notes, np.ones((int(11*img_width/1294), int(11*img_height/160)), np.uint8))
img_only_notes = cv2.dilate(img_only_notes, np.ones((int(11*img_width/1294), int(11*img_height/160)), np.uint8))

#get contours


conts, hier = cv2.findContours(img_only_notes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
good_conts = []

for cont in conts:
    area = cv2.contourArea(cont)
    if area > 50 * ((img_height * img_width)/(1294*160)) and area < 100000 * ((img_height * img_width)/(1294 * 160)):
        good_conts.append(cont)


output = img.copy()

conts_parameters = []

for cont in good_conts:
    area = cv2.contourArea(cont)
    M = cv2.moments(cont)
    cX = int(M["m10"]/M["m00"])
    cY = int(M["m01"]/M["m00"])
    note_type = 'c'
    conts_parameters.append([cont, note_type, cX, cY])

#sort notes from left to right
for i in range(len(conts_parameters)):
    for j in range(0, len(conts_parameters)-i-1):
        if conts_parameters[j][2]>conts_parameters[j+1][2]:
            temp = conts_parameters[j]
            conts_parameters[j]=conts_parameters[j+1]
            conts_parameters[j+1] = temp

treble_max=conts_parameters[0][0][1][0][1]
treble_min=conts_parameters[0][0][1][0][1]

for i in range(len(conts_parameters[0][0])):
    if (conts_parameters[0][0][i][0][1] >= treble_max):
        treble_max=conts_parameters[0][0][i][0][1]
    if (conts_parameters[0][0][i][0][1] <= treble_min):
        treble_min=conts_parameters[0][0][i][0][1]

treble_height=treble_max-treble_min

k=treble_height/89.0 #skala podbienstwa klucza wiolinowego obrazu, do wzorca

for cont in conts_parameters:
    dY = conts_parameters[0][3]-cont[3]
    if ((dY > k * -31 and dY < k * -29)or(dY > k * 12 and dY< k * 14)):
        note_type ='c'
    elif ((dY > k * -25 and dY < k * -23)or(dY > k * 19 and dY < k * 21)):
        note_type ='d'
    elif ((dY > k * -19 and dY < k * -17)or(dY > k * 25 and dY < k * 27)):
        note_type ='e'
    elif ((dY > k * -13 and dY < k * -11)or(dY > k * 31 and dY < k * 33)):
        note_type ='f'
    elif ((dY > k * -6 and dY < k * -4)or(dY > k * 37 and dY < k * 39)):
        note_type ='g'
    elif ((dY > k * 0 and dY < k * 2)or(dY > k * 43 and dY < k * 45)):
        note_type ='a'
    elif ((dY > k * 6 and dY < k * 8)or(dY > k * 49 and dY < k * 51)):
        note_type ='h'
    cont[1] = note_type



#add note type to output
for i in range(len(conts_parameters)):
    if (i > 1):
        output = cv2.putText(output, conts_parameters[i][1], (conts_parameters[i][2]-10, int(135*img_height/160)), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
notes = []
for i in range(len(conts_parameters)):
    if (i > 1):
        notes.append(conts_parameters[i][1])
        print(conts_parameters[i][1], end=' ')
print(notes)

SlovNote = {'c': 60, 'd': 62, 'e': 64, 'f': 65, 'g': 67, 'a': 69, 'h': 71, 'c1': 72, 'd1': 74, 'e1': 76, 'f1': 77, 'g1': 79, 'a1': 81, 'h1': 83}
finaly = []
for i in notes:
    finaly.append(SlovNote[i])
print(finaly)
degrees  = finaly # MIDI note number
track    = 0
channel  = 0
time     = 0   # In beats
duration = 1   # In beats
tempo    = 60  # In BPM
volume   = 100 # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
                     # automatically created)
MyMIDI.addTempo(track,time, tempo)

for pitch in degrees:
    MyMIDI.addNote(track, channel, pitch, time, duration, volume)
    time = time + 1

with open("C:/Users/Mi/PycharmProjects/MOSH/FlaskWebProject1/static/Midi/CC.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)

def midi_to_wav(midi_file, soundfont_file, wav_file):
    """
    Преобразует MIDI-файл в WAV, используя FluidSynth и SoundFont.

    Args:
        midi_file: Путь к MIDI-файлу (.mid).
        soundfont_file: Путь к SoundFont-файлу (.sf2).
        wav_file: Путь для сохранения WAV-файла (.wav).
    """
    try:
      fs = fluidsynth.Synth()
      fs.start()

      sfid = fs.sfload(soundfont_file)
      fs.program_select(0, sfid, 0, 0)  # Выбираем SoundFont для канала 0

      fs.midi_to_audio(midi_file, wav_file)

      fs.delete()
    except Exception as e:
      print(f"Error converting MIDI to WAV: {e}")


# Пример использования:
midi_file = r'C:\Users\Mi\PycharmProjects\MOSH\FlaskWebProject1\static\Midi\CC.mid'  # Замените на путь к вашему MIDI-файлу
soundfont_file = r'C:\Users\Mi\PycharmProjects\MOSH\FlaskWebProject1\static\pic\198_Prophet_Piano_VS.sf2'  # Замените на путь к вашему SoundFont-файлу
wav_file = 'output.wav'

# Проверка существования файлов
if not os.path.exists(midi_file):
    print(f"MIDI file not found: {midi_file}")
else:
    if not os.path.exists(soundfont_file):
        print(f"SoundFont file not found: {soundfont_file}")
    else:
        midi_to_wav(midi_file, soundfont_file, wav_file)
        print(f"Successfully converted {midi_file} to {wav_file}")
