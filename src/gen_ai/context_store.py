"""
Context Storage Service.
Stores and retrieves conversation context for multi-turn dialogues.
"""
import logging
import json
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.config import Config

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis library not available")


class ContextStore:
    """Service for storing and retrieving conversation context."""
    
    def __init__(self):
        """Initialize context storage service."""
        self.provider = Config.CONTEXT_STORAGE_PROVIDER
        self.context_table = Config.CONTEXT_TABLE
        self.max_turns = Config.DIALOGUE_CONTEXT_RETENTION_TURNS
        self.max_minutes = Config.DIALOGUE_CONTEXT_RETENTION_MINUTES
        
        # Initialize storage backend
        if self.provider == 'redis' and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=Config.REDIS_HOST,
                    port=Config.REDIS_PORT,
                    db=Config.REDIS_DB,
                    decode_responses=True
                )
                self.redis_client.ping()  # Test connection
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {str(e)}, falling back to DynamoDB")
                self.provider = 'dynamodb'
                self.redis_client = None
        else:
            self.redis_client = None
        
        # Initialize DynamoDB
        if self.provider == 'dynamodb':
            try:
                self.dynamodb = boto3.client(
                    'dynamodb',
                    region_name=Config.AWS_REGION,
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                logger.error(f"Could not initialize DynamoDB: {str(e)}")
                self.dynamodb = None
    
    def save_context(
        self,
        session_id: str,
        user_id: str,
        turn: Dict[str, Any],
        conversation_state: Optional[str] = None
    ) -> bool:
        """
        Save conversation turn to context.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            turn: Conversation turn (question, answer, timestamp)
            conversation_state: Current conversation state
            
        Returns:
            bool: True if successful
        """
        try:
            if self.provider == 'redis' and self.redis_client:
                return self._save_to_redis(session_id, user_id, turn, conversation_state)
            else:
                return self._save_to_dynamodb(session_id, user_id, turn, conversation_state)
        except Exception as e:
            logger.error(f"Error saving context: {str(e)}")
            return False
    
    def get_context(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        max_turns: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get conversation context.
        
        Args:
            session_id: Session identifier
            user_id: User identifier (optional)
            max_turns: Maximum number of turns to retrieve
            
        Returns:
            dict: Context with conversation history
        """
        try:
            max_turns = max_turns or self.max_turns
            
            if self.provider == 'redis' and self.redis_client:
                return self._get_from_redis(session_id, user_id, max_turns)
            else:
                return self._get_from_dynamodb(session_id, user_id, max_turns)
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return {'turns': [], 'entities': {}, 'state': 'IDLE'}
    
    def clear_context(self, session_id: str) -> bool:
        """Clear context for a session."""
        try:
            if self.provider == 'redis' and self.redis_client:
                self.redis_client.delete(f"context:{session_id}")
                return True
            else:
                # Mark as expired in DynamoDB
                return self._expire_in_dynamodb(session_id)
        except Exception as e:
            logger.error(f"Error clearing context: {str(e)}")
            return False
    
    def _save_to_redis(
        self,
        session_id: str,
        user_id: str,
        turn: Dict[str, Any],
        conversation_state: Optional[str]
    ) -> bool:
        """Save context to Redis."""
        key = f"context:{session_id}"
        
        # Get existing context
        existing = self.redis_client.get(key)
        if existing:
            context = json.loads(existing)
        else:
            context = {
                'session_id': session_id,
                'user_id': user_id,
                'turns': [],
                'entities': {},
                'state': 'IDLE',
                'created_at': datetime.utcnow().isoformat()
            }
        
        # Add new turn
        context['turns'].append({
            'question': turn.get('question', ''),
            'answer': turn.get('answer', ''),
            'timestamp': turn.get('timestamp', datetime.utcnow().isoformat())
        })
        
        # Keep only last max_turns
        context['turns'] = context['turns'][-self.max_turns:]
        
        # Update state
        if conversation_state:
            context['state'] = conversation_state
        
        # Update entities if provided
        if 'entities' in turn:
            context['entities'].update(turn['entities'])
        
        context['updated_at'] = datetime.utcnow().isoformat()
        
        # Save to Redis with expiration
        self.redis_client.setex(
            key,
            self.max_minutes * 60,  # Convert to seconds
            json.dumps(context)
        )
        
        return True
    
    def _get_from_redis(
        self,
        session_id: str,
        user_id: Optional[str],
        max_turns: int
    ) -> Dict[str, Any]:
        """Get context from Redis."""
        key = f"context:{session_id}"
        data = self.redis_client.get(key)
        
        if not data:
            return {'turns': [], 'entities': {}, 'state': 'IDLE'}
        
        context = json.loads(data)
        
        # Limit turns
        context['turns'] = context['turns'][-max_turns:]
        
        return context
    
    def _save_to_dynamodb(
        self,
        session_id: str,
        user_id: str,
        turn: Dict[str, Any],
        conversation_state: Optional[str]
    ) -> bool:
        """Save context to DynamoDB."""
        if not self.dynamodb:
            return False
        
        try:
            # Get existing context
            existing = self.get_context(session_id, user_id)
            
            # Add new turn
            turns = existing.get('turns', [])
            turns.append({
                'question': turn.get('question', ''),
                'answer': turn.get('answer', ''),
                'timestamp': turn.get('timestamp', datetime.utcnow().isoformat())
            })
            
            # Keep only last max_turns
            turns = turns[-self.max_turns:]
            
            # Update entities
            entities = existing.get('entities', {})
            if 'entities' in turn:
                entities.update(turn['entities'])
            
            # Prepare item
            item = {
                'session_id': {'S': session_id},
                'user_id': {'S': user_id},
                'turns': {'L': [self._marshal_turn(t) for t in turns]},
                'entities': {'M': {k: {'S': str(v)} for k, v in entities.items()}},
                'state': {'S': conversation_state or existing.get('state', 'IDLE')},
                'updated_at': {'S': datetime.utcnow().isoformat()},
                'ttl': {'N': str(int((datetime.utcnow() + timedelta(minutes=self.max_minutes)).timestamp()))}
            }
            
            # Put item
            self.dynamodb.put_item(
                TableName=self.context_table,
                Item=item
            )
            
            return True
        except Exception as e:
            logger.error(f"Error saving to DynamoDB: {str(e)}")
            return False
    
    def _get_from_dynamodb(
        self,
        session_id: str,
        user_id: Optional[str],
        max_turns: int
    ) -> Dict[str, Any]:
        """Get context from DynamoDB."""
        if not self.dynamodb:
            return {'turns': [], 'entities': {}, 'state': 'IDLE'}
        
        try:
            response = self.dynamodb.get_item(
                TableName=self.context_table,
                Key={'session_id': {'S': session_id}}
            )
            
            if 'Item' not in response:
                return {'turns': [], 'entities': {}, 'state': 'IDLE'}
            
            item = response['Item']
            
            # Unmarshal turns
            turns = []
            if 'turns' in item:
                for turn_item in item['turns'].get('L', []):
                    turns.append(self._unmarshal_turn(turn_item))
            
            # Unmarshal entities
            entities = {}
            if 'entities' in item:
                for k, v in item['entities'].get('M', {}).items():
                    entities[k] = v.get('S', '')
            
            return {
                'turns': turns[-max_turns:],
                'entities': entities,
                'state': item.get('state', {}).get('S', 'IDLE')
            }
        except Exception as e:
            logger.error(f"Error getting from DynamoDB: {str(e)}")
            return {'turns': [], 'entities': {}, 'state': 'IDLE'}
    
    def _marshal_turn(self, turn: Dict[str, Any]) -> Dict[str, Any]:
        """Marshal turn for DynamoDB."""
        return {
            'M': {
                'question': {'S': turn.get('question', '')},
                'answer': {'S': turn.get('answer', '')},
                'timestamp': {'S': turn.get('timestamp', '')}
            }
        }
    
    def _unmarshal_turn(self, turn_item: Dict[str, Any]) -> Dict[str, Any]:
        """Unmarshal turn from DynamoDB."""
        turn_m = turn_item.get('M', {})
        return {
            'question': turn_m.get('question', {}).get('S', ''),
            'answer': turn_m.get('answer', {}).get('S', ''),
            'timestamp': turn_m.get('timestamp', {}).get('S', '')
        }
    
    def _expire_in_dynamodb(self, session_id: str) -> bool:
        """Mark context as expired in DynamoDB."""
        if not self.dynamodb:
            return False
        
        try:
            self.dynamodb.update_item(
                TableName=self.context_table,
                Key={'session_id': {'S': session_id}},
                UpdateExpression='SET ttl = :ttl',
                ExpressionAttributeValues={
                    ':ttl': {'N': str(int(datetime.utcnow().timestamp()))}
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error expiring context: {str(e)}")
            return False

