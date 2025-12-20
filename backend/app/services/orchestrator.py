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
        
        # Handler mapping
        handlers = {
            "GET_WEATHER": self._handle_get_weather,
            "ADD_TASK": self._handle_add_task,
            "DAILY_SUMMARY": self._handle_daily_summary,
            "DELETE_CALENDAR_EVENT": self._handle_delete_calendar_event,
            "LEARN": self._handle_learn,
            "GENERAL_CHAT": self._handle_general_chat,
        }
        
        # Get handler or default to general chat
        handler = handlers.get(intent, self._handle_general_chat)
        return await handler(transcript)

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
        Handle daily summary requests with real calendar data.
        
        Args:
            transcript: User's summary request
            
        Returns:
            Daily summary with calendar events
        """
        logger.info("Handler: DAILY_SUMMARY")
        
        try:
            # Try to get real calendar events
            from app.services.calendar_tool import get_calendar_tool
            from datetime import datetime
            
            calendar_tool = get_calendar_tool()
            events = calendar_tool.get_today_events()
            
            if events:
                # Use real calendar data
                summary_message = calendar_tool.summarize_events(events)
                
                return {
                    "type": "summary",
                    "data": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "events": events,
                        "event_count": len(events),
                        "source": "google_calendar"
                    },
                    "message": summary_message,
                }
            else:
                # Fallback to mock data if no events
                logger.info("No calendar events found, using mock summary")
                return self._get_mock_daily_summary()
                
        except Exception as e:
            # Fallback to mock data on any error
            logger.warning(f"Calendar integration failed, using mock data: {e}")
            return self._get_mock_daily_summary()
    
    def _get_mock_daily_summary(self) -> Dict[str, Any]:
        """Return mock daily summary data"""
        from datetime import datetime
        return {
            "type": "summary",
            "data": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tasks_completed": 5,
                "tasks_pending": 3,
                "meetings_attended": 2,
                "highlights": [
                    "Completed project proposal",
                    "Team standup at 10 AM",
                    "Code review session",
                ],
                "source": "mock_data"
            },
            "message": "Today you completed 5 tasks and attended 2 meetings. Great progress!",
        }

    async def _handle_delete_calendar_event(self, transcript: str) -> Dict[str, Any]:
        """
        Handle calendar event deletion requests.
        
        Args:
            transcript: User's delete request
            
        Returns:
            Deletion confirmation or error
        """
        logger.info("Handler: DELETE_CALENDAR_EVENT")
        
        try:
            from app.services.calendar_tool import get_calendar_tool
            
            calendar_tool = get_calendar_tool()
            events = calendar_tool.get_today_events()
            
            if not events:
                return {
                    "type": "calendar_delete",
                    "data": {"error": "No events found"},
                    "message": "You don't have any events today to delete."
                }
            
            # Find matching event by name in transcript
            transcript_lower = transcript.lower()
            matching_event = None
            
            for event in events:
                event_summary = event.get('summary', '').lower()
                if event_summary and event_summary in transcript_lower:
                    matching_event = event
                    break
            
            if not matching_event:
                event_names = [e.get('summary') for e in events]
                return {
                    "type": "calendar_delete",
                    "data": {"available_events": event_names},
                    "message": f"I couldn't find that event. You have: {', '.join(event_names)}."
                }
            
            # Delete the event
            result = calendar_tool.delete_event(matching_event['id'])
            
            if "error" in result:
                return {
                    "type": "calendar_delete",
                    "data": result,
                    "message": f"Failed to delete: {result['error']}"
                }
            
            return {
                "type": "calendar_delete",
                "data": {"deleted_event": matching_event['summary']},
                "message": f"I've deleted '{matching_event['summary']}' from your calendar."
            }
            
        except Exception as e:
            logger.error(f"Calendar deletion failed: {e}")
            return {
                "type": "calendar_delete",
                "data": {"error": str(e)},
                "message": "I had trouble deleting that event. Please try again."
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
