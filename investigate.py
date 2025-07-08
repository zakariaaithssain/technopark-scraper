import pandas as pd 

data = pd.read_json(path_or_buf="data/technopark_startups.json", encoding= "utf-8", orient= 'records')

print(data.info())
print(data.describe())
