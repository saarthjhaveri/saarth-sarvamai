from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SmartQueryRouter:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.category_examples = {
            "meta_query": [
                # Basic identity questions
                "what can you do",
                "who are you",
                "tell me about yourself",
                "what are your capabilities",
                
                # Detailed capability questions
                "what are your features",
                "what are your limitations",
                "what kind of tasks can you handle",
                "how can you assist me",
                "what is your purpose",
                
                # Technical/Background questions
                "how do you work",
                "are you an AI",
                "what model are you based on",
                "who created you",
                "what version are you",
                
                # Specific capability questions
                "can you process images",
                "do you understand code",
                "can you remember our conversation",
                "do you have memory",
                "how smart are you"
            ],
            
            "system_query": [
                # File operations
                "upload a pdf",
                "how do I upload files",
                "can I upload multiple documents",
                "how to import a pdf",
                "load a document",
                
                # System controls
                "switch chat mode",
                "change the mode",
                "how do I change settings",
                "modify system preferences",
                
                # History/Memory management
                "clear the conversation",
                "delete chat history",
                "start a new chat",
                "reset our conversation",
                "clear memory",
                
                # Usage help
                "how do I use this system",
                "show me how to use this",
                "what are the available commands",
                "guide me through the features",
                "how does this work",
                
                # Technical system queries
                "what file formats are supported",
                "is there a file size limit",
                "how to export conversation",
                "where are files stored",
                "system requirements"
            ],
            
            "document_query": [
                # Basic document questions
                "what does the document say about",
                "find information about",
                "search for",
                "look up",
                
                # Analysis requests
                "summarize the section on",
                "give me a summary of",
                "analyze the part about",
                "explain the section on",
                
                # Specific content queries
                "what is mentioned about",
                "find references to",
                "show me where it talks about",
                "locate information regarding",
                
                # Comparison queries
                "compare what the document says about",
                "what are the differences between",
                "how does the document relate",
                "find connections between",
                
                # Detail-oriented queries
                "what are the specific details about",
                "give me the exact information on",
                "what does it specifically say about",
                "find detailed information about",
                
                # Context queries
                "in what context is",
                "how is this topic discussed",
                "what's the background on",
                "provide context for"
            ],
            
            "conversation": [
                # Greetings
                "hello",
                "hi there",
                "hey",
                "good morning",
                "good afternoon",
                "good evening",
                
                # Gratitude
                "thank you",
                "thanks a lot",
                "appreciate your help",
                "that was helpful",
                "you've been very helpful",
                
                # Farewells
                "goodbye",
                "bye",
                "see you later",
                "have a good day",
                "until next time",
                
                # Acknowledgments
                "I understand",
                "got it",
                "makes sense",
                "okay",
                "alright",
                
                # Politeness
                "please",
                "if you could",
                "would you mind",
                "sorry to bother",
                "excuse me",
                
                # Feedback
                "that's great",
                "perfect",
                "excellent",
                "well done",
                "that works"
            ]
        }
        
        # Pre-compute embeddings for examples
        self.category_embeddings = {}
        for category, examples in self.category_examples.items():
            self.category_embeddings[category] = self.model.encode(examples)
        
        # Define confidence thresholds
        self.high_confidence = 0.85
        self.medium_confidence = 0.70
        self.low_confidence = 0.50

    async def classify_query(self, query: str):
        query_embedding = self.model.encode([query])[0]
        similarities = {}
        
        for category, embeddings in self.category_embeddings.items():
            similarity = cosine_similarity([query_embedding], embeddings).max()
            similarities[category] = similarity
        
        best_category = max(similarities.items(), key=lambda x: x[1])
        confidence = float(best_category[1])
        
        
        # Simplified return type to match main.py and streamlit expectations
        return {
            "category": best_category[0],
            "confidence": float(confidence),  # Ensure it's a float for JSON serialization
            "requires_context": best_category[0] in ["document_query"]
        }