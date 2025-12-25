import os
import sys
import re
import json
import fitz
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Try to import Groq, fall back to Google if not available
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize models (lazy loading)
_embed_model = None
_llm = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model

def get_llm():
    global _llm
    if _llm is None:
        # Try Groq first (free tier)
        groq_key = os.getenv("GROQ_API_KEY", "")
        google_key = os.getenv("GOOGLE_API_KEY", "")
        
        if GROQ_AVAILABLE and groq_key:
            print("ResumeAnalyzer: Using Groq API (llama-3.3-70b-versatile)")
            _llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0,
                api_key=groq_key
            )
        elif GOOGLE_AVAILABLE and google_key:
            print("ResumeAnalyzer: Using Google Gemini API")
            _llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        else:
            print("ResumeAnalyzer: No LLM API configured! Set GROQ_API_KEY or GOOGLE_API_KEY")
            _llm = None
    return _llm

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume against job description using Groq or Google Gemini.
    Returns structured JSON with score, summary, and gaps.
    """
    llm = get_llm()
    
    if llm is None:
        return {
            "score": 0,
            "summary": "AI analysis unavailable. Please configure GROQ_API_KEY or GOOGLE_API_KEY.",
            "gaps": ["No API configured"]
        }
    
    prompt = f"""
    Analyze the following Resume against the Job Description.
    
    JOB DESCRIPTION:
    {job_description}
    
    RESUME:
    {resume_text[:10000]}
    
    Provide your analysis in the following JSON format ONLY (no additional text):
    {{
        "score": <number between 0-100>,
        "summary": "<2-3 sentence summary of candidate's fit>",
        "gaps": ["<gap 1>", "<gap 2>", "<gap 3>"]
    }}
    
    Be strict and objective in scoring. Only list the top 3 most critical skill/experience gaps.
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Try to extract JSON from the response
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        result = json.loads(content)
        
        # Validate and normalize
        return {
            "score": int(result.get("score", 0)),
            "summary": str(result.get("summary", "Analysis not available")),
            "gaps": result.get("gaps", [])[:3]  # Limit to 3 gaps
        }
    except json.JSONDecodeError:
        # Fallback: try to extract info manually
        return {
            "score": 50,
            "summary": "Unable to parse AI response. Please try again.",
            "gaps": ["Analysis error"]
        }
    except Exception as e:
        return {
            "score": 0,
            "summary": f"Error during analysis: {str(e)}",
            "gaps": []
        }

def get_embedding(text: str) -> np.ndarray:
    """Get embedding vector for text."""
    model = get_embed_model()
    return model.encode([text])[0]
