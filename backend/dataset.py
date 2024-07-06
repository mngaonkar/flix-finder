import pandas as pd

class Dataset():
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)

    def get_data(self):
        return self.data
    
    def get_columns(self):
        return self.data.columns.tolist()
    
    def get_rows(self):
        return self.data.shape[0]
    
    def print_data(self):
        for index, row in self.data.iterrows():
            print(f"{index}")
            print(f"Title: {row['original_title']} Description: {row['overview']}")

    def search(self, query):
        return self.data[self.data['overview'].str.contains(query)]

    def get_data_by_index(self, index):
        entry = self.data.iloc[index]
        return entry.to_dict()