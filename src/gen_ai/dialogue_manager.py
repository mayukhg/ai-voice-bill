"""
Multi-Turn Dialogue Management Service.
Manages conversation context and enables natural multi-turn dialogues.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.gen_ai.context_store import ContextStore
from src.gen_ai.entity_tracker import EntityTracker
from src.gen_ai.llm_service import LLMService
from src.gen_ai.emotion_detector import EmotionDetector
from src.gen_ai.error_corrector import ErrorCorrector

logger = logging.getLogger(__name__)


class DialogueManager:
    """Service for managing multi-turn dialogues with context retention."""
    
    def __init__(self):
        """Initialize dialogue manager."""
        self.context_store = ContextStore()
        self.entity_tracker = EntityTracker()
        self.llm_service = LLMService()
        self.emotion_detector = EmotionDetector()
        self.error_corrector = ErrorCorrector()
    
    def process_turn(
        self,
        session_id: str,
        user_id: str,
        user_input: str,
        stt_confidence: float = 1.0,
        voice_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a conversation turn with full gen-AI pipeline.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            user_input: User's input text
            stt_confidence: STT confidence score
            voice_metadata: Optional voice characteristics
            
        Returns:
            dict: Processed turn with response and metadata
        """
        try:
            # Step 1: Get existing context
            context = self.context_store.get_context(session_id, user_id)
            
            # Step 2: Correct STT errors
            correction_result = self.error_corrector.correct_stt_text(
                user_input,
                stt_confidence,
                user_id,
                self._format_history(context.get('turns', []))
            )
            
            corrected_input = correction_result.get('corrected_text', user_input)
            
            # Step 3: Detect emotion and intent
            emotion_result = self.emotion_detector.detect_emotion_and_intent(
                corrected_input,
                voice_metadata
            )
            
            # Step 4: Extract entities
            entities = self.entity_tracker.extract_entities(corrected_input, context)
            
            # Step 5: Resolve references
            resolved_entities = self._resolve_references(entities, context)
            
            # Step 6: Generate response with context
            response = self._generate_contextual_response(
                corrected_input,
                context,
                emotion_result,
                resolved_entities,
                user_id
            )
            
            # Step 7: Adapt response tone based on emotion
            adapted_response = self.emotion_detector.adapt_response_tone(
                response.get('text', ''),
                emotion_result.get('emotion', 'neutral'),
                emotion_result.get('emotion_confidence', 0.5)
            )
            
            # Step 8: Save turn to context
            turn = {
                'question': corrected_input,
                'answer': adapted_response,
                'timestamp': datetime.utcnow().isoformat(),
                'entities': resolved_entities
            }
            
            conversation_state = self._determine_state(corrected_input, emotion_result)
            self.context_store.save_context(session_id, user_id, turn, conversation_state)
            
            # Step 9: Return result
            result = {
                'original_input': user_input,
                'corrected_input': corrected_input,
                'correction_applied': correction_result.get('correction_applied', False),
                'response': adapted_response,
                'emotion': emotion_result.get('emotion', 'neutral'),
                'emotion_confidence': emotion_result.get('emotion_confidence', 0.5),
                'intent': emotion_result.get('intent', 'general'),
                'entities': resolved_entities,
                'should_escalate': emotion_result.get('should_escalate', False),
                'should_offer_escalation': emotion_result.get('should_offer_escalation', False),
                'conversation_state': conversation_state,
                'success': True
            }
            
            logger.info(f"Processed turn for session {session_id}: {emotion_result.get('emotion')} emotion, "
                       f"{emotion_result.get('intent')} intent")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing turn: {str(e)}")
            return {
                'original_input': user_input,
                'response': "I apologize, but I encountered an error. Please try again.",
                'success': False,
                'error': str(e)
            }
    
    def _format_history(self, turns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format conversation history for LLM."""
        history = []
        for turn in turns:
            history.append({
                'role': 'user',
                'content': turn.get('question', '')
            })
            history.append({
                'role': 'assistant',
                'content': turn.get('answer', '')
            })
        return history
    
    def _resolve_references(
        self,
        entities: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve references to previous entities."""
        resolved = entities.copy()
        
        references = entities.get('references', [])
        if references:
            for ref in references:
                resolved_entity = self.entity_tracker.resolve_reference(ref, context)
                if resolved_entity:
                    # Add resolved entity to appropriate category
                    entity_type = resolved_entity.get('type')
                    if entity_type == 'bill':
                        resolved['bills'].append(resolved_entity.get('text', ''))
                    elif entity_type == 'date':
                        resolved['dates'].append(resolved_entity.get('text', ''))
                    elif entity_type == 'amount':
                        resolved['amounts'].append(resolved_entity.get('text', ''))
        
        return resolved
    
    def _generate_contextual_response(
        self,
        user_input: str,
        context: Dict[str, Any],
        emotion_result: Dict[str, Any],
        entities: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate response using LLM with full context."""
        # Build system prompt
        system_prompt = """You are a helpful bill payment assistant. You help users manage and pay their bills.
Use the conversation context to understand references and provide natural, helpful responses.
Be empathetic and clear in your communication."""
        
        # Build context string
        context_str = self._build_context_string(context, entities)
        
        # Build prompt
        prompt = f"""
{context_str}

User query: "{user_input}"

Provide a helpful, natural response. Use the conversation context to understand references.
If the user refers to "that one" or "the month before", use the context to understand what they mean.
"""
        
        # Generate response
        response = self.llm_service.generate_with_emotion_context(
            prompt,
            emotion_result.get('emotion', 'neutral'),
            emotion_result.get('emotion_confidence', 0.5),
            emotion_result.get('intent', 'general'),
            system_prompt,
            self._format_history(context.get('turns', []))
        )
        
        return response
    
    def _build_context_string(
        self,
        context: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> str:
        """Build context string for LLM prompt."""
        turns = context.get('turns', [])
        
        if not turns:
            return "This is the start of the conversation."
        
        context_str = "Previous conversation:\n"
        for i, turn in enumerate(turns[-5:], 1):  # Last 5 turns
            context_str += f"{i}. User: {turn.get('question', '')}\n"
            context_str += f"   Assistant: {turn.get('answer', '')}\n"
        
        # Add entity context
        if entities:
            context_str += "\nCurrent entities mentioned:\n"
            if entities.get('bills'):
                context_str += f"- Bills: {', '.join(entities['bills'])}\n"
            if entities.get('dates'):
                context_str += f"- Dates: {', '.join(entities['dates'])}\n"
            if entities.get('amounts'):
                context_str += f"- Amounts: ${', $'.join(map(str, entities['amounts']))}\n"
        
        return context_str
    
    def _determine_state(
        self,
        user_input: str,
        emotion_result: Dict[str, Any]
    ) -> str:
        """Determine conversation state."""
        intent = emotion_result.get('intent', 'general')
        emotion = emotion_result.get('emotion', 'neutral')
        
        if intent == 'payment':
            return 'PAYMENT_IN_PROGRESS'
        elif emotion == 'frustration':
            return 'FRUSTRATION_DETECTED'
        elif emotion == 'confusion':
            return 'CLARIFICATION_NEEDED'
        else:
            return 'ACTIVE'
    
    def get_conversation_summary(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of conversation."""
        context = self.context_store.get_context(session_id, user_id)
        
        return {
            'session_id': session_id,
            'turn_count': len(context.get('turns', [])),
            'state': context.get('state', 'IDLE'),
            'entities': context.get('entities', {}),
            'last_turn': context.get('turns', [])[-1] if context.get('turns') else None
        }
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation context."""
        return self.context_store.clear_context(session_id)

