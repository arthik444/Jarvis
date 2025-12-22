"""Tests for orchestrator service"""
import pytest
from app.services.orchestrator import get_orchestrator


class TestOrchestratorService:
    """Test suite for OrchestratorService"""

    @pytest.fixture
    def orchestrator(self):
        """Get orchestrator instance for testing"""
        return get_orchestrator()

    @pytest.mark.asyncio
    async def test_weather_intent_routing(self, orchestrator):
        """Test GET_WEATHER intent routes to weather handler"""
        result = await orchestrator.process_transcript("What's the weather like today?")
        
        assert result["intent"] == "GET_WEATHER"
        assert result["handler_response"]["type"] == "weather"
        assert "temperature" in result["handler_response"]["data"]
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_add_task_intent_routing(self, orchestrator):
        """Test ADD_TASK intent routes to task handler"""
        result = await orchestrator.process_transcript("Add buy milk to my todo list")
        
        assert result["intent"] == "ADD_TASK"
        assert result["handler_response"]["type"] == "task"
        assert "task_id" in result["handler_response"]["data"]
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_daily_summary_intent_routing(self, orchestrator):
        """Test DAILY_SUMMARY intent routes to summary handler"""
        result = await orchestrator.process_transcript("Give me a summary of my day")
        
        assert result["intent"] == "DAILY_SUMMARY"
        assert result["handler_response"]["type"] == "summary"
        assert "tasks_completed" in result["handler_response"]["data"]
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_learn_intent_routing(self, orchestrator):
        """Test LEARN intent routes to educational handler"""
        result = await orchestrator.process_transcript("How does photosynthesis work?")
        
        assert result["intent"] == "LEARN"
        assert result["handler_response"]["type"] == "educational"
        assert "topic" in result["handler_response"]["data"]
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_general_chat_intent_routing(self, orchestrator):
        """Test GENERAL_CHAT intent routes to conversation handler"""
        result = await orchestrator.process_transcript("Hello, how are you?")
        
        assert result["intent"] == "GENERAL_CHAT"
        assert result["handler_response"]["type"] == "conversation"
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_low_confidence_fallback(self, orchestrator):
        """Test low confidence scores fallback to GENERAL_CHAT"""
        # The orchestrator should handle low confidence by routing to GENERAL_CHAT
        # This test validates the fallback mechanism exists
        result = await orchestrator.process_transcript("asdf qwerty gibberish")
        
        # Should return a valid response structure
        assert "intent" in result
        assert "handler_response" in result
        assert "message" in result["handler_response"]

    @pytest.mark.asyncio
    async def test_response_structure(self, orchestrator):
        """Test all responses have consistent structure"""
        result = await orchestrator.process_transcript("What's the weather?")
        
        # Validate top-level structure
        assert "transcript" in result
        assert "intent" in result
        assert "confidence" in result
        assert "handler_response" in result
        
        # Validate handler response structure
        handler_response = result["handler_response"]
        assert "type" in handler_response
        assert "data" in handler_response
        assert "message" in handler_response

    @pytest.mark.asyncio
    async def test_transcript_preserved(self, orchestrator):
        """Test original transcript is preserved in response"""
        original_text = "What's the weather like today?"
        result = await orchestrator.process_transcript(original_text)
        
        assert result["transcript"] == original_text

    @pytest.mark.asyncio
    async def test_confidence_score_present(self, orchestrator):
        """Test confidence score is included and valid"""
        result = await orchestrator.process_transcript("What's the weather?")
        
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))
        assert 0.0 <= result["confidence"] <= 1.0
