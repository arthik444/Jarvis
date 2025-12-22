"""Manual test script for orchestrator service"""
import asyncio
from app.services.orchestrator import get_orchestrator


async def test_orchestrator():
    """Test orchestrator with different transcript examples"""
    
    orchestrator = get_orchestrator()
    
    # Test cases for each intent type
    test_cases = [
        "What's the weather like today?",
        "Add buy milk to my todo list",
        "Give me a summary of my day",
        "How does photosynthesis work?",
        "Hello, how are you?",
    ]
    
    print("=" * 60)
    print("ORCHESTRATOR MANUAL TEST")
    print("=" * 60)
    
    for i, transcript in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{transcript}'")
        print("-" * 60)
        
        result = await orchestrator.process_transcript(transcript)
        
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Handler Type: {result['handler_response']['type']}")
        print(f"Message: {result['handler_response']['message']}")
        print(f"Data: {result['handler_response']['data']}")
    
    print("\n" + "=" * 60)
    print("✓ All test cases completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
