# utils/smart_clustering_v2.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN, AgglomerativeClustering
import numpy as np
import re
from collections import defaultdict, Counter

class EnhancedClusteringEngine:
    def __init__(self):
        """Initialize with better sentence transformer and clustering parameters"""
        # Using a more powerful model for better semantic understanding
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.45
        self.min_cluster_size = 2
        
    def advanced_text_preprocessing(self, text):
        """
        Advanced text preprocessing to extract meaningful features
        """
        if not text or "[No text detected]" in text:
            return {
                'cleaned_text': '',
                'entities': [],
                'keywords': [],
                'numbers': [],
                'urls': [],
                'emails': []
            }
        
        text_lower = text.lower()
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract numbers (could be prices, dates, IDs)
        numbers = re.findall(r'\d+\.?\d*', text)
        
        # Extract potential entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Clean text for keywords
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        
        # Enhanced stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'this', 'that', 'these', 'those', 'am', 'been', 'being', 'have',
            'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would',
            'should', 'could', 'ought', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'them', 'their', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 's', 't', 'just', 'now'
        }
        
        words = text_clean.split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Get most common keywords (important terms)
        keyword_freq = Counter(keywords)
        top_keywords = [word for word, _ in keyword_freq.most_common(10)]
        
        return {
            'cleaned_text': ' '.join(keywords),
            'entities': entities,
            'keywords': top_keywords,
            'numbers': numbers,
            'urls': urls,
            'emails': emails,
            'original_text': text
        }
    
    def generate_contextual_embedding(self, processed_text):
        """
        Generate embeddings with context awareness
        Combines original text with extracted features for better clustering
        """
        if not processed_text['cleaned_text']:
            return np.zeros(384)
        
        # Create a rich context string
        context_parts = [processed_text['original_text']]
        
        # Add entities with emphasis
        if processed_text['entities']:
            context_parts.append(' '.join(processed_text['entities']) * 2)
        
        # Add keywords with emphasis
        if processed_text['keywords']:
            context_parts.append(' '.join(processed_text['keywords']) * 2)
        
        context_text = ' '.join(context_parts)
        
        try:
            return self.model.encode(context_text, convert_to_numpy=True)
        except:
            return np.zeros(384)
    
    def calculate_multi_factor_similarity(self, data1, data2):
        """
        Calculate similarity using multiple factors:
        - Semantic similarity (embeddings)
        - Entity overlap
        - Keyword overlap
        - Structural similarity (URLs, emails, numbers)
        """
        # 1. Semantic similarity (40% weight)
        emb1 = data1['embedding'].reshape(1, -1)
        emb2 = data2['embedding'].reshape(1, -1)
        semantic_sim = float(cosine_similarity(emb1, emb2)[0][0])
        
        # 2. Entity similarity (20% weight)
        entities1 = set(data1['processed']['entities'])
        entities2 = set(data2['processed']['entities'])
        entity_sim = self._jaccard_similarity(entities1, entities2)
        
        # 3. Keyword similarity (20% weight)
        keywords1 = set(data1['processed']['keywords'])
        keywords2 = set(data2['processed']['keywords'])
        keyword_sim = self._jaccard_similarity(keywords1, keywords2)
        
        # 4. Structural similarity (20% weight) - URLs, emails
        has_url1 = len(data1['processed']['urls']) > 0
        has_url2 = len(data2['processed']['urls']) > 0
        has_email1 = len(data1['processed']['emails']) > 0
        has_email2 = len(data2['processed']['emails']) > 0
        
        structural_matches = 0
        if has_url1 == has_url2:
            structural_matches += 1
        if has_email1 == has_email2:
            structural_matches += 1
        structural_sim = structural_matches / 2
        
        # Weighted combination
        final_similarity = (
            semantic_sim * 0.4 +
            entity_sim * 0.2 +
            keyword_sim * 0.2 +
            structural_sim * 0.2
        )
        
        return final_similarity
    
    def _jaccard_similarity(self, set1, set2):
        """Calculate Jaccard similarity between two sets"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
    
    def match_to_tags(self, image_text, user_tags):
        """Enhanced tag matching with better scoring"""
        if not image_text or "[No text detected]" in image_text:
            return None, 0.0
        
        processed = self.advanced_text_preprocessing(image_text)
        text_embedding = self.generate_contextual_embedding(processed)
        
        best_match = None
        best_score = 0.0
        
        for tag in user_tags:
            tag_processed = self.advanced_text_preprocessing(tag)
            tag_embedding = self.generate_contextual_embedding(tag_processed)
            
            # 1. Direct mention check (highest priority)
            text_lower = image_text.lower()
            tag_lower = tag.lower()
            
            direct_match = 0.0
            if tag_lower in text_lower:
                direct_match = 1.0
            else:
                # Check partial matches
                tag_words = tag_lower.split()
                match_count = sum(1 for word in tag_words if word in text_lower)
                if len(tag_words) > 0:
                    direct_match = match_count / len(tag_words)
            
            # 2. Semantic similarity
            emb1 = text_embedding.reshape(1, -1)
            emb2 = tag_embedding.reshape(1, -1)
            semantic_sim = float(cosine_similarity(emb1, emb2)[0][0])
            
            # 3. Keyword overlap
            keyword_sim = self._jaccard_similarity(
                set(processed['keywords']),
                set(tag_processed['keywords'])
            )
            
            # Weighted scoring with emphasis on direct matches
            if direct_match > 0.5:
                final_score = direct_match * 0.7 + semantic_sim * 0.2 + keyword_sim * 0.1
            else:
                final_score = semantic_sim * 0.6 + keyword_sim * 0.4
            
            if final_score > best_score:
                best_score = final_score
                best_match = tag
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        return None, best_score
    
    def smart_cluster_unmatched(self, unmatched_data):
        """
        Advanced clustering using DBSCAN and hierarchical clustering
        """
        if not unmatched_data:
            return {}
        
        filenames = list(unmatched_data.keys())
        
        if len(filenames) == 1:
            return {filenames[0]: "Uncategorized"}
        
        # Preprocess all texts and generate embeddings
        processed_data = {}
        valid_filenames = []
        
        for filename, text in unmatched_data.items():
            processed = self.advanced_text_preprocessing(text)
            if processed['cleaned_text']:
                embedding = self.generate_contextual_embedding(processed)
                processed_data[filename] = {
                    'processed': processed,
                    'embedding': embedding
                }
                valid_filenames.append(filename)
            else:
                # No valid text
                processed_data[filename] = None
        
        clusters = {}
        
        # Handle files without text
        for filename in filenames:
            if processed_data.get(filename) is None:
                clusters[filename] = "Uncategorized"
        
        if len(valid_filenames) < 2:
            for filename in valid_filenames:
                clusters[filename] = "Uncategorized"
            return clusters
        
        # Build similarity matrix
        n = len(valid_filenames)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                fn1 = valid_filenames[i]
                fn2 = valid_filenames[j]
                sim = self.calculate_multi_factor_similarity(
                    processed_data[fn1],
                    processed_data[fn2]
                )
                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim
        
        # Convert similarity to distance
        distance_matrix = 1 - similarity_matrix
        
        # Use Agglomerative Clustering for better control
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - self.similarity_threshold,
            metric='precomputed',
            linkage='average'
        )
        
        cluster_labels = clustering.fit_predict(distance_matrix)
        
        # Generate meaningful cluster names
        label_to_filenames = defaultdict(list)
        for filename, label in zip(valid_filenames, cluster_labels):
            label_to_filenames[label].append(filename)
        
        # Assign cluster names
        for label, fnames in label_to_filenames.items():
            if len(fnames) == 1:
                cluster_name = "Uncategorized"
            else:
                # Generate name from common keywords
                cluster_name = self._generate_cluster_name(
                    fnames,
                    processed_data,
                    label
                )
            
            for fname in fnames:
                clusters[fname] = cluster_name
        
        return clusters
    
    def _generate_cluster_name(self, filenames, processed_data, cluster_id):
        """Generate meaningful cluster names based on content"""
        # Collect all keywords from this cluster
        all_keywords = []
        all_entities = []
        
        for fname in filenames:
            if fname in processed_data and processed_data[fname]:
                all_keywords.extend(processed_data[fname]['processed']['keywords'])
                all_entities.extend(processed_data[fname]['processed']['entities'])
        
        # Find most common keywords/entities
        keyword_freq = Counter(all_keywords)
        entity_freq = Counter(all_entities)
        
        # Prefer entities over keywords for naming
        if entity_freq:
            top_entity = entity_freq.most_common(1)[0][0]
            return f"Group: {top_entity}"
        elif keyword_freq:
            top_keywords = [word for word, _ in keyword_freq.most_common(2)]
            return f"Group: {' '.join(top_keywords).title()}"
        else:
            return f"Group {cluster_id + 1}"
    
    def organize_screenshots(self, extracted_data, user_tags):
        """
        Main organization function with improved clustering
        """
        results = {
            'matched': {tag: [] for tag in user_tags},
            'clustered': {},
            'scores': {},
            'unmatched_count': 0
        }
        
        unmatched_data = {}
        
        # Match to tags
        for filename, data in extracted_data.items():
            text = data['text']
            best_tag, score = self.match_to_tags(text, user_tags)
            results['scores'][filename] = score
            
            if best_tag:
                results['matched'][best_tag].append(filename)
            else:
                results['unmatched_count'] += 1
                unmatched_data[filename] = text
        
        # Cluster unmatched
        if unmatched_data:
            clusters = self.smart_cluster_unmatched(unmatched_data)
            for filename, cluster_name in clusters.items():
                if cluster_name not in results['clustered']:
                    results['clustered'][cluster_name] = []
                results['clustered'][cluster_name].append(filename)
        
        return results