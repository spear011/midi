import mido
import os
import numpy as np
from utils.utils import get_file_name

class Refintor:
    """
    Compare MIDI files.
    """

    def __init__(self, path, df, output_folder):
        self.path = path
        self.df = df
        self.output_folder = output_folder

    def manhattan_distance(self, list1, list2):
        distance = 0
        for sub1, sub2 in zip(list1, list2):
            sub_distance = 0
            for x, y in zip(sub1, sub2):
                sub_distance += abs(x - y)
            distance += sub_distance
        return distance

    def compare_midi_files(self, file1, file2):
        # Load midi files
        try:
            mid1 = mido.MidiFile(file1)
            mid2 = mido.MidiFile(file2)
        except:
            return 'read_error'

        # Extract notes from midi files and group adjacent pitches together
        notes1 = []
        for msg in mido.merge_tracks(mid1.tracks):
            if 'note_on' in msg.type:
                pitch = msg.note
                if notes1 and pitch == notes1[-1][-1] + 1:
                    # Append pitch to last group
                    notes1[-1].append(pitch)
                else:
                    # Create new group for pitch
                    notes1.append([pitch])

        notes2 = []
        for msg in mido.merge_tracks(mid2.tracks):
            if 'note_on' in msg.type:
                pitch = msg.note
                if notes2 and pitch == notes2[-1][-1] + 1:
                    # Append pitch to last group
                    notes2[-1].append(pitch)
                else:
                    # Create new group for pitch
                    notes2.append([pitch])

        # Calculate similarity for each group of pitches
        return self.manhattan_distance(notes1, notes2)

    def check_duplicate(self):

        df = self.df
        output_folder = self.output_folder

        song_file_name = get_file_name(self.path)

        current_instr = None
        comparing_instr = None
        current_file = None
        duplicated = {}
        duplicate_detected = []

        midi_folder = os.path.join(output_folder, song_file_name)
        midi_files = df['file_name']
        midi_files_path = [os.path.join(midi_folder, file) for file in midi_files]

        df['repeated'] = np.nan

        for i in range(len(df)):
            current_instr = df.loc[i, 'instrument_name']
            current_file = df.loc[i, 'file_name']

            if current_file in duplicate_detected:
                continue

            for j in range(len(df)):
                comparing_instr = df.loc[j, 'instrument_name']

                if current_instr == comparing_instr:
                    if i == j:
                        continue
                    else:
                        similarity = self.compare_midi_files(midi_files_path[i], midi_files_path[j])
                        if similarity == 0:
                            duplicated[df['file_name'][i]] = df['file_name'][j]
                            duplicate_detected.append(df['file_name'][j])
                            df.loc[i, 'repeated'] = df['file_name'][j]
                            
                        elif similarity == 'read_error':
                            df.loc[i, 'repeated'] = 'read_error'

                elif current_instr != comparing_instr:
                    continue

        # for i in range(len(df)):
        #     if df.loc[i, 'repeated'] is not None:
        #         repeated_file = df.loc[i, 'repeated']
        #         target_file = df.loc[i, 'file_name']
        #         target_idx = df[df['file_name'] == repeated_file].index
        #         df.loc[target_idx, 'file_name'] = target_file

        return df