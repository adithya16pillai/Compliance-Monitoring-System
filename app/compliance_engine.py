import json
import re
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
import openai
from anthropic import Anthropic
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import pandas as pd

load_dotenv()

class ComplianceEngine:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.setup_llm_clients()
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(
            name="compliance_docs",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        
        # Load compliance rules
        self.rules = self.load_all_rules()
    
    def setup_llm_clients(self):
        """Initialize LLM clients based on available API keys"""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if openai_key:
            openai.api_key = openai_key
            self.openai_client = openai
        
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
    
    def load_all_rules(self) -> Dict[str, Any]:
        """Load all compliance rules from JSON files"""
        rules = {}
        rules_dir = os.path.join(os.path.dirname(__file__), "rules")
        
        for filename in os.listdir(rules_dir):
            if filename.endswith("_rules.json"):
                rule_type = filename.replace("_rules.json", "").upper()
                with open(os.path.join(rules_dir, filename), 'r') as f:
                    rules[rule_type] = json.load(f)
        
        return rules
    
    def add_document_to_vector_db(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Add document to ChromaDB for retrieval QA"""
        # Split document into chunks
        chunks = self.chunk_text(content, chunk_size=1000, overlap=200)
        
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas=[{**metadata, "chunk_id": i}],
                ids=[f"{doc_id}_chunk_{i}"]
            )
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if end >= len(text):
                break
        
        return chunks
    
    def retrieve_relevant_context(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    
    def check_pattern_compliance(self, content: str, rule: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check document against pattern-based rules"""
        violations = []
        patterns = rule.get("patterns", [])
        
        for pattern in patterns:
            # Simple keyword matching (can be enhanced with regex)
            if pattern.lower() in content.lower():
                # Find context around the match
                content_lower = content.lower()
                start = content_lower.find(pattern.lower())
                context_start = max(0, start - 100)
                context_end = min(len(content), start + len(pattern) + 100)
                context = content[context_start:context_end]
                violations.append(f"Found '{pattern}' in context: ...{context}...")
        
        return len(violations) > 0, violations
    
    def llm_compliance_check(self, content: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze compliance"""
        prompt = f"""
        Compliance Analysis Request:
        
        Rule: {rule['name']}
        Description: {rule['description']}
        Analysis Prompt: {rule.get('llm_prompt', 'Analyze this document for compliance violations.')}
        
        Document Content:
        {content[:3000]}  # Limit content to avoid token limits
        
        Please analyze the document and respond with:
        1. Is there a compliance violation? (Yes/No)
        2. Confidence score (0.0 to 1.0)
        3. Evidence from the document (specific quotes)
        4. Explanation of the violation or compliance
        
        Format your response as JSON:
        {{
            "violation": true/false,
            "confidence": 0.0-1.0,
            "evidence": ["quote1", "quote2"],
            "explanation": "detailed explanation"
        }}
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text
            else:
                return {
                    "violation": False,
                    "confidence": 0.0,
                    "evidence": [],
                    "explanation": "No LLM API configured"
                }
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {
                    "violation": True,
                    "confidence": 0.5,
                    "evidence": [],
                    "explanation": result
                }
                
        except Exception as e:
            return {
                "violation": False,
                "confidence": 0.0,
                "evidence": [],
                "explanation": f"LLM analysis failed: {str(e)}"
            }
    
    def analyze_document(self, doc_id: str, content: str, rule_types: List[str] = None) -> List[Dict[str, Any]]:
        """Analyze document for compliance violations"""
        results = []
        
        # Add document to vector DB for retrieval QA
        self.add_document_to_vector_db(doc_id, content, {"doc_id": doc_id})
        
        # If no rule types specified, use all available
        if rule_types is None:
            rule_types = list(self.rules.keys())
        
        for rule_type in rule_types:
            if rule_type not in self.rules:
                continue
                
            rule_set = self.rules[rule_type]
            
            for rule in rule_set.get("rules", []):
                # Pattern-based checking
                has_pattern_violation, pattern_evidence = self.check_pattern_compliance(content, rule)
                
                # LLM-based analysis
                llm_result = self.llm_compliance_check(content, rule)
                
                # Combine results
                result = {
                    "document_id": doc_id,
                    "rule_type": rule_type,
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "violation_type": rule["description"],
                    "severity": rule.get("severity", "MEDIUM"),
                    "pattern_violation": has_pattern_violation,
                    "pattern_evidence": pattern_evidence,
                    "llm_violation": llm_result.get("violation", False),
                    "llm_confidence": llm_result.get("confidence", 0.0),
                    "llm_evidence": llm_result.get("evidence", []),
                    "llm_explanation": llm_result.get("explanation", ""),
                    "overall_violation": has_pattern_violation or llm_result.get("violation", False),
                    "confidence_score": max(
                        0.8 if has_pattern_violation else 0.0,
                        llm_result.get("confidence", 0.0)
                    ),
                    "created_at": datetime.utcnow()
                }
                
                results.append(result)
        
        return results
    
    def generate_compliance_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive compliance report"""
        if not results:
            return {"status": "No violations found", "summary": {}}
        
        # Group by rule type and severity
        df = pd.DataFrame(results)
        
        summary = {
            "total_violations": len(df[df["overall_violation"] == True]),
            "total_checks": len(df),
            "violations_by_type": df[df["overall_violation"] == True].groupby("rule_type").size().to_dict(),
            "violations_by_severity": df[df["overall_violation"] == True].groupby("severity").size().to_dict(),
            "high_confidence_violations": len(df[(df["overall_violation"] == True) & (df["confidence_score"] > 0.7)]),
            "compliance_score": (len(df) - len(df[df["overall_violation"] == True])) / len(df) * 100
        }
        
        return {
            "status": "Analysis Complete",
            "summary": summary,
            "detailed_results": results
        }