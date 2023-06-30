import os
import glob
import pandas as pd

from pipeline.truncator import Truncator
from pipeline.refintor import Refintor

from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")

class Pipeline:
    """
    Preprocess data for training.
    """

    def __init__(self, data_folder, num_bars, output_folder, genre):
        self.data_folder = data_folder
        self.num_bars = num_bars
        self.file_path = glob.glob(f'{self.data_folder}/*.mid')
        self.output_folder = output_folder
        self.p_df = pd.read_csv(r'/Users/hai/Desktop/hch/projects/midi/csv/program_change.csv')
        self.genre = genre
    
    def start(self):

        num_bars = self.num_bars
        file_path = self.file_path
        output_folder = self.output_folder
        p_df = self.p_df
        genre = self.genre

        error = 0

        df = pd.DataFrame(columns=['song_midi', 'file_name', 'program_change_value' ,'program_change_msg', 'start_position', 'end_position', 'num_bars', 'tempo', 'key'])
        error_df = pd.DataFrame(columns=['midi_path', 'error_msg'])

        for idx, path in tqdm(enumerate(file_path)):
            
            current_df, df_type_msg = Truncator(path, num_bars, output_folder, p_df).truncate_midi_by_bars()

            if current_df is None:
                error += 1
                continue
            
            if df_type_msg == 'error':
                error_df = pd.concat([error_df, current_df], ignore_index=True)
                continue
            
            checked_df = Refintor(path, current_df, output_folder).check_duplicate()
            df = pd.concat([df, checked_df], ignore_index=True)

            if idx % 100 == 0 and idx != 0:
                print(f'Saved {idx} files', 'Error: ', error)
        
        df.to_csv( genre + '.csv', index=False)
        error_df.to_csv( genre + '_error.csv', index=False)

        return df, error_df
        