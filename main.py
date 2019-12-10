import extract
from dataset import DataSet

data_path = 'data'
segments_path = 'data/segments'

# extract.extract_all(data_path)
dataset = DataSet(segments_path=segments_path)
