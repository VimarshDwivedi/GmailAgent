import requests
import json
from datetime import datetime

class AIAgent:
    DEFAULT_MODEL = "llama2:7b"
    
    def __init__(self, model=DEFAULT_MODEL, base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.api_model_url = f"{base_url}/api/tags"
        self._initialize_model()

    def set_model(self, model):
        """Set the AI model to use"""
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}. Available models: {list(self.SUPPORTED_MODELS.keys())}")
        self.model = model
        self._initialize_model()



    def get_supported_models(self):
        """Get list of supported models with their properties"""
        return self.SUPPORTED_MODELS

    def pull_model(self, model_name):
        """Pull a model from Ollama"""
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model_name}")
            
        try:
            # First check if model exists
            response = requests.get(self.api_model_url, timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if any(m['name'] == model_name for m in models):
                    return f"Model {model_name} already exists"
            
            # Pull the model
            pull_url = f"{self.base_url}/api/pull"
            response = requests.post(pull_url, json={"name": model_name}, timeout=120)
            
            if response.status_code == 200:
                return f"Successfully pulled model: {model_name}"
            else:
                return f"Failed to pull model: {model_name}. Error: {response.text}"
                
        except Exception as e:
            return f"Error pulling model: {str(e)}"

    def _initialize_model(self):
        """Initialize the selected model"""
        try:
            # Check if model exists
            response = requests.get(self.api_model_url, timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if not any(m['name'] == self.model for m in models):
                    # Model doesn't exist, try to pull it
                    self.pull_model(self.model)
        except Exception as e:
            print(f"Warning: Could not initialize model: {str(e)}")

    def check_model_status(self, model_name):
        """Check if a model exists and its status"""
        try:
            response = requests.get(self.api_model_url, timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_info = next((m for m in models if m['name'] == model_name), None)
                if model_info:
                    return {
                        'exists': True,
                        'status': model_info.get('status', 'unknown'),
                        'size': model_info.get('size', 'unknown')
                    }
                return {'exists': False}
            return {'error': 'Failed to get model status'}
        except Exception as e:
            return {'error': str(e)}
    
    def generate_reply(self, email, user_profile, custom_instruction="", context="", style="Professional"):
        """Generate an AI reply to an email"""
        prompt = self._build_prompt(email, user_profile, custom_instruction, context, style)
        
        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"❌ AI Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Could not connect to Ollama server. Please ensure it's running."
        except requests.exceptions.Timeout:
            return "❌ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def _build_prompt(self, email, user_profile, custom_instruction, context, style):
        """Build the prompt for AI generation"""
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Build user context
        user_context = ""
        if user_profile:
            user_context = f"""
My Profile:
- Name: {user_profile.get('name', 'Not specified')}
- Role: {user_profile.get('role', 'Not specified')}
- Company: {user_profile.get('company', 'Not specified')}
- Email: {user_profile.get('email', 'Not specified')}
- Bio: {user_profile.get('bio', 'Not specified')}
- Preferences: {user_profile.get('preferences', 'Professional and courteous')}
"""
        
        # Build context from RAG
        rag_context = ""
        if context:
            rag_context = f"""
Relevant Context from Knowledge Base:
{context}
"""
        
        # Style guidelines
        style_guide = {
            "Professional": "Use professional, formal language. Be concise and respectful.",
            "Casual": "Use friendly, conversational tone. Be approachable and warm.",
            "Formal": "Use very formal language. Be extremely respectful and traditional.",
            "Friendly": "Use warm, enthusiastic tone. Be personal and engaging."
        }
        
        prompt = f"""You are an intelligent email assistant helping to compose professional email replies.

{user_context}

Email to Reply To:
From: {email['sender']}
Subject: {email['subject']}
Date: {email['date']}
Body: {email['body']}

{rag_context}

Instructions:
- Current date: {current_date}
- Response style: {style} - {style_guide.get(style, '')}
- Custom instruction: {custom_instruction if custom_instruction else 'Reply appropriately to the email'}
- Use the sender's name if available
- Include my name ({user_profile.get('name', 'User')}) in the signature
- Keep the reply concise but complete
- Be helpful and professional
- Address the main points in the original email

Generate only the email reply content (no subject line needed):"""

        return prompt
    
    def generate_email(self, prompt):
        """Generate an email based on the given prompt"""
        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f" AI Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return " Could not connect to Ollama server. Please ensure it's running."
        except requests.exceptions.Timeout:
            return " Request timed out. Please try again."
        except Exception as e:
            return f" Unexpected error: {str(e)}"

    def check_connection(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def generate_summary(self, emails):
        """Generate a summary of multiple emails"""
        if not emails:
            return "No emails to summarize."
        
        email_summaries = []
        for email in emails[:5]:  # Limit to 5 emails
            summary = f"- From {email['sender']}: {email['subject'][:50]}..."
            email_summaries.append(summary)
        
        prompt = f"""Provide a brief summary of these unread emails:

{chr(10).join(email_summaries)}

Total unread emails: {len(emails)}

Provide a concise summary highlighting:
1. Most important/urgent emails
2. Common topics or themes
3. Any action items needed

Summary:"""

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "max_tokens": 200}
            }, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return "Could not generate summary."
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def suggest_action(self, email):
        """Suggest an appropriate action for an email"""
        prompt = f"""Based on this email, suggest the most appropriate action:

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body'][:300]}...

Choose from: Reply, Schedule Meeting, Forward, Archive, Flag for Follow-up, Mark as Important

Suggested Action:"""

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "max_tokens": 50}
            }, timeout=15)
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return "Reply"
            
        except:
            return "Reply"