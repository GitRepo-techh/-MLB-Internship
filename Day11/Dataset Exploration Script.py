from sklearn.datasets import load_iris
import pandas as pd



call = load_iris()  # loads the data

tabular = pd.DataFrame( call.data, columns = call.feature_names)   # transforms into a readable tabular form structure instead of a numpy array
tabular['species'] = call.target  # calls the labels of the species available.

# visualize and describe the data.
print(tabular.head())
print(tabular.describe())
print(tabular.info())
print(tabular["species"].value_counts())


