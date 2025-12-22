"""Quick test script to debug TTS functionality"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_tts():
    """Test TTS service directly"""
    try:
        from app.services.tts import get_tts_service
        
        print("1. Getting TTS service...")
        tts_service = get_tts_service()
        print(f"✓ TTS service initialized with voice: {tts_service.voice_id}")
        
        print("\n2. Testing text_to_speech_base64...")
        test_text = "Hello, this is a test message."
        audio_base64 = tts_service.text_to_speech_base64(test_text)
        
        if audio_base64:
            print(f"✓ Generated audio (base64 length: {len(audio_base64)} chars)")
            print(f"   First 50 chars: {audio_base64[:50]}")
            return True
        else:
            print("✗ No audio generated (returned None or empty)")
            return False
            
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_orchestrator_tts():
    """Test full flow: transcript -> orchestrator -> TTS"""
    try:
        from app.services.orchestrator import get_orchestrator
        from app.services.tts import get_tts_service
        
        print("\n3. Testing orchestrator + TTS flow...")
        orchestrator = get_orchestrator()
        tts_service = get_tts_service()
        
        # Test with a simple transcript
        transcript = "What's the weather like?"
        print(f"   Transcript: '{transcript}'")
        
        result = await orchestrator.process_transcript(transcript)
        message = result["handler_response"]["message"]
        print(f"   AI Response: '{message}'")
        
        print("\n4. Converting response to speech...")
        audio_base64 = tts_service.text_to_speech_base64(message)
        
        if audio_base64:
            print(f"✓ Generated audio (base64 length: {len(audio_base64)} chars)")
            return True
        else:
            print("✗ No audio generated")
            return False
            
    except Exception as e:
        print(f"✗ Orchestrator+TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TTS Debug Test")
    print("=" * 60)
    
    asyncio.run(test_tts())
    asyncio.run(test_orchestrator_tts())
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
