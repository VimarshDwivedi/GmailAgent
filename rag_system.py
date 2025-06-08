import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2
import docx

class RAGSystem:
    def __init__(self, storage_path="knowledge_base"):
        self.storage_path = storage_path
        self.documents = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = None
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing documents
        self._load_documents()
    
    def add_document(self, file_or_text, title=None, metadata=None):
        """Add a document to the knowledge base"""
        
        # Extract text based on input type
        if hasattr(file_or_text, 'read'):  # File-like object
            text = self._extract_text_from_file(file_or_text)
            title = title or getattr(file_or_text, 'name', 'Uploaded Document')
        else:  # String text
            text = file_or_text
            title = title or f"Document {len(self.documents) + 1}"
        
        if not text or len(text.strip()) < 10:
            raise ValueError("Document text is too short or empty")
        
        # Create document object
        doc_id = hashlib.md5(text.encode()).hexdigest()
        document = {
            'id': doc_id,
            'title': title,
            'content': text,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'word_count': len(text.split())
        }
        
        # Check if document already exists
        if any(doc['id'] == doc_id for doc in self.documents):
            raise ValueError("Document already exists in knowledge base")
        
        # Add to documents list
        self.documents.append(document)
        
        # Update vectors
        self._update_vectors()
        
        # Save to disk
        self._save_documents()
        
        return doc_id
    
    def _extract_text_from_file(self, file):
        """Extract text from uploaded file"""
        file_type = file.type if hasattr(file, 'type') else 'text/plain'
        
        if file_type == 'text/plain':
            return file.read().decode('utf-8')
        
        elif file_type == 'application/pdf':
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            # Try to read as text
            try:
                return file.read().decode('utf-8')
            except:
                raise ValueError(f"Unsupported file type: {file_type}")
    
    def get_relevant_context(self, query, max_results=3, min_similarity=0.1):
        """Get relevant context for a query"""
        if not self.documents or self.document_vectors is None:
            return ""
        
        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.document_vectors)[0]
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            relevant_contexts = []
            for idx in top_indices:
                if similarities[idx] >= min_similarity:
                    doc = self.documents[idx]
                    context = self._extract_relevant_snippet(doc['content'], query)
                    relevant_contexts.append({
                        'title': doc['title'],
                        'content': context,
                        'similarity': float(similarities[idx])
                    })
            
            # Format context for AI
            if relevant_contexts:
                context_text = ""
                for ctx in relevant_contexts:
                    context_text += f"From '{ctx['title']}':\n{ctx['content']}\n\n"
                return context_text.strip()
            
            return ""
            
        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return ""
    
    def _extract_relevant_snippet(self, text, query, snippet_length=200):
        """Extract relevant snippet from document"""
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # Find best position
        best_pos = 0
        best_score = 0
        
        words = text.split()
        for i in range(len(words)):
            snippet = ' '.join(words[i:i+50])  # 50 word window
            snippet_lower = snippet.lower()
            
            score = sum(1 for word in query_words if word in snippet_lower)
            if score > best_score:
                best_score = score
                best_pos = i
        
        # Extract snippet
        start = max(0, best_pos - 10)
        end = min(len(words), best_pos + 40)
        snippet = ' '.join(words[start:end])
        
        # Truncate if too long
        if len(snippet) > snippet_length:
            snippet = snippet[:snippet_length] + "..."
        
        return snippet
    
    def _update_vectors(self):
        """Update document vectors"""
        if not self.documents:
            self.document_vectors = None
            return
        
        try:
            contents = [doc['content'] for doc in self.documents]
            self.document_vectors = self.vectorizer.fit_transform(contents)
        except Exception as e:
            print(f"Error updating vectors: {e}")
            self.document_vectors = None
    
    def _save_documents(self):
        """Save documents to disk"""
        try:
            with open(os.path.join(self.storage_path, 'documents.json'), 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Error saving documents: {e}")
    
    def _load_documents(self):
        """Load documents from disk"""
        try:
            doc_file = os.path.join(self.storage_path, 'documents.json')
            if os.path.exists(doc_file):
                with open(doc_file, 'r') as f:
                    self.documents = json.load(f)
                self._update_vectors()
        except Exception as e:
            print(f"Error loading documents: {e}")
            self.documents = []
    
    def get_stats(self):
        """Get knowledge base statistics"""
        total_words = sum(doc.get('word_count', 0) for doc in self.documents)
        return {
            'total_documents': len(self.documents),
            'total_words': total_words,
            'average_words': total_words // len(self.documents) if self.documents else 0
        }
    
    def search_documents(self, query, limit=5):
        """Search documents by query"""
        if not self.documents:
            return []
        
        try:
            context = self.get_relevant_context(query, max_results=limit, min_similarity=0.05)
            if context:
                return [{'title': doc['title'], 'snippet': context[:200]} for doc in self.documents[:limit]]
            return []
        except:
            return []
    
    def remove_document(self, doc_id):
        """Remove a document from knowledge base"""
        self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
        self._update_vectors()
        self._save_documents()
    
    def clear_knowledge_base(self):
        """Clear all documents"""
        self.documents = []
        self.document_vectors = None
        self._save_documents()
    
    def add_text_snippet(self, text, title, metadata=None):
        """Add a simple text snippet to knowledge base"""
        return self.add_document(text, title, metadata)