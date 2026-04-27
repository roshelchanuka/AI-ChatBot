from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_learned_responses

class MLLearner:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.learned_pairs = []
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        """Reloads learned responses from the database and retrains the model."""
        try:
            self.learned_pairs = get_learned_responses()
        except Exception as e:
            print(f"ML Learner: Database not ready yet ({e})")
            self.learned_pairs = []

        if self.learned_pairs:
            corpus = [pair[0] for pair in self.learned_pairs]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.tfidf_matrix = None

    def find_match(self, user_input, threshold=0.75):
        """Finds the best matching learned response using cosine similarity."""
        if not self.learned_pairs or self.tfidf_matrix is None:
            return None

        # Vectorize user input
        user_vec = self.vectorizer.transform([user_input])
        
        # Calculate similarity
        similarities = cosine_similarity(user_vec, self.tfidf_matrix)
        
        # Find index of best match
        best_match_idx = similarities.argmax()
        max_similarity = similarities[0, best_match_idx]

        if max_similarity >= threshold:
            return self.learned_pairs[best_match_idx][1]
        
        return None

# Singleton instance
learner = MLLearner()

def get_learned_match(user_input):
    return learner.find_match(user_input)

def retrain_learner():
    learner.load_data()
