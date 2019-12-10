import os
import pandas as pd
import numpy as np


class DataSet:
    def __init__(self, segments_path=None, csv_path=None):
        if csv_path:
            self.df = pd.read_csv(csv_path, index_col=0)
        elif segments_path:
            segments_dirs = os.listdir(segments_path)
            data = []
            for dir in segments_dirs:
                segments_dir = os.path.join(segments_path, dir)
                segments = os.listdir(segments_dir)
                data += [[segments_dir, os.path.splitext(segment)[0]] for segment in segments]
                # segment_paths = list(map(lambda s: os.path.join(segments_path, s), segments))
                # Set path to the specific directory, Onset to the video name
                # data = [['v1', 10], ['v2', 15], ['v3', 14]]

            self.df = pd.DataFrame(data, columns=['Path', 'Onset'])
            self.save_to_csv()

    def add_segments(self, segments_path):
        segments_dirs = os.listdir(segments_path)
        data = []
        for dir in segments_dirs:
            segments_dir = os.path.join(segments_path, dir)
            segments = os.listdir(segments_dir)
            data += [[segments_dir, os.path.splitext(segment)[0]] for segment in segments]
            # segment_paths = list(map(lambda s: os.path.join(segments_path, s), segments))
            # Set path to the specific directory, Onset to the video name
            # data = [['v1', 10], ['v2', 15], ['v3', 14]]
        df_added = pd.DataFrame(data, columns=['Path', 'Onset'])
        self.df = self.df.append(df_added, ignore_index=True, verify_integrity=True, sort=False)
        self.save_to_csv()

    def get_next_unclassified(self, user):
        if user not in self.df:
            self.add_user(user)
        unclassified = self.df.loc[self.df[user].isnull()]
        return unclassified.sample()

    def add_record(self, user, record_id, classification):
        if user not in self.df:
            self.add_user(user)
        self.df.loc[record_id, user] = classification
        self.save_to_csv()

    def add_user(self, user):
        if user not in self.df:
            self.df[user] = np.nan
            self.save_to_csv()

    def save_to_csv(self):
        self.df.to_csv('classifications.csv', mode='w')

# ds = DataSet('data/segments')
# ds = DataSet(csv_path='classifications.csv')
# ds.add_user('tony')
# ds.add_record('tony', 2, 'valid')
# ds.add_record('lisa', 2, 'invalid')
# print(ds.df)
# ds.save_to_csv()
