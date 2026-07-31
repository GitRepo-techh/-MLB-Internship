import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.cluster import KMeans


load = load_iris()
x, y = load.data, load.target
inertias = []  # We need this to plot the elbow graph.
for k in range(1, 8):
    model = KMeans(n_clusters=k, random_state=42)
    model.fit(x)
    inertias.append(round(model.inertia_, 2))  # It gives you the sum of squared distances of points to their centroid.
print(inertias)





# graph for the elbow method
plt.plot(range(1, 8), inertias, marker='o')
plt.xlabel('K')
plt.ylabel('Inertia')
plt.show()


# graph for teh scatter plot
plt.scatter(load['petal length (cm)'], load['petal width (cm)'], c=load['cluster'], cmap='viridis')
plt.xlabel('Petal length (cm)')
plt.ylabel('Petal width (cm)')
plt.title('K-Means Clusters (Iris)')
plt.savefig('kmeans_scatter.png')
plt.show()