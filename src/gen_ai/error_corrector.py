"""
Contextual Error Correction Service.
Corrects STT errors using billing context and LLM.
"""
import logging
import re
from typing import Dict, Any, Optional, List
from src.config import Config
from src.gen_ai.llm_service import LLMService
from src.aws_services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)


class ErrorCorrector:
    """Service for correcting STT errors using context."""
    
    def __init__(self):
        """Initialize error correction service."""
        self.enabled = Config.ERROR_CORRECTION_ENABLED
        self.confidence_threshold = Config.ERROR_CORRECTION_CONFIDENCE_THRESHOLD
        self.llm_service = LLMService()
        self.db_service = DynamoDBService()
    
    def correct_stt_text(
        self,
        stt_text: str,
        stt_confidence: float,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Correct STT errors using billing context.
        
        Args:
            stt_text: STT transcription
            stt_confidence: STT confidence score
            user_id: User identifier
            conversation_history: Previous conversation turns
            
        Returns:
            dict: Correction result with corrected text and confidence
        """
        if not self.enabled:
            return {
                'original_text': stt_text,
                'corrected_text': stt_text,
                'correction_applied': False,
                'confidence': stt_confidence,
                'success': True
            }
        
        try:
            # Get user context
            user_context = self._get_user_context(user_id)
            
            # Check if correction is needed
            if stt_confidence >= self.confidence_threshold:
                # High confidence, likely correct
                return {
                    'original_text': stt_text,
                    'corrected_text': stt_text,
                    'correction_applied': False,
                    'confidence': stt_confidence,
                    'success': True
                }
            
            # Use LLM to correct
            correction_result = self.llm_service.correct_stt_error(
                stt_text,
                stt_confidence,
                user_context,
                conversation_history
            )
            
            # Extract corrected text from LLM response
            corrected_text = self._extract_corrected_text(
                correction_result.get('corrected_text', stt_text),
                stt_text
            )
            
            # Determine if correction should be applied
            correction_applied = corrected_text.lower() != stt_text.lower()
            
            # Calculate confidence
            if correction_applied:
                # Use LLM confidence if available, otherwise use STT confidence
                confidence = correction_result.get('confidence', stt_confidence + 0.2)
            else:
                confidence = stt_confidence
            
            result = {
                'original_text': stt_text,
                'corrected_text': corrected_text,
                'correction_applied': correction_applied,
                'confidence': min(confidence, 1.0),
                'suggestions': self._generate_suggestions(stt_text, corrected_text, user_context),
                'success': True
            }
            
            if correction_applied:
                logger.info(f"STT correction: '{stt_text}' -> '{corrected_text}'")
            
            return result
            
        except Exception as e:
            logger.error(f"Error correcting STT text: {str(e)}")
            return {
                'original_text': stt_text,
                'corrected_text': stt_text,
                'correction_applied': False,
                'confidence': stt_confidence,
                'error': str(e),
                'success': False
            }
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's billing context for error correction."""
        try:
            # Get user's bills
            bills = self.db_service.get_user_bills(user_id, include_paid=True)
            
            # Extract context
            bill_types = list(set([bill.get('bill_type', '') for bill in bills if bill.get('bill_type')]))
            amounts = [float(bill.get('amount', 0)) for bill in bills if bill.get('amount')]
            recent_amounts = sorted(set(amounts), reverse=True)[:10]  # Top 10 unique amounts
            
            # Common patterns
            patterns = {
                'common_bill_types': bill_types[:5],
                'common_amounts': recent_amounts[:5],
                'date_patterns': ['month', 'last month', 'this month', 'due date']
            }
            
            return {
                'bill_types': bill_types,
                'recent_amounts': recent_amounts,
                'patterns': patterns
            }
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {
                'bill_types': [],
                'recent_amounts': [],
                'patterns': {}
            }
    
    def _extract_corrected_text(self, llm_response: str, original_text: str) -> str:
        """Extract corrected text from LLM response."""
        # Try to find corrected text in quotes or after "corrected:" etc.
        patterns = [
            r'corrected[:\s]+"([^"]+)"',
            r'corrected[:\s]+([^\.]+)',
            r'"([^"]+)"',  # Any quoted text
            r'Did you mean[:\s]+"([^"]+)"',
            r'Did you mean[:\s]+([^?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                corrected = match.group(1).strip()
                if corrected and corrected.lower() != original_text.lower():
                    return corrected
        
        # If no pattern matches, return original
        return original_text
    
    def _generate_suggestions(
        self,
        original: str,
        corrected: str,
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Generate correction suggestions for user confirmation."""
        suggestions = []
        
        if original.lower() != corrected.lower():
            # Main suggestion
            suggestions.append(f"Did you mean: \"{corrected}\"?")
            
            # Additional context-based suggestions
            bill_types = user_context.get('bill_types', [])
            if bill_types:
                # Check if correction involves bill type
                for bill_type in bill_types[:3]:
                    if bill_type.lower() in corrected.lower():
                        suggestions.append(f"Or did you mean your {bill_type} bill?")
        
        return suggestions
    
    def confirm_correction(
        self,
        original: str,
        corrected: str,
        user_response: str
    ) -> bool:
        """
        Determine if user confirmed the correction.
        
        Args:
            original: Original STT text
            corrected: Corrected text
            user_response: User's response to correction
            
        Returns:
            bool: True if user confirmed
        """
        user_lower = user_response.lower()
        
        # Positive confirmations
        confirmations = ['yes', 'correct', 'right', 'that\'s it', 'yeah', 'yep', 'sure']
        if any(conf in user_lower for conf in confirmations):
            return True
        
        # Negative confirmations
        rejections = ['no', 'wrong', 'incorrect', 'not', 'nope']
        if any(rej in user_lower for rej in rejections):
            return False
        
        # If user repeats the corrected text, assume confirmation
        if corrected.lower() in user_lower:
            return True
        
        # Default: assume not confirmed
        return False

