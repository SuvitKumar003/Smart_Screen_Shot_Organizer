# utils/smart_clustering.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from collections import defaultdict

class EnhancedClusteringEngine:
    def __init__(self):
        """Initialize with sentence transformer for semantic similarity"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.45
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        if not text or "[No text detected]" in text:
            return []
        
        text_lower = text.lower()
        # Remove special characters
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        words = text_clean.split()
        
        # Remove common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'
        }
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords
    
    def generate_embedding(self, text):
        """Generate semantic embedding for text"""
        if not text or "[No text detected]" in text:
            return np.zeros(384)
        try:
            return self.model.encode(text, convert_to_numpy=True)
        except:
            return np.zeros(384)
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])
    
    def keyword_overlap_score(self, keywords1, keywords2):
        """Calculate keyword overlap between two keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def tag_specificity_match(self, text, tag):
        """
        Check for specific tag matches in text.
        More specific tags should have higher priority.
        Example: "Google Recruiter" should match before "Recruiter"
        """
        text_lower = text.lower()
        tag_lower = tag.lower()
        
        # Check if tag (or parts of it) are directly in text
        tag_words = tag_lower.split()
        
        # Full tag match
        if tag_lower in text_lower:
            return 1.0
        
        # Check how many tag words are in text
        match_count = sum(1 for word in tag_words if word in text_lower)
        
        if match_count > 0:
            return match_count / len(tag_words)
        
        return 0.0
    
    def match_to_tags(self, image_text, user_tags):
        """
        Match screenshot text to user-defined tags with intelligent scoring.
        Priority: Specificity > Semantic Similarity > Keyword Overlap
        """
        if not image_text or "[No text detected]" in image_text:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        # Get embeddings
        text_embedding = self.generate_embedding(image_text)
        text_keywords = self.extract_keywords(image_text)
        
        for tag in user_tags:
            # 1. SPECIFICITY CHECK - Direct tag mention in text (highest priority)
            specificity_score = self.tag_specificity_match(image_text, tag)
            
            # 2. SEMANTIC SIMILARITY - Using embeddings
            tag_embedding = self.generate_embedding(tag)
            semantic_score = self.calculate_similarity(text_embedding, tag_embedding)
            
            # 3. KEYWORD OVERLAP - Matching important words
            tag_keywords = self.extract_keywords(tag)
            keyword_score = self.keyword_overlap_score(text_keywords, tag_keywords)
            
            # Weighted combination with priority
            # Specificity has highest weight (0.6)
            # Semantic similarity (0.25)
            # Keyword overlap (0.15)
            if specificity_score > 0:
                final_score = (specificity_score * 0.6) + (semantic_score * 0.25) + (keyword_score * 0.15)
            else:
                final_score = (semantic_score * 0.5) + (keyword_score * 0.5)
            
            if final_score > best_score:
                best_score = final_score
                best_match = tag
        
        # Apply threshold
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def smart_cluster_unmatched(self, unmatched_data):
        """
        Intelligently cluster unmatched screenshots based on semantic similarity.
        Groups similar content together automatically.
        """
        if not unmatched_data:
            return {}
        
        filenames = list(unmatched_data.keys())
        texts = list(unmatched_data.values())
        
        if len(filenames) == 1:
            return {filenames[0]: "Uncategorized"}
        
        # Generate embeddings for all unmatched images
        embeddings = []
        valid_indices = []
        
        for idx, text in enumerate(texts):
            if text and "[No text detected]" not in text:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
                valid_indices.append(idx)
        
        clusters = {}
        
        # For images without text, put in "Uncategorized"
        for idx, filename in enumerate(filenames):
            if idx not in valid_indices:
                clusters[filename] = "Uncategorized"
        
        # Cluster images with text using hierarchical approach
        if embeddings:
            embeddings_array = np.array(embeddings)
            assigned = set()
            cluster_counter = 1
            
            for i in range(len(valid_indices)):
                if i in assigned:
                    continue
                
                idx_i = valid_indices[i]
                filename_i = filenames[idx_i]
                cluster_name = f"Group {cluster_counter}"
                
                clusters[filename_i] = cluster_name
                assigned.add(i)
                
                # Find similar images for this cluster
                for j in range(i + 1, len(valid_indices)):
                    if j in assigned:
                        continue
                    
                    similarity = self.calculate_similarity(
                        embeddings_array[i],
                        embeddings_array[j]
                    )
                    
                    if similarity >= self.similarity_threshold:
                        idx_j = valid_indices[j]
                        filename_j = filenames[idx_j]
                        clusters[filename_j] = cluster_name
                        assigned.add(j)
                
                cluster_counter += 1
        
        return clusters
    
    def organize_screenshots(self, extracted_data, user_tags):
        """
        Main organization function:
        1. First, match screenshots to user-defined tags
        2. For unmatched ones, auto-cluster them intelligently
        
        Args:
            extracted_data: Dict of {filename: {'text': str, 'file': file_obj}}
            user_tags: List of user-defined category tags
        
        Returns:
            dict: Results with matched and clustered screenshots
        """
        results = {
            'matched': {tag: [] for tag in user_tags},
            'clustered': {},
            'scores': {},
            'unmatched_count': 0
        }
        
        unmatched_data = {}
        
        # Step 1: Match each screenshot to tags
        for filename, data in extracted_data.items():
            text = data['text']
            
            # Try to match to a user-defined tag
            best_tag, score = self.match_to_tags(text, user_tags)
            results['scores'][filename] = score
            
            if best_tag:
                # Matched! Add to that tag's list
                results['matched'][best_tag].append(filename)
            else:
                # No match found, will be auto-clustered
                results['unmatched_count'] += 1
                unmatched_data[filename] = text
        
        # Step 2: Auto-cluster unmatched screenshots
        if unmatched_data:
            clusters = self.smart_cluster_unmatched(unmatched_data)
            
            for filename, cluster_name in clusters.items():
                if cluster_name not in results['clustered']:
                    results['clustered'][cluster_name] = []
                results['clustered'][cluster_name].append(filename)
        
        return results