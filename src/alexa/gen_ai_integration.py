"""
Gen-AI Integration for Alexa Skill.
Integrates emotion detection, error correction, and dialogue management.
"""
import logging
from typing import Dict, Any, Optional
from ask_sdk_core.handler_input import HandlerInput
from src.gen_ai.dialogue_manager import DialogueManager
from src.alexa.session_manager import SessionManager

logger = logging.getLogger(__name__)

# Initialize dialogue manager
dialogue_manager = DialogueManager()


def process_with_gen_ai(
    handler_input: HandlerInput,
    user_text: str,
    intent_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process user input with gen-AI pipeline.
    
    Args:
        handler_input: ASK handler input
        user_text: User's input text
        intent_name: Detected intent name (optional)
        
    Returns:
        dict: Processed result with response and metadata
    """
    try:
        # Get session ID and user ID
        session_id = handler_input.request_envelope.session.session_id
        user_id = SessionManager.get_user_id(handler_input)
        
        if not user_id:
            user_id = session_id  # Fallback to session ID
        
        # Get STT confidence if available
        stt_confidence = 1.0  # Default
        # In production, extract from request metadata
        
        # Process turn with dialogue manager
        result = dialogue_manager.process_turn(
            session_id=session_id,
            user_id=user_id,
            user_input=user_text,
            stt_confidence=stt_confidence
        )
        
        # Store emotion and intent in session
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['last_emotion'] = result.get('emotion', 'neutral')
        session_attr['last_intent'] = result.get('intent', 'general')
        session_attr['correction_applied'] = result.get('correction_applied', False)
        handler_input.attributes_manager.session_attributes = session_attr
        
        return result
        
    except Exception as e:
        logger.error(f"Error in gen-AI processing: {str(e)}")
        return {
            'response': user_text,  # Fallback to original
            'success': False,
            'error': str(e)
        }


def get_user_text_from_handler(handler_input: HandlerInput) -> str:
    """Extract user text from handler input."""
    try:
        # Try to get from intent slots or request
        request = handler_input.request_envelope.request
        
        if hasattr(request, 'intent') and request.intent:
            # Get from slots
            slots = request.intent.slots or {}
            # Try to reconstruct from slots or use intent name
            return request.intent.name or "user query"
        else:
            return "user query"
    except Exception as e:
        logger.error(f"Error extracting user text: {str(e)}")
        return "user query"


def enhance_response_with_gen_ai(
    handler_input: HandlerInput,
    base_response: str,
    user_text: Optional[str] = None
) -> str:
    """
    Enhance response using gen-AI if enabled.
    
    Args:
        handler_input: ASK handler input
        base_response: Base response from intent handler
        user_text: User's input text (optional)
        
    Returns:
        str: Enhanced response
    """
    try:
        from src.config import Config
        
        # Check if gen-AI is enabled
        if not Config.EMOTION_DETECTION_ENABLED:
            return base_response
        
        # Get emotion from session
        session_attr = handler_input.attributes_manager.session_attributes
        emotion = session_attr.get('last_emotion', 'neutral')
        emotion_confidence = session_attr.get('emotion_confidence', 0.5)
        
        # Adapt response tone
        from src.gen_ai.emotion_detector import EmotionDetector
        emotion_detector = EmotionDetector()
        
        enhanced_response = emotion_detector.adapt_response_tone(
            base_response,
            emotion,
            emotion_confidence
        )
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error enhancing response: {str(e)}")
        return base_response

