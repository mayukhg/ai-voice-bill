"""
LLM Service for generative AI features.
Supports OpenAI, Anthropic, and AWS Bedrock.
"""
import logging
import time
from typing import Dict, Any, Optional, List
from src.config import Config

logger = logging.getLogger(__name__)

# Try to import LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")


class LLMService:
    """Service for interacting with Large Language Models."""
    
    def __init__(self):
        """Initialize LLM service based on configuration."""
        self.provider = Config.LLM_PROVIDER.lower()
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE
        self.timeout = Config.LLM_TIMEOUT_SECONDS
        
        # Initialize provider-specific clients
        if self.provider == 'openai' and OPENAI_AVAILABLE:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
        elif self.provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.ANTHROPIC_MODEL
        elif self.provider == 'bedrock':
            import boto3
            self.client = boto3.client('bedrock-runtime', region_name=Config.AWS_REGION)
            self.model = Config.AWS_BEDROCK_MODEL_ID
        else:
            logger.warning(f"LLM provider {self.provider} not available, using mock mode")
            self.client = None
            self.model = None
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            context: Conversation history (list of {role, content} dicts)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            dict: Response with text and metadata
        """
        try:
            start_time = time.time()
            
            if not self.client:
                return self._mock_response(prompt)
            
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature if temperature is not None else self.temperature
            
            if self.provider == 'openai':
                return self._generate_openai(prompt, system_prompt, context, max_tokens, temperature)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(prompt, system_prompt, context, max_tokens, temperature)
            elif self.provider == 'bedrock':
                return self._generate_bedrock(prompt, system_prompt, context, max_tokens, temperature)
            else:
                return self._mock_response(prompt)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return {
                'text': "I apologize, but I'm having trouble processing your request. Please try again.",
                'error': str(e),
                'success': False
            }
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        context: Optional[List[Dict[str, str]]],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        if context:
            messages.extend(context)
        
        messages.append({'role': 'user', 'content': prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=self.timeout
        )
        
        return {
            'text': response.choices[0].message.content,
            'model': self.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'success': True
        }
    
    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        context: Optional[List[Dict[str, str]]],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate response using Anthropic Claude."""
        messages = []
        
        if context:
            for msg in context:
                if msg['role'] == 'user':
                    messages.append({'role': 'user', 'content': msg['content']})
                elif msg['role'] == 'assistant':
                    messages.append({'role': 'assistant', 'content': msg['content']})
        
        messages.append({'role': 'user', 'content': prompt})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages
        )
        
        return {
            'text': response.content[0].text,
            'model': self.model,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            },
            'success': True
        }
    
    def _generate_bedrock(
        self,
        prompt: str,
        system_prompt: Optional[str],
        context: Optional[List[Dict[str, str]]],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate response using AWS Bedrock."""
        import json
        
        messages = []
        
        if context:
            messages.extend(context)
        
        messages.append({'role': 'user', 'content': prompt})
        
        body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': messages
        }
        
        if system_prompt:
            body['system'] = system_prompt
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        return {
            'text': response_body['content'][0]['text'],
            'model': self.model,
            'usage': response_body.get('usage', {}),
            'success': True
        }
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response for testing when LLM is not available."""
        logger.warning("Using mock LLM response")
        return {
            'text': f"Mock response to: {prompt[:50]}...",
            'model': 'mock',
            'usage': {'total_tokens': 0},
            'success': True
        }
    
    def generate_with_emotion_context(
        self,
        prompt: str,
        emotion: str,
        emotion_confidence: float,
        intent: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response with emotion-aware context.
        
        Args:
            prompt: User prompt
            emotion: Detected emotion
            emotion_confidence: Confidence score
            intent: Detected intent
            system_prompt: System prompt
            context: Conversation history
            
        Returns:
            dict: Emotion-aware response
        """
        emotion_prompt = f"""
User emotion: {emotion} (confidence: {emotion_confidence:.2f})
User intent: {intent}

Based on the detected emotion, adapt your response tone:
- If frustration: Use empathetic, calming tone. Offer assistance and escalation options.
- If confusion: Use clear, simple language. Provide step-by-step guidance.
- If urgency: Prioritize quick, actionable responses.
- If satisfaction: Acknowledge positive sentiment, maintain friendly tone.

User query: {prompt}
"""
        
        return self.generate_response(emotion_prompt, system_prompt, context)
    
    def correct_stt_error(
        self,
        stt_text: str,
        stt_confidence: float,
        user_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Correct STT errors using context.
        
        Args:
            stt_text: STT transcription
            stt_confidence: STT confidence score
            user_context: User's bill history and context
            conversation_history: Previous conversation turns
            
        Returns:
            dict: Corrected text and confidence
        """
        system_prompt = """You are an intelligent assistant that corrects speech-to-text errors in bill payment conversations.
Use the user's bill history and context to identify and correct misinterpretations.
Present corrections as natural confirmations, not assumptions."""

        context_str = f"""
User's bill history:
- Bill types: {', '.join(user_context.get('bill_types', []))}
- Recent amounts: {', '.join(map(str, user_context.get('recent_amounts', [])))}
- Common patterns: {user_context.get('patterns', 'N/A')}

STT Transcription: "{stt_text}"
STT Confidence: {stt_confidence:.2f}

Identify potential errors and suggest corrections based on billing context.
If the transcription seems correct, confirm it.
If there are errors, suggest the most likely correction with confidence.
"""

        prompt = f"{context_str}\n\nProvide the corrected text and explanation:"
        
        response = self.generate_response(prompt, system_prompt, conversation_history)
        
        return {
            'original_text': stt_text,
            'corrected_text': response.get('text', stt_text),
            'confidence': stt_confidence,
            'correction_applied': response.get('text', stt_text) != stt_text,
            'llm_response': response
        }

