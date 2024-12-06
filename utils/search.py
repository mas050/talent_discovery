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
        high_potential_candidates = pd.DataFrame()
        
        for query in queries:
            query_embedding = self.llm_processor.get_embedding(query)
            if query_embedding:
                data['similarity'] = data['embedded_chunk'].apply(
                    lambda x: self.cosine_similarity(json.loads(query_embedding), x) if x is not None else -1
                )
                top_candidates = data.nlargest(20, "similarity")
                high_potential_candidates = pd.concat([high_potential_candidates, top_candidates])
                
        # Remove duplicates and get refined results
        unique_candidates = high_potential_candidates.drop_duplicates(subset=["candidate_name"])
        summaries = "\n".join(unique_candidates['resume_section_content'])
        refined_results = self.llm_processor.rerank_results(summaries, queries)
        
        return {
            "candidates": unique_candidates,
            "analysis": refined_results
        }
