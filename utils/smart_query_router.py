from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer, util
from datasets import load_dataset
import torch
import asyncio
import os

class SmartQueryRouter:
    def __init__(self):
        # Initialize models
        self.tokenizer = AutoTokenizer.from_pretrained("typeform/distilbert-base-uncased-mnli")
        self.intent_model = AutoModelForSequenceClassification.from_pretrained(
            "typeform/distilbert-base-uncased-mnli"
        )
        self.semantic_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        # Initialize zero-shot classifier
        self.zero_shot = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Load reference datasets (lazy loading)
        self._load_datasets()
        
        # Define classification categories
        self.categories = [
            "conversation",      # general chat
            "document_query",    # PDF-related questions
            "system_query",      # system-related questions
            "meta_query"         # questions about the bot
        ]

    def _load_datasets(self):
        # Load small subsets of datasets for efficiency
        try:
            self.conv_examples = load_dataset("daily_dialog", split="train[:1000]", trust_remote_code=True)
            self.qa_examples = load_dataset("squad", split="train[:1000]")
        except Exception as e:
            print(f"Warning: Could not load all datasets: {e}")
            self.conv_examples = []
            self.qa_examples = []

    async def classify_query(self, query: str):
        # Zero-shot classification
        zero_shot_result = self.zero_shot(
            query,
            candidate_labels=self.categories,
            hypothesis_template="This is {}."
        )

        # Get semantic similarity scores
        semantic_score = await self._get_semantic_score(query)
        
        # Combine scores
        final_category = zero_shot_result['labels'][0]
        confidence = max(zero_shot_result['scores'][0], semantic_score)

        return {
            "category": final_category,
            "confidence": confidence,
            "requires_context": final_category == "document_query"
        }

    async def _get_semantic_score(self, query: str):
        query_embedding = self.semantic_model.encode(query)
        
        if self.conv_examples and self.qa_examples:
            # Compare with conversation examples
            conv_similarities = []
            for conv in self.conv_examples["dialog"][:100]:
                conv_embedding = self.semantic_model.encode(conv)
                similarity = util.pytorch_cos_sim(query_embedding, conv_embedding)
                conv_similarities.append(similarity.item())
            
            return max(conv_similarities) if conv_similarities else 0.0
        return 0.5  # Default fallback score