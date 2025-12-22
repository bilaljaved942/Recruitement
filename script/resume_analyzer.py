import os
import fitz
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env file
load_dotenv()

# Initialize Embeddings (Still local/free)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Google Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

class ResumeAIPipeline:
    def __init__(self):
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.stored_resumes = []

    def extract_text(self, pdf_path):
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

    def process_and_index(self, resume_id, text):
        vector = embed_model.encode([text])
        self.index.add(np.array(vector).astype('float32'))
        self.stored_resumes.append({"id": resume_id, "text": text})

    def generate_analysis(self, resume_text, job_desc):
        """Uses Google Gemini to summarize and score."""
        prompt = f"""
        Strictly analyze the Resume against the Job Description.
        
        JOB DESCRIPTION:
        {job_desc}
        
        RESUME:
        {resume_text[:10000]} # Gemini can handle much larger text than local models
        
        RESPONSE FORMAT:
        - Score: (0-100)
        - Summary: (Max 3 sentences)
        - Key Gaps: (List 3 missing skills)
        """
        # Invoke the cloud model
        response = llm.invoke(prompt)
        return response.content

    def find_top_matches(self, job_desc, top_k=3):
        job_vector = embed_model.encode([job_desc])
        distances, indices = self.index.search(np.array(job_vector).astype('float32'), top_k)
        matches = []
        for idx in indices[0]:
            if idx != -1:
                matches.append(self.stored_resumes[idx])
        return matches

if __name__ == "__main__":
    pipeline = ResumeAIPipeline()
    job_info = "Looking for a QA Engineer with experience in testing of applications."
    
    # Process local file
    sample_text = pipeline.extract_text("C:\\Users\\hp\\Documents\\Recruitment\\CV_documents\\resume1.pdf")
    pipeline.process_and_index("Candidate_01", sample_text)
    print(pipeline.stored_resumes)
    
    # Generate Cloud AI Report
    report = pipeline.generate_analysis(sample_text, job_info)
    print("--- GOOGLE AI ANALYSIS ---\n", report)