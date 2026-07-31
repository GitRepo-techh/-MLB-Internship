from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris




iris = load_iris()

x, y = iris.data, iris.target

standardrize = StandardScaler()
sta_x = standardrize.fit_transform(x)

for_pca = PCA(n_components=2)

pca_x = for_pca.fit_transform(sta_x)




plt.scatter(pca_x[:, 0], pca_x[:, 1], c=y, cmap='viridis')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA Visualization (Iris)')
plt.savefig('pca_scatter.png')
plt.show()






# Fit K-Means (K=3, based on elbow method)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(x)

# Comparison plot: original vs K-Means vs PCA
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].scatter(x[:, 2], x[:, 3], c=y, cmap='viridis')
axes[0].set_xlabel('Petal length (cm)')
axes[0].set_ylabel('Petal width (cm)')
axes[0].set_title('Original Data (True Species)')

axes[1].scatter(x[:, 2], x[:, 3], c=clusters, cmap='viridis')
axes[1].set_xlabel('Petal length (cm)')
axes[1].set_ylabel('Petal width (cm)')
axes[1].set_title('K-Means Clusters')

axes[2].scatter(pca_x[:, 0], pca_x[:, 1], c=clusters, cmap='viridis')
axes[2].set_xlabel('Principal Component 1')
axes[2].set_ylabel('Principal Component 2')
axes[2].set_title('PCA Visualization')

plt.tight_layout()
plt.savefig('comparison_plot.png')
plt.show()

print("Explained variance ratio:", for_pca.explained_variance_ratio_)
print("Total variance retained:", sum(for_pca.explained_variance_ratio_))