from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ClusteringEngine:
    def __init__(self):
        """Initialize the sentence transformer model"""
        # Using a lightweight model for speed
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.35  # Adjust this for stricter/looser matching
    
    def generate_embedding(self, text):
        """
        Generate embedding for a given text
        
        Args:
            text: String to embed
            
        Returns:
            numpy array: Embedding vector
        """
        if not text or text == "[No text detected]":
            # Return zero vector for empty text
            return np.zeros(384)  # all-MiniLM-L6-v2 has 384 dimensions
        
        return self.model.encode(text)
    
    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1, embedding2: Numpy arrays
            
        Returns:
            float: Similarity score (0-1)
        """
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def match_to_tags(self, image_text, user_tags):
        """
        Match image text to user-defined tags
        
        Args:
            image_text: Extracted text from image
            user_tags: List of user-defined tag strings
            
        Returns:
            tuple: (best_match_tag, similarity_score) or (None, 0) if no match
        """
        if not image_text or image_text == "[No text detected]":
            return None, 0.0
        
        # Generate embedding for image text
        image_embedding = self.generate_embedding(image_text)
        
        best_match = None
        best_score = 0.0
        
        # Compare with each tag
        for tag in user_tags:
            tag_embedding = self.generate_embedding(tag)
            similarity = self.calculate_similarity(image_embedding, tag_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_match = tag
        
        # Return match only if above threshold
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def cluster_unmatched(self, unmatched_images):
        """
        Cluster images that didn't match any user tag
        
        Args:
            unmatched_images: Dict of {filename: text}
            
        Returns:
            dict: {filename: cluster_id}
        """
        if not unmatched_images:
            return {}
        
        # Generate embeddings for all unmatched images
        embeddings = []
        filenames = []
        
        for filename, text in unmatched_images.items():
            if text and text != "[No text detected]":
                embeddings.append(self.generate_embedding(text))
                filenames.append(filename)
        
        if len(embeddings) == 0:
            return {fn: "misc" for fn in unmatched_images.keys()}
        
        # Simple clustering: group similar images
        clusters = {}
        cluster_counter = 1
        
        embeddings_array = np.array(embeddings)
        
        for i, filename in enumerate(filenames):
            if filename in clusters:
                continue
            
            # Start new cluster
            cluster_name = f"Cluster_{cluster_counter}"
            clusters[filename] = cluster_name
            
            # Find similar images
            for j in range(i + 1, len(filenames)):
                if filenames[j] in clusters:
                    continue
                
                similarity = self.calculate_similarity(
                    embeddings_array[i], 
                    embeddings_array[j]
                )
                
                # If similar enough, add to same cluster
                if similarity >= self.similarity_threshold:
                    clusters[filenames[j]] = cluster_name
            
            cluster_counter += 1
        
        # Handle images with no text
        for filename in unmatched_images.keys():
            if filename not in clusters:
                clusters[filename] = "misc"
        
        return clusters
    
    def organize_screenshots(self, extracted_data, user_tags):
        """
        Main function to organize all screenshots
        
        Args:
            extracted_data: Dict of {filename: {'text': str, 'file': file}}
            user_tags: List of user-defined tags
            
        Returns:
            dict: Organization results with structure:
                {
                    'matched': {tag: [filenames]},
                    'clustered': {cluster_name: [filenames]},
                    'scores': {filename: score}
                }
        """
        results = {
            'matched': {tag: [] for tag in user_tags},
            'clustered': {},
            'scores': {}
        }
        
        unmatched = {}
        
        # First pass: match to user tags
        for filename, data in extracted_data.items():
            text = data['text']
            best_tag, score = self.match_to_tags(text, user_tags)
            
            results['scores'][filename] = score
            
            if best_tag:
                results['matched'][best_tag].append(filename)
            else:
                unmatched[filename] = text
        
        # Second pass: cluster unmatched images
        if unmatched:
            clusters = self.cluster_unmatched(unmatched)
            
            for filename, cluster_name in clusters.items():
                if cluster_name not in results['clustered']:
                    results['clustered'][cluster_name] = []
                results['clustered'][cluster_name].append(filename)
        
        return results