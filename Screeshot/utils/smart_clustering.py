from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from collections import Counter

class EnhancedClusteringEngine:
    def __init__(self):
        """Initialize with better models for screenshot clustering"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.35
        
        # Keywords for different screenshot types
        self.screenshot_patterns = {
            'social_media': ['linkedin', 'twitter', 'facebook', 'instagram', 'profile', 'post', 'message'],
            'recruitment': ['recruiter', 'job', 'opportunity', 'position', 'hiring', 'interview', 'application'],
            'code': ['github', 'code', 'function', 'class', 'def', 'import', 'console', 'terminal'],
            'receipts': ['receipt', 'invoice', 'payment', 'total', 'paid', 'amount', 'order', 'transaction'],
            'memes': ['meme', 'funny', 'lol', 'joke'],
            'emails': ['from:', 'to:', 'subject:', 'dear', 'regards', 'inbox', 'sent'],
            'meetings': ['zoom', 'meet', 'teams', 'meeting', 'calendar', 'schedule'],
            'design': ['figma', 'design', 'prototype', 'mockup', 'ui', 'ux']
        }
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        if not text or text == "[No text detected]":
            return []
        
        # Convert to lowercase
        text_lower = text.lower()
        
        # Remove special characters but keep spaces
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        
        # Split into words
        words = text_clean.split()
        
        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
    
    def detect_screenshot_type(self, text):
        """
        Detect what type of screenshot this is based on keywords
        Returns: (type, confidence)
        """
        if not text or text == "[No text detected]":
            return None, 0.0
        
        text_lower = text.lower()
        scores = {}
        
        for screenshot_type, patterns in self.screenshot_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize by number of patterns
                scores[screenshot_type] = score / len(patterns)
        
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type, scores[best_type]
        
        return None, 0.0
    
    def focused_text_extraction(self, text, target_keywords):
        """
        Extract only relevant portions of text that match target keywords
        This helps in better clustering for specific tags like "LinkedIn recruiter"
        """
        if not text or text == "[No text detected]":
            return ""
        
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if any target keyword is in this sentence
            for keyword in target_keywords:
                if keyword.lower() in sentence_lower:
                    relevant_sentences.append(sentence.strip())
                    break
        
        return '. '.join(relevant_sentences) if relevant_sentences else text
    
    def enhanced_similarity(self, text1, text2, tag=None):
        """
        Enhanced similarity calculation with keyword matching
        """
        # Get embeddings
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)
        
        # Cosine similarity
        semantic_sim = self.calculate_similarity(emb1, emb2)
        
        # Keyword overlap bonus
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if keywords1 and keywords2:
            keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
        else:
            keyword_overlap = 0
        
        # If tag provided, check for tag keywords in text
        tag_boost = 0
        if tag:
            tag_keywords = self.extract_keywords(tag)
            text_keywords = self.extract_keywords(text1)
            
            for tk in tag_keywords:
                if tk in text_keywords:
                    tag_boost += 0.1
            
            tag_boost = min(tag_boost, 0.3)  # Cap the boost
        
        # Weighted combination
        final_score = (semantic_sim * 0.6) + (keyword_overlap * 0.3) + tag_boost
        
        return min(final_score, 1.0)
    
    def generate_embedding(self, text):
        """Generate embedding for text"""
        if not text or text == "[No text detected]":
            return np.zeros(384)
        return self.model.encode(text)
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity"""
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])
    
    def match_to_tags(self, image_text, user_tags):
        """
        Enhanced matching with focused text extraction
        """
        if not image_text or image_text == "[No text detected]":
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        for tag in user_tags:
            # Extract keywords from tag
            tag_keywords = self.extract_keywords(tag)
            
            # Focus on relevant text portions
            focused_text = self.focused_text_extraction(image_text, tag_keywords)
            
            # Calculate enhanced similarity
            similarity = self.enhanced_similarity(
                focused_text if focused_text else image_text,
                tag,
                tag
            )
            
            if similarity > best_score:
                best_score = similarity
                best_match = tag
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        else:
            return None, best_score
    
    def smart_cluster_unmatched(self, unmatched_images):
        """
        Intelligent clustering based on screenshot types and content
        """
        if not unmatched_images:
            return {}
        
        # First, detect types
        typed_images = {}
        for filename, text in unmatched_images.items():
            screenshot_type, confidence = self.detect_screenshot_type(text)
            if screenshot_type and confidence > 0.2:
                if screenshot_type not in typed_images:
                    typed_images[screenshot_type] = []
                typed_images[screenshot_type].append(filename)
        
        # Group by detected types
        clusters = {}
        for screenshot_type, filenames in typed_images.items():
            cluster_name = screenshot_type.replace('_', ' ').title()
            for fn in filenames:
                clusters[fn] = cluster_name
        
        # For remaining untyped images, use similarity clustering
        untyped = {fn: text for fn, text in unmatched_images.items() if fn not in clusters}
        
        if untyped:
            embeddings = []
            filenames = []
            
            for filename, text in untyped.items():
                if text and text != "[No text detected]":
                    embeddings.append(self.generate_embedding(text))
                    filenames.append(filename)
            
            if embeddings:
                embeddings_array = np.array(embeddings)
                cluster_counter = 1
                
                for i, filename in enumerate(filenames):
                    if filename in clusters:
                        continue
                    
                    cluster_name = f"Group_{cluster_counter}"
                    clusters[filename] = cluster_name
                    
                    for j in range(i + 1, len(filenames)):
                        if filenames[j] in clusters:
                            continue
                        
                        similarity = self.calculate_similarity(
                            embeddings_array[i],
                            embeddings_array[j]
                        )
                        
                        if similarity >= self.similarity_threshold:
                            clusters[filenames[j]] = cluster_name
                    
                    cluster_counter += 1
        
        # Handle images with no text
        for filename in unmatched_images.keys():
            if filename not in clusters:
                clusters[filename] = "Uncategorized"
        
        return clusters
    
    def organize_screenshots(self, extracted_data, user_tags):
        """
        Enhanced organization with better matching
        """
        results = {
            'matched': {tag: [] for tag in user_tags},
            'clustered': {},
            'scores': {},
            'types': {}  # Store detected types
        }
        
        unmatched = {}
        
        # Match to user tags
        for filename, data in extracted_data.items():
            text = data['text']
            
            # Detect screenshot type
            screenshot_type, type_confidence = self.detect_screenshot_type(text)
            results['types'][filename] = screenshot_type or "unknown"
            
            # Match to tags
            best_tag, score = self.match_to_tags(text, user_tags)
            results['scores'][filename] = score
            
            if best_tag:
                results['matched'][best_tag].append(filename)
            else:
                unmatched[filename] = text
        
        # Cluster unmatched with smart logic
        if unmatched:
            clusters = self.smart_cluster_unmatched(unmatched)
            
            for filename, cluster_name in clusters.items():
                if cluster_name not in results['clustered']:
                    results['clustered'][cluster_name] = []
                results['clustered'][cluster_name].append(filename)
        
        return results