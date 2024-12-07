import streamlit as st
import google.generativeai as genai
import re
from datetime import datetime
from models import Usage
from utils.database import UsageTracker
from config import Config
import json

class LLMProcessor:
    def __init__(self):
        self.tracker = UsageTracker()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.LLM_MODEL)

    def _parse_chunks(self, text):
        try:
            # Extract candidate name
            name_match = re.search(r"candidate_name:\s*(.+)", text)
            if not name_match:
                return None
            
            # Extract chunks
            chunks = re.findall(r"\d+\s*-\s*(.+?)(?=\n\d+\s*-|$)", text, re.DOTALL)
            if not chunks:
                return None
                
            return {
                "name": name_match.group(1).strip(),
                "chunks": chunks
            }
        except Exception as e:
            st.error(f"Error parsing chunks: {e}")
            return None
        
    def _log_operation(self, user_id: str, operation_type: str, prompt: str, completion: str, model: str):
        usage = Usage(
            user_id=user_id,
            timestamp=datetime.now(),
            operation_type=operation_type,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(completion.split()),
            model=model,
            cost=0.0  # Will be calculated by UsageTracker
        )
        usage.cost = self.tracker.calculate_cost(
            usage.prompt_tokens,
            usage.completion_tokens,
            model
        )
        self.tracker.log_usage(usage)

    def preprocess_resume(self, text: str, user_id: str):
        prompt = f"""
        Condense this resume while preserving all key information about:
        - Work experience, roles, list of all the accomplishments and the duration the person held each role/project
        - Companies/Projects names, sectors, main contributions, tools and technics used at each company or project
        - Skills, tools, technologies, certifications
        - Education, training
        - Projects, publications
        - Dates and total durations
        
        Maintain the document's original sequence of presentation, so the condense resume has a similar flow and no information is missing.

        Here's the resume to condense:
        {text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self._log_operation(
                user_id=user_id,
                operation_type='preprocess',
                prompt=prompt + text,
                completion=result,
                model=Config.LLM_MODEL
            )
            return result
        except Exception as e:
            st.error(f"Error preprocessing resume: {e}")
            return text
            
    def chunk_resume(self, text: str, user_id: str):
        prompt = """
        Segment the provided resume of a candidate into numbered chunks that adhere to the following guidelines:

        Chunking Guidelines:

        -Identify natural breaks in the text, such as topic shifts, paragraph breaks, or sentence ends, similar to how a human would.
        -Ensure each chunk maintains logical coherence with the content before and after it, using full sentences only.
        -Avoid redundant or overlapping content between chunks, ensuring each contains unique information.
        -Preserve any existing formatting, such as lists or subheadings, within each chunk to maintain the document's original structure.
        -Make each role or project realized its own chunk where you see fit so we don't have all of them bunched together in one unique chunk.
        
        Avoid Modifications:

        -Do not modify, summarize, or alter the content of the candidate's resume.
        -If perfectly identical sections of information repeat themselves across the document (e.g., footnotes or headers), output each repeated section only once.
        
        Generate a Summary Chunk:

        After chunking the resume, create a final summary chunk that consolidates the key information for a Retrieval-Augmented Generation (RAG) system. This summary should prioritize details such as:
        -The candidate's core competencies, skills, and expertise with years of experience.
        -Significant achievements, certifications, or projects.
        -Relevant professional experience, including roles, industries, and notable contributions.
        -Educational background and degrees.
        -Ensure the summary chunk is concise, well-structured, and focuses solely on critical details already present in the chunks.
        
        Output Format:
        candidate_name: <Name>
        1 - <Chunk>
        2 - <Chunk>
        ...
        <Number> - Summary for RAG: <Summary>

        Important Notes:

        -Do not include any introduction, conclusion, notes or explanations about your process in your output. 
        -Only provide the ordered chunks and the final summary.

        Here's the candidate resume:
        """
        
        try:
            response = self.model.generate_content(prompt + text)
            result = response.text
            self._log_operation(
                user_id=user_id,
                operation_type='chunk',
                prompt=prompt + text,
                completion=result,
                model=Config.LLM_MODEL
            )
            return self._parse_chunks(result)
        except Exception as e:
            st.error(f"Error chunking resume: {e}")
            return None

    def get_embedding(self, text):
        try:
            result = genai.embed_content(
                model=Config.EMBEDDING_MODEL,
                content=text
            )
            return json.dumps(result['embedding'])  # Now json is defined
        except Exception as e:
            st.error(f"Embedding error: {e}")
            return None
            
    def rerank_results(self, candidates: str, queries: list, user_id: str):
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
        - continue to other criteria provided by the user
        OVERALL: [Ranking and fit assessment]
        
        ---
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self._log_operation(
                user_id=user_id,
                operation_type='rerank',
                prompt=prompt,
                completion=result,
                model=Config.LLM_MODEL
            )
            return result
        except Exception as e:
            st.error(f"Reranking error: {e}")
            return None
