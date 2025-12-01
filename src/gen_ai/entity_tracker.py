"""
Entity Tracking Service.
Tracks mentioned entities (bills, dates, amounts) in conversations.
"""
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.gen_ai.llm_service import LLMService

logger = logging.getLogger(__name__)


class EntityTracker:
    """Service for tracking entities in conversations."""
    
    def __init__(self):
        """Initialize entity tracker."""
        self.llm_service = LLMService()
    
    def extract_entities(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: User input text
            context: Previous conversation context
            
        Returns:
            dict: Extracted entities
        """
        try:
            entities = {
                'bills': [],
                'dates': [],
                'amounts': [],
                'references': []
            }
            
            # Extract using patterns
            entities['bills'] = self._extract_bill_types(text)
            entities['dates'] = self._extract_dates(text)
            entities['amounts'] = self._extract_amounts(text)
            entities['references'] = self._extract_references(text, context)
            
            # Use LLM for advanced extraction
            llm_entities = self._extract_with_llm(text, context)
            
            # Merge results
            entities = self._merge_entities(entities, llm_entities)
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {'bills': [], 'dates': [], 'amounts': [], 'references': []}
    
    def _extract_bill_types(self, text: str) -> List[str]:
        """Extract bill types from text."""
        bill_types = ['electric', 'electricity', 'utility', 'water', 'gas', 'internet', 'phone', 'credit card']
        found = []
        
        text_lower = text.lower()
        for bill_type in bill_types:
            if bill_type in text_lower:
                found.append(bill_type)
        
        return found
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        
        # Patterns for dates
        patterns = [
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # MM/DD/YYYY
            r'(last|this|next)\s+month',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'(\d{1,2})(st|nd|rd|th)',
            r'today|yesterday|tomorrow'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append(match.group(0))
        
        return dates
    
    def _extract_amounts(self, text: str) -> List[float]:
        """Extract dollar amounts from text."""
        amounts = []
        
        # Pattern for dollar amounts
        pattern = r'\$?(\d+(?:\.\d{2})?)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            try:
                amount = float(match.group(1))
                if 0 < amount < 100000:  # Reasonable range
                    amounts.append(amount)
            except ValueError:
                continue
        
        return amounts
    
    def _extract_references(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Extract references (pronouns, "that one", etc.)."""
        references = []
        
        reference_patterns = [
            r'\bthat\s+one\b',
            r'\bthis\s+one\b',
            r'\bit\b',
            r'\bthat\b',
            r'\bthis\b',
            r'\bthe\s+month\s+before\b',
            r'\bthe\s+one\s+before\b',
            r'\blast\s+one\b'
        ]
        
        for pattern in reference_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                references.append(pattern)
        
        return references
    
    def _extract_with_llm(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract entities using LLM."""
        system_prompt = """You are an entity extraction system. Extract entities from user text related to bill payments.
Extract: bill types, dates, amounts, and references to previous entities."""

        context_str = ""
        if context:
            context_str = f"""
Previous context:
- Bills mentioned: {context.get('bills', [])}
- Dates mentioned: {context.get('dates', [])}
- Amounts mentioned: {context.get('amounts', [])}
"""

        prompt = f"""
{context_str}
Extract entities from this text: "{text}"

Return JSON with:
- bills: list of bill types mentioned
- dates: list of dates mentioned
- amounts: list of dollar amounts mentioned
- references: list of references (pronouns, "that one", etc.)
"""

        response = self.llm_service.generate_response(prompt, system_prompt)
        
        # Try to parse JSON from response
        import json
        import re
        
        text_response = response.get('text', '')
        json_match = re.search(r'\{[^}]+\}', text_response, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {'bills': [], 'dates': [], 'amounts': [], 'references': []}
    
    def _merge_entities(
        self,
        pattern_entities: Dict[str, Any],
        llm_entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge entities from pattern matching and LLM."""
        merged = {
            'bills': list(set(pattern_entities.get('bills', []) + llm_entities.get('bills', []))),
            'dates': list(set(pattern_entities.get('dates', []) + llm_entities.get('dates', []))),
            'amounts': list(set(pattern_entities.get('amounts', []) + llm_entities.get('amounts', []))),
            'references': list(set(pattern_entities.get('references', []) + llm_entities.get('references', [])))
        }
        
        return merged
    
    def resolve_reference(
        self,
        reference: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a reference to a previous entity.
        
        Args:
            reference: Reference text ("that one", "it", etc.)
            context: Conversation context with previous entities
            
        Returns:
            dict: Resolved entity or None
        """
        # Get last mentioned entities from context
        turns = context.get('turns', [])
        if not turns:
            return None
        
        # Look for entities in recent turns
        for turn in reversed(turns[-5:]):  # Check last 5 turns
            answer = turn.get('answer', '')
            
            # Try to find bill, date, or amount in answer
            if 'bill' in answer.lower():
                # Extract bill info
                return {
                    'type': 'bill',
                    'text': answer
                }
            elif any(date_word in answer.lower() for date_word in ['month', 'date', 'day']):
                return {
                    'type': 'date',
                    'text': answer
                }
            elif '$' in answer or 'amount' in answer.lower():
                return {
                    'type': 'amount',
                    'text': answer
                }
        
        return None

