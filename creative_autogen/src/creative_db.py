"""Simple wrapper around Pinecone (placeholder)."""
import os
try:
    import pinecone
except Exception:  # if pinecone is not installed
    pinecone = None


class CreativeDB:
    def __init__(self, index_name='creative-index'):
        self.index_name = index_name
        self._index = None
        if pinecone and os.getenv('PINECONE_API_KEY'):
            pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment='us-west1-gcp')
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(index_name, dimension=1536)
            self._index = pinecone.Index(index_name)

    def upsert(self, vectors):
        if self._index:
            self._index.upsert(vectors)

    def query(self, vector, top_k=5):
        if self._index:
            return self._index.query(vector, top_k=top_k)
        return []
