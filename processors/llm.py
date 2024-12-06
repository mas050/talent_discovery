# processors/llm.py
import google.generativeai as genai
from config import Config
import json
import re

class LLMProcessor:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.LLM_MODEL)
        
    def chunk_resume(self, text):
        prompt = """
        Segment the provided resume of a candidate into numbered chunks that adhere to the following guidelines:

        Chunking Guidelines:
        -Identify natural breaks in the text, such as topic shifts, paragraph breaks, or sentence ends
        -Ensure each chunk maintains logical coherence
        -Avoid redundant content between chunks
        -Preserve existing formatting
        
        Generate a Summary Chunk:
        After chunking, create a final summary consolidating:
        -Core competencies and expertise with years
        -Achievements and certifications
        -Professional experience
        -Educational background
        
        Output Format:
        candidate_name: <Name>
        1 - <Chunk>
        2 - <Chunk>
        ...
        <Number> - Summary for RAG: <Summary>
        """
        
        try:
            response = self.model.generate_content(prompt + text)
            text = response.text
            
            name_match = re.search(r"candidate_name:\s*(.+)", text)
            if not name_match:
                return None
                
            chunks = re.findall(r"\d+\s*-\s*(.+?)(?=\n\d+\s*-|$)", text, re.DOTALL)
            return {"name": name_match.group(1).strip(), "chunks": chunks}
        except Exception as e:
            st.error(f"LLM error: {e}")
            return None

    def get_embedding(self, text):
        try:
            result = genai.embed_content(
                model=Config.EMBEDDING_MODEL,
                content=text
            )
            return json.dumps(result['embedding'])
        except Exception as e:
            st.error(f"Embedding error: {e}")
            return None
            
    def rerank_results(self, candidates, queries):
        prompt = f"""
        Analyze multiple candidates based on their resume summaries and the search criteria.
        
        Summaries of candidates:
        {candidates}
        
        Search criteria:
        {', '.join(queries)}
        
        For EACH candidate provide:
        1. Name (extract from summary)
        2. Match analysis for each search criterion
        3. Overall fit ranking
        
        Format:
        CANDIDATE: [Name]
        CRITERIA MATCHES:
        - [Criterion 1]: [Analysis]
        - [Criterion 2]: [Analysis]
        OVERALL: [Ranking and fit assessment]
        
        ---
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Reranking error: {e}")
            return None
