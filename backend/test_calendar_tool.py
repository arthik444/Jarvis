"""Manual test script for calendar tool"""
import asyncio
from app.services.calendar_tool import get_calendar_tool
from app.services.orchestrator import get_orchestrator


async def test_calendar_tool():
    """Test calendar tool functionality"""
    
    print("=" * 60)
    print("CALENDAR TOOL TEST")
    print("=" * 60)
    
    # Test 1: Calendar Tool directly
    print("\n1. Testing Calendar Tool directly")
    print("-" * 60)
    
    calendar_tool = get_calendar_tool()
    events = calendar_tool.get_today_events()
    
    print(f"Fetched {len(events)} events")
    if events:
        print("\nEvents:")
        for event in events:
            print(f"  - {event.get('summary')}: {event.get('start')}")
        
        print("\nSummary:")
        summary = calendar_tool.summarize_events(events)
        print(f"  {summary}")
    else:
        print("  No events found (or Calendar API not configured)")
    
    # Test 2: Through orchestrator
    print("\n\n2. Testing through Orchestrator")
    print("-" * 60)
    
    orchestrator = get_orchestrator()
    result = await orchestrator.process_transcript("Give me a summary of my day")
    
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Data Source: {result['handler_response']['data'].get('source', 'unknown')}")
    print(f"Message: {result['handler_response']['message']}")
    
    if 'events' in result['handler_response']['data']:
        events = result['handler_response']['data']['events']
        print(f"\nEvent count: {len(events)}")
    
    print("\n" + "=" * 60)
    print("✓ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_calendar_tool())
