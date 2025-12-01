"""
Emotion and Intent Detection Service.
Detects user's emotional state and intent from voice/text input.
"""
import logging
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.config import Config
from src.gen_ai.llm_service import LLMService

logger = logging.getLogger(__name__)


class EmotionDetector:
    """Service for detecting emotions and intents from user input."""
    
    def __init__(self):
        """Initialize emotion detection service."""
        self.enabled = Config.EMOTION_DETECTION_ENABLED
        self.provider = Config.EMOTION_DETECTION_PROVIDER
        self.threshold = Config.EMOTION_DETECTION_THRESHOLD
        self.escalation_threshold = Config.FRUSTRATION_ESCALATION_THRESHOLD
        self.llm_service = LLMService()
        
        # Initialize AWS Comprehend if using AWS
        if self.provider == 'comprehend':
            try:
                self.comprehend = boto3.client('comprehend', region_name=Config.AWS_REGION)
            except Exception as e:
                logger.warning(f"Could not initialize Comprehend: {str(e)}")
                self.comprehend = None
        else:
            self.comprehend = None
    
    def detect_emotion_and_intent(
        self,
        text: str,
        voice_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect emotion and intent from text and voice metadata.
        
        Args:
            text: User's transcribed text
            voice_metadata: Optional voice characteristics (pitch, rate, volume)
            
        Returns:
            dict: Emotion and intent detection results
        """
        if not self.enabled:
            return self._default_result()
        
        try:
            # Detect emotion
            emotion_result = self._detect_emotion(text, voice_metadata)
            
            # Detect intent
            intent_result = self._detect_intent(text)
            
            # Combine results
            result = {
                'emotion': emotion_result.get('emotion', 'neutral'),
                'emotion_confidence': emotion_result.get('confidence', 0.5),
                'intent': intent_result.get('intent', 'general'),
                'intent_confidence': intent_result.get('confidence', 0.5),
                'should_escalate': emotion_result.get('emotion') == 'frustration' and \
                                 emotion_result.get('confidence', 0) >= self.escalation_threshold,
                'should_offer_escalation': emotion_result.get('emotion') == 'frustration' and \
                                          self.threshold <= emotion_result.get('confidence', 0) < self.escalation_threshold,
                'detection_timestamp': datetime.utcnow().isoformat(),
                'success': True
            }
            
            logger.info(f"Emotion detected: {result['emotion']} ({result['emotion_confidence']:.2f}), "
                       f"Intent: {result['intent']} ({result['intent_confidence']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {str(e)}")
            return self._default_result()
    
    def _detect_emotion(
        self,
        text: str,
        voice_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Detect emotion from text and voice."""
        if self.provider == 'comprehend' and self.comprehend:
            return self._detect_with_comprehend(text)
        else:
            return self._detect_with_llm(text, voice_metadata)
    
    def _detect_with_comprehend(self, text: str) -> Dict[str, Any]:
        """Detect emotion using AWS Comprehend."""
        try:
            response = self.comprehend.detect_sentiment(Text=text, LanguageCode='en')
            
            sentiment = response['Sentiment'].lower()
            scores = response['SentimentScore']
            
            # Map Comprehend sentiment to our emotions
            emotion_map = {
                'positive': 'satisfaction',
                'negative': 'frustration',
                'neutral': 'neutral',
                'mixed': 'confusion'
            }
            
            emotion = emotion_map.get(sentiment, 'neutral')
            confidence = scores.get('Positive' if sentiment == 'positive' else 
                                  'Negative' if sentiment == 'negative' else
                                  'Neutral', 0.5)
            
            return {
                'emotion': emotion,
                'confidence': confidence
            }
        except Exception as e:
            logger.error(f"Error with Comprehend: {str(e)}")
            return self._detect_with_llm(text)
    
    def _detect_with_llm(
        self,
        text: str,
        voice_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Detect emotion using LLM."""
        system_prompt = """You are an emotion detection system. Analyze the user's text and detect their emotional state.
Return one of: frustration, confusion, urgency, satisfaction, neutral.
Also provide a confidence score (0-1)."""

        voice_context = ""
        if voice_metadata:
            voice_context = f"""
Voice characteristics:
- Pitch variation: {voice_metadata.get('pitch_variation', 'normal')}
- Speech rate: {voice_metadata.get('speech_rate', 'normal')}
- Volume: {voice_metadata.get('volume', 'normal')}
"""

        prompt = f"""
Analyze this user input and detect the emotional state:

{voice_context}
User text: "{text}"

Return JSON with:
- emotion: one of [frustration, confusion, urgency, satisfaction, neutral]
- confidence: float between 0 and 1
"""

        response = self.llm_service.generate_response(prompt, system_prompt)
        
        # Parse LLM response (try to extract JSON)
        import json
        import re
        
        text_response = response.get('text', '')
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', text_response)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'emotion': result.get('emotion', 'neutral'),
                    'confidence': float(result.get('confidence', 0.5))
                }
            except:
                pass
        
        # Fallback: simple keyword matching
        return self._detect_with_keywords(text)
    
    def _detect_with_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based emotion detection."""
        text_lower = text.lower()
        
        frustration_keywords = ['frustrated', 'angry', 'annoyed', 'upset', 'wrong', 'error', 'broken']
        confusion_keywords = ['confused', 'don\'t understand', 'unclear', 'what', 'how', 'help']
        urgency_keywords = ['urgent', 'asap', 'immediately', 'now', 'quickly', 'soon']
        satisfaction_keywords = ['thanks', 'thank you', 'great', 'good', 'perfect', 'excellent']
        
        if any(kw in text_lower for kw in frustration_keywords):
            return {'emotion': 'frustration', 'confidence': 0.7}
        elif any(kw in text_lower for kw in confusion_keywords):
            return {'emotion': 'confusion', 'confidence': 0.7}
        elif any(kw in text_lower for kw in urgency_keywords):
            return {'emotion': 'urgency', 'confidence': 0.7}
        elif any(kw in text_lower for kw in satisfaction_keywords):
            return {'emotion': 'satisfaction', 'confidence': 0.7}
        else:
            return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect user intent from text."""
        system_prompt = """You are an intent classification system for a bill payment service.
Classify the user's intent into one of: payment, inquiry, complaint, account_management, general."""

        prompt = f"""
Classify this user intent:

User text: "{text}"

Return JSON with:
- intent: one of [payment, inquiry, complaint, account_management, general]
- confidence: float between 0 and 1
"""

        response = self.llm_service.generate_response(prompt, system_prompt)
        
        # Parse response
        import json
        import re
        
        text_response = response.get('text', '')
        json_match = re.search(r'\{[^}]+\}', text_response)
        
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'intent': result.get('intent', 'general'),
                    'confidence': float(result.get('confidence', 0.5))
                }
            except:
                pass
        
        # Fallback: keyword-based intent detection
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['pay', 'payment', 'bill']):
            return {'intent': 'payment', 'confidence': 0.7}
        elif any(kw in text_lower for kw in ['what', 'show', 'list', 'check']):
            return {'intent': 'inquiry', 'confidence': 0.7}
        elif any(kw in text_lower for kw in ['problem', 'issue', 'wrong', 'error']):
            return {'intent': 'complaint', 'confidence': 0.7}
        else:
            return {'intent': 'general', 'confidence': 0.5}
    
    def _default_result(self) -> Dict[str, Any]:
        """Return default result when emotion detection is disabled."""
        return {
            'emotion': 'neutral',
            'emotion_confidence': 0.5,
            'intent': 'general',
            'intent_confidence': 0.5,
            'should_escalate': False,
            'should_offer_escalation': False,
            'success': True
        }
    
    def adapt_response_tone(
        self,
        base_response: str,
        emotion: str,
        emotion_confidence: float
    ) -> str:
        """
        Adapt response tone based on detected emotion.
        
        Args:
            base_response: Original response text
            emotion: Detected emotion
            emotion_confidence: Confidence score
            
        Returns:
            str: Adapted response
        """
        if emotion == 'frustration' and emotion_confidence >= self.threshold:
            # Add empathetic tone
            return f"I understand this can be frustrating. {base_response} I'm here to help. Would you like me to connect you with a support agent?"
        elif emotion == 'confusion' and emotion_confidence >= self.threshold:
            # Add clarity
            return f"Let me explain this clearly. {base_response} If you have any questions, I'm happy to help."
        elif emotion == 'urgency' and emotion_confidence >= self.threshold:
            # Prioritize action
            return f"I'll help you right away. {base_response}"
        else:
            return base_response

