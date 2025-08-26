# backend/cluster.py
from sklearn.cluster import KMeans
import umap
import numpy as np

def cluster_embeddings(embeddings, n_clusters=8):
    if len(embeddings) == 0:
        return []
    kmeans = KMeans(n_clusters=min(n_clusters, len(embeddings)), random_state=42)
    labels = kmeans.fit_predict(embeddings)
    return labels

def reduce_embeddings(embeddings, n_components=2):
    if len(embeddings)==0:
        return np.zeros((0, n_components))
    reducer = umap.UMAP(n_components=n_components, random_state=42)
    return reducer.fit_transform(embeddings)
