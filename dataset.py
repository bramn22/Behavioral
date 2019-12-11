import os
import pandas as pd
import numpy as np


class DataSet:
    def __init__(self, cfg, create_csv=False):
        self.cfg = cfg
        csv_path = self.cfg['user']+'.csv'
        if not create_csv:
            self.df = pd.read_csv(csv_path, index_col=0)
        else:
            experiment_dirs = os.listdir(self.cfg['segments_path'])

            data = []
            for experiment in experiment_dirs:
                experiment_path = os.path.join(self.cfg['segments_path'], experiment)
                segments_dirs = os.listdir(experiment_path)

                for dir in segments_dirs:
                    segments_dir = os.path.join(experiment_path, dir)
                    segments = os.listdir(segments_dir)
                    data += [[segments_dir, os.path.splitext(segment)[0]] for segment in segments]

            self.df = pd.DataFrame(data, columns=['Path', 'Onset'])
            self.save_to_csv()

    def add_segments(self, segments_path):
        experiment_dirs = os.listdir(segments_path)

        data = []
        for experiment in experiment_dirs:
            experiment_path = os.path.join(segments_path, experiment)
            segments_dirs = os.listdir(experiment_path)
            for dir in segments_dirs:
                segments_dir = os.path.join(experiment_path, dir)
                # Check if this segments_dir is already included in the csv
                if self.df.loc[self.df['Path']==segments_dir].empty:
                    segments = os.listdir(segments_dir)
                    data += [[segments_dir, os.path.splitext(segment)[0]] for segment in segments]
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
        self.df.to_csv(self.cfg['user']+'.csv', mode='w')
