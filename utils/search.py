# utils/search.py
import numpy as np
from scipy.spatial.distance import cosine
import json
import pandas as pd
from processors.llm import LLMProcessor

class SemanticSearch:
    def __init__(self):
        self.llm_processor = LLMProcessor()
        
    def cosine_similarity(self, vec1, vec2):
        return 1 - cosine(vec1, vec2)
        
    def deserialize_embedding(self, json_string):
        try:
            return np.array(json.loads(json_string))
        except Exception:
            return None
            
    def search_candidates(self, data, queries):
        data['embedded_chunk'] = data['embedded_chunk'].apply(self.deserialize_embedding)
        top_candidates = pd.DataFrame()
        
        for query in queries:
            query_embedding = self.llm_processor.get_embedding(query)
            if query_embedding:
                data['similarity'] = data['embedded_chunk'].apply(
                    lambda x: self.cosine_similarity(json.loads(query_embedding), x) if x is not None else -1
                )
                query_top = data.nlargest(20, "similarity")
                top_candidates = pd.concat([top_candidates, query_top])
        
        unique_candidates = top_candidates.drop_duplicates(subset=["candidate_name"])
        
        # Extract summaries with candidate names
        summaries = []
        for name in unique_candidates['candidate_name'].unique():
            candidate_data = data[data['candidate_name'] == name]
            summary = candidate_data[candidate_data['resume_section_content'].str.contains('Summary for RAG', na=False)]
            if not summary.empty:
                summaries.append(f"Candidate: {name}\n{summary['resume_section_content'].iloc[0]}")
        
        summaries_text = "\n\n---\n\n".join(summaries)
        refined_results = self.llm_processor.rerank_results(summaries_text, queries)
        
        return {
            "candidates": unique_candidates,
            "analysis": refined_results
        }