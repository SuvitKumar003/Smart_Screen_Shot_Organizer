from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

class SmartClusteringEngine:
    def __init__(self):
        """Initialize the smart clustering engine with semantic understanding"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.30  # Lower for semantic matching
        
        # Domain-specific keyword patterns
        self.domain_patterns = {
            'linkedin': {
                'keywords': ['connections', 'experience', 'skills', 'profile', 'endorsed', 
                            'recommendations', 'work', 'education', 'professional', 'career',
                            'network', 'colleague', 'position', 'company', 'industry'],
                'semantic_context': 'professional networking social media profile career job experience'
            },
            'twitter': {
                'keywords': ['tweet', 'retweet', 'like', 'following', 'followers', 'hashtag',
                            'trending', 'timeline', 'mention', 'reply', 'quote'],
                'semantic_context': 'social media microblogging tweets posts updates'
            },
            'instagram': {
                'keywords': ['post', 'story', 'reel', 'followers', 'following', 'likes',
                            'comments', 'share', 'save', 'explore'],
                'semantic_context': 'photo sharing social media images stories'
            },
            'code': {
                'keywords': ['def', 'function', 'class', 'import', 'return', 'if', 'else',
                            'for', 'while', 'print', 'console', 'error', 'debug', 'variable',
                            'const', 'let', 'var', 'public', 'private', 'void'],
                'semantic_context': 'programming code snippet software development script'
            },
            'receipt': {
                'keywords': ['total', 'paid', 'invoice', 'amount', 'price', 'payment',
                            'tax', 'subtotal', 'discount', 'order', 'purchase', 'bill'],
                'semantic_context': 'financial transaction payment receipt invoice bill'
            },
            'email': {
                'keywords': ['from', 'to', 'subject', 'inbox', 'sent', 'draft', 'compose',
                            'reply', 'forward', 'attachment', 'cc', 'bcc'],
                'semantic_context': 'email message correspondence communication'
            },
            'whatsapp': {
                'keywords': ['message', 'chat', 'online', 'typing', 'last seen', 'delivered',
                            'read', 'group', 'broadcast', 'status'],
                'semantic_context': 'messaging instant chat conversation whatsapp'
            },
            'document': {
                'keywords': ['page', 'paragraph', 'heading', 'title', 'content', 'text',
                            'document', 'file', 'pdf', 'word'],
                'semantic_context': 'document text file written content'
            }
        }
        
        # Noise words to remove
        self.noise_words = {
            'screenshot', 'image', 'photo', 'picture', 'capture', 'am', 'pm',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'today', 'yesterday', 'tomorrow', 'now', 'ago', 'min', 'hour', 'day'
        }
    
    def clean_text(self, text):
        """
        Clean and preprocess extracted text to remove noise
        
        Args:
            text: Raw extracted text from OCR
            
        Returns:
            str: Cleaned text
        """
        if not text or text == "[No text detected]":
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove timestamps (HH:MM format)
        text = re.sub(r'\d{1,2}:\d{2}', '', text)
        
        # Remove standalone numbers (but keep numbers in words)
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s#@$]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove noise words
        words = text.split()
        words = [w for w in words if w not in self.noise_words and len(w) > 2]
        
        return ' '.join(words)
    
    def detect_domain(self, text):
        """
        Detect the domain/category of the text using keyword matching
        
        Args:
            text: Cleaned text
            
        Returns:
            tuple: (domain_name, confidence_score) or (None, 0)
        """
        if not text:
            return None, 0
        
        text_lower = text.lower()
        domain_scores = {}
        
        # Calculate keyword match scores
        for domain, patterns in self.domain_patterns.items():
            score = 0
            keywords_found = []
            
            for keyword in patterns['keywords']:
                if keyword in text_lower:
                    score += 1
                    keywords_found.append(keyword)
            
            if score > 0:
                # Normalize score
                domain_scores[domain] = score / len(patterns['keywords'])
        
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            return best_domain, domain_scores[best_domain]
        
        return None, 0
    
    def generate_embedding(self, text):
        """Generate semantic embedding for text"""
        if not text or text == "[No text detected]":
            return np.zeros(384)
        return self.model.encode(text)
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between embeddings"""
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def semantic_match_to_tag(self, text, tag):
        """
        Match text to tag using semantic understanding
        
        Args:
            text: Cleaned text from image
            tag: User-defined tag
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text:
            return 0.0
        
        # Generate embeddings
        text_embedding = self.generate_embedding(text)
        tag_embedding = self.generate_embedding(tag)
        
        # Check if tag matches a known domain
        tag_lower = tag.lower()
        if tag_lower in self.domain_patterns:
            # Use domain context for better matching
            context = self.domain_patterns[tag_lower]['semantic_context']
            context_embedding = self.generate_embedding(context)
            
            # Calculate similarities
            direct_sim = self.calculate_similarity(text_embedding, tag_embedding)
            context_sim = self.calculate_similarity(text_embedding, context_embedding)
            
            # Weighted combination (favor context understanding)
            return 0.4 * direct_sim + 0.6 * context_sim
        else:
            # Direct semantic matching for custom tags
            return self.calculate_similarity(text_embedding, tag_embedding)
    
    def match_to_tags(self, image_text, user_tags):
        """
        Match image to user tags using multi-layer approach
        
        Args:
            image_text: Raw extracted text
            user_tags: List of user-defined tags
            
        Returns:
            tuple: (best_match_tag, confidence_score, method_used)
        """
        # Step 1: Clean text
        cleaned_text = self.clean_text(image_text)
        
        if not cleaned_text:
            return None, 0.0, "no_text"
        
        # Step 2: Try keyword-based domain detection
        detected_domain, keyword_confidence = self.detect_domain(cleaned_text)
        
        # Check if detected domain matches any user tag
        if detected_domain:
            for tag in user_tags:
                if tag.lower() == detected_domain or detected_domain in tag.lower():
                    # High confidence match via keywords
                    return tag, 0.7 + (keyword_confidence * 0.3), "keyword_match"
        
        # Step 3: Semantic matching with all tags
        best_match = None
        best_score = 0.0
        
        for tag in user_tags:
            semantic_score = self.semantic_match_to_tag(cleaned_text, tag)
            
            # Boost score if domain detected and relates to tag
            if detected_domain and (detected_domain in tag.lower() or tag.lower() in detected_domain):
                semantic_score = min(1.0, semantic_score * 1.3)
            
            if semantic_score > best_score:
                best_score = semantic_score
                best_match = tag
        
        # Return match if above threshold
        if best_score >= self.similarity_threshold:
            return best_match, best_score, "semantic_match"
        else:
            return None, best_score, "below_threshold"
    
    def intelligent_cluster_unmatched(self, unmatched_images):
        """
        Cluster unmatched images using domain detection
        
        Args:
            unmatched_images: Dict of {filename: text}
            
        Returns:
            dict: {filename: cluster_name}
        """
        if not unmatched_images:
            return {}
        
        clusters = {}
        domain_clusters = {}
        
        # First, try to group by detected domain
        for filename, text in unmatched_images.items():
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                clusters[filename] = "no_text_detected"
                continue
            
            # Detect domain
            detected_domain, confidence = self.detect_domain(cleaned_text)
            
            if detected_domain and confidence > 0.2:
                cluster_name = f"{detected_domain}_auto"
                if cluster_name not in domain_clusters:
                    domain_clusters[cluster_name] = []
                domain_clusters[cluster_name].append(filename)
            else:
                # Fall back to semantic clustering
                clusters[filename] = None  # Will be clustered later
        
        # Add domain clusters to results
        for cluster_name, filenames in domain_clusters.items():
            for filename in filenames:
                clusters[filename] = cluster_name
        
        # Semantic clustering for remaining images
        remaining = {fn: unmatched_images[fn] for fn in unmatched_images 
                    if fn in clusters and clusters[fn] is None}
        
        if remaining:
            semantic_clusters = self._semantic_cluster(remaining)
            clusters.update(semantic_clusters)
        
        return clusters
    
    def _semantic_cluster(self, images):
        """Semantic clustering for images without domain match"""
        embeddings = []
        filenames = []
        
        for filename, text in images.items():
            cleaned = self.clean_text(text)
            if cleaned:
                embeddings.append(self.generate_embedding(cleaned))
                filenames.append(filename)
        
        if not embeddings:
            return {fn: "misc" for fn in images.keys()}
        
        clusters = {}
        cluster_counter = 1
        embeddings_array = np.array(embeddings)
        
        for i, filename in enumerate(filenames):
            if filename in clusters:
                continue
            
            cluster_name = f"similar_content_{cluster_counter}"
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
        
        for filename in images.keys():
            if filename not in clusters:
                clusters[filename] = "misc"
        
        return clusters
    
    def organize_screenshots(self, extracted_data, user_tags):
        """
        Main function to intelligently organize screenshots
        
        Args:
            extracted_data: Dict of {filename: {'text': str, 'file': file}}
            user_tags: List of user-defined tags
            
        Returns:
            dict: Organization results with metadata
        """
        results = {
            'matched': {tag: [] for tag in user_tags},
            'clustered': {},
            'scores': {},
            'methods': {},
            'cleaned_texts': {}
        }
        
        unmatched = {}
        
        # Match to user tags
        for filename, data in extracted_data.items():
            text = data['text']
            cleaned = self.clean_text(text)
            results['cleaned_texts'][filename] = cleaned
            
            best_tag, score, method = self.match_to_tags(text, user_tags)
            
            results['scores'][filename] = score
            results['methods'][filename] = method
            
            if best_tag:
                results['matched'][best_tag].append(filename)
            else:
                unmatched[filename] = text
        
        # Intelligent clustering for unmatched
        if unmatched:
            clusters = self.intelligent_cluster_unmatched(unmatched)
            
            for filename, cluster_name in clusters.items():
                if cluster_name not in results['clustered']:
                    results['clustered'][cluster_name] = []
                results['clustered'][cluster_name].append(filename)
        
        return results