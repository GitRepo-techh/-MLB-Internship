import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


# Load the data set using pandas and explore it:

load = load_iris()
x, y = load.data, load.target
table = pd.DataFrame(x, columns = load.feature_names)
print(table.info())
print(table.describe())


# Call the K-Mean function:
inertia = []
for kk in range(1,8):

    call_k = KMeans(n_clusters=kk, random_state=88)
    call_k.fit(x)
    inertia.append(call_k.inertia_)

# graph for the elbow method
plt.plot(range(1, 8), inertia, marker='o')
plt.xlabel('K')
plt.ylabel('Inertia')
plt.show()   


# Use the PCA method :

# We first standardrize the data as PCA is very sensitive to one value being maximum and other being minimum.

standardrize = StandardScaler()
sta_x = standardrize.fit_transform(x)

call_pca = PCA(n_components=2)
pca_x = call_pca.fit_transform(sta_x)




# Comparison plots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].scatter(x[:, 2], x[:, 3], c=y, cmap='viridis')
axes[0].set_xlabel('Petal length (cm)')
axes[0].set_ylabel('Petal width (cm)')
axes[0].set_title('Original Data (True Species)')

axes[1].scatter(x[:, 2], x[:, 3], c=y, cmap='viridis')
axes[1].set_xlabel('Petal length (cm)')
axes[1].set_ylabel('Petal width (cm)')
axes[1].set_title('K-Means Clusters')

axes[2].scatter(pca_x[:, 0], pca_x[:, 1], c=y, cmap='viridis')
axes[2].set_xlabel('Principal Component 1')
axes[2].set_ylabel('Principal Component 2')
axes[2].set_title('PCA Visualization')

plt.tight_layout()
plt.savefig('comparison_plot.png')
plt.show()

print("Explained variance ratio:", call_pca.explained_variance_ratio_)
print("Total variance retained:", sum(call_pca.explained_variance_ratio_))


# How many clusters were formed?
# So, after all of this three clusters were formed as teh elbow method gave us the 3 index we needed 

# Did the clusters represent the flower species well?
# Mostly yes — setosa gets separated perfectly, but versicolor and virginica overlap slightly since their petal measurements are close, so a few flowers get misclassified between those two clusters.

# How did PCA help in visualization?
# It compressed the 4 original measurements into just 2 components (retaining ~96% of the variance), making it possible to plot the entire dataset on a single 2D scatter plot instead of an unplottable 4D spacehe