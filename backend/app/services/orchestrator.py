"""Orchestrator service for intent routing and handler coordination"""
import logging
from functools import lru_cache
from typing import Any, Dict

from app.services.gemini import get_gemini_service

logger = logging.getLogger(__name__)


class OrchestratorService:
    """Orchestrates intent classification and routes to appropriate handlers"""

    def __init__(self):
        """Initialize orchestrator service"""
        self.gemini_service = get_gemini_service()
        logger.info("✓ Orchestrator service initialized")

    async def process_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Process transcript by classifying intent and routing to handler.
        
        Args:
            transcript: User's transcribed message
            
        Returns:
            Dict containing:
                - transcript: Original user input
                - intent: Classified intent
                - confidence: Classification confidence score
                - handler_response: Handler's structured response
        """
        try:
            # Classify intent using existing Gemini classifier
            intent_result = await self.gemini_service.classify_intent(transcript)
            intent = intent_result.get("intent", "GENERAL_CHAT")
            confidence = intent_result.get("confidence", 0.5)
            
            logger.info(f"Orchestrator: Intent={intent}, Confidence={confidence}")
            
            # Route to appropriate handler based on intent
            handler_response = await self._route_to_handler(intent, transcript, confidence)
            
            return {
                "transcript": transcript,
                "intent": intent,
                "confidence": confidence,
                "handler_response": handler_response,
            }
            
        except Exception as e:
            logger.error(f"Orchestrator processing error: {e}")
            # Fallback to general chat on error
            return {
                "transcript": transcript,
                "intent": "GENERAL_CHAT",
                "confidence": 0.0,
                "handler_response": await self._handle_general_chat(transcript),
            }

    async def process_transcript_stream(self, transcript: str):
        """
        Process transcript with streaming support for faster responses.
        
        Classifies intent and either:
        - Streams from Gemini for GENERAL_CHAT (conversational responses)
        - Returns immediate handler response for structured intents (weather, tasks, etc.)
        
        Args:
            transcript: User's transcribed message
            
        Yields:
            For GENERAL_CHAT: Text chunks as they stream from Gemini
            For other intents: Single handler message (no streaming needed)
            
        Returns (via header metadata):
            Intent and confidence for client-side handling
        """
        try:
            # Classify intent using existing Gemini classifier
            intent_result = await self.gemini_service.classify_intent(transcript)
            intent = intent_result.get("intent", "GENERAL_CHAT")
            confidence = intent_result.get("confidence", 0.5)
            
            logger.info(f"Orchestrator Streaming: Intent={intent}, Confidence={confidence}")
            
            # Apply confidence threshold
            confidence_threshold = 0.7
            if confidence < confidence_threshold:
                logger.info(f"Low confidence ({confidence}), fallback to GENERAL_CHAT")
                intent = "GENERAL_CHAT"
            
            # For GENERAL_CHAT: stream from Gemini for natural conversation
            if intent == "GENERAL_CHAT":
                logger.info("Streaming from Gemini for GENERAL_CHAT")
                async for chunk in self.gemini_service.generate_response_stream(transcript):
                    yield chunk, intent, confidence
            else:
                # For structured intents: return immediate response (no streaming needed)
                logger.info(f"Immediate response for {intent} (structured data)")
                handler_response = await self._route_to_handler(intent, transcript, confidence)
                # Yield the complete message at once
                yield handler_response["message"], intent, confidence
                
        except Exception as e:
            logger.error(f"Orchestrator streaming error: {e}")
            # Fallback to generic response
            yield "I'm having trouble processing that right now.", "GENERAL_CHAT", 0.0

    async def _route_to_handler(
        self, intent: str, transcript: str, confidence: float
    ) -> Dict[str, Any]:
        """
        Route to appropriate handler based on intent.
        
        Args:
            intent: Classified intent
            transcript: User's message
            confidence: Classification confidence
            
        Returns:
            Handler's structured response
        """
        # Fallback to general chat for low confidence
        confidence_threshold = 0.7
        if confidence < confidence_threshold:
            logger.info(f"Low confidence ({confidence}), fallback to GENERAL_CHAT")
            intent = "GENERAL_CHAT"
        
        # Route to handlers
        if intent == "GET_WEATHER":
            return await self._handle_get_weather(transcript)
        elif intent == "ADD_TASK":
            return await self._handle_add_task(transcript)
        elif intent == "DAILY_SUMMARY":
            return await self._handle_daily_summary(transcript)
        elif intent == "LEARN":
            return await self._handle_learn(transcript)
        else:
            # Default to general chat
            return await self._handle_general_chat(transcript)

    # ========== Handler Functions (Mock Data) ==========

    async def _handle_get_weather(self, transcript: str) -> Dict[str, Any]:
        """
        Handle weather queries with mock data.
        
        Args:
            transcript: User's weather query
            
        Returns:
            Mock weather data response
        """
        logger.info("Handler: GET_WEATHER")
        return {
            "type": "weather",
            "data": {
                "location": "San Francisco",
                "temperature": 72,
                "unit": "fahrenheit",
                "condition": "Sunny",
                "humidity": 65,
                "wind_speed": 8,
            },
            "message": "It's currently 72°F and sunny in San Francisco with light winds.",
        }

    async def _handle_add_task(self, transcript: str) -> Dict[str, Any]:
        """
        Handle task creation with mock confirmation.
        
        Args:
            transcript: User's task creation request
            
        Returns:
            Mock task creation confirmation
        """
        logger.info("Handler: ADD_TASK")
        # Extract task from transcript (simple mock - just use the transcript)
        task_text = transcript.replace("add", "").replace("to my todo list", "").strip()
        
        return {
            "type": "task",
            "data": {
                "task_id": "mock_task_123",
                "task_text": task_text,
                "created_at": "2025-12-19T14:48:00Z",
                "status": "pending",
            },
            "message": f"I've added '{task_text}' to your task list.",
        }

    async def _handle_daily_summary(self, transcript: str) -> Dict[str, Any]:
        """
        Handle daily summary requests with mock data.
        
        Args:
            transcript: User's summary request
            
        Returns:
            Mock daily summary
        """
        logger.info("Handler: DAILY_SUMMARY")
        return {
            "type": "summary",
            "data": {
                "date": "2025-12-19",
                "tasks_completed": 5,
                "tasks_pending": 3,
                "meetings_attended": 2,
                "highlights": [
                    "Completed project proposal",
                    "Team standup at 10 AM",
                    "Code review session",
                ],
            },
            "message": "Today you completed 5 tasks and attended 2 meetings. Great progress!",
        }

    async def _handle_learn(self, transcript: str) -> Dict[str, Any]:
        """
        Handle educational queries with mock response.
        
        Args:
            transcript: User's learning question
            
        Returns:
            Mock educational response
        """
        logger.info("Handler: LEARN")
        return {
            "type": "educational",
            "data": {
                "topic": "General Knowledge",
                "summary": "This is a mock educational response.",
                "key_points": [
                    "Educational content would go here",
                    "Retrieved from knowledge base",
                    "Structured for easy understanding",
                ],
            },
            "message": "Here's what I found about your question. This is a mock response that would contain educational content.",
        }

    async def _handle_general_chat(self, transcript: str) -> Dict[str, Any]:
        """
        Handle general conversation with mock response.
        
        Args:
            transcript: User's conversational message
            
        Returns:
            Mock conversational response
        """
        logger.info("Handler: GENERAL_CHAT")
        return {
            "type": "conversation",
            "data": {
                "response_type": "casual",
                "context": "general_chat",
            },
            "message": "I'm here to help! This is a mock conversational response. How can I assist you today?",
        }


@lru_cache
def get_orchestrator() -> OrchestratorService:
    """
    Get cached orchestrator service instance.
    
    Returns:
        Configured OrchestratorService instance
    """
    return OrchestratorService()
