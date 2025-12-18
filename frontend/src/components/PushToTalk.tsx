import { useState, useRef, useEffect } from 'react';

type RecordingState = 'idle' | 'recording' | 'processing' | 'playing';

export default function PushToTalk() {
    const [state, setState] = useState<RecordingState>('idle');
    const [error, setError] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<string>('');
    const [aiResponse, setAiResponse] = useState<string>('');

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Auto-play audio when it's set
    useEffect(() => {
        if (audioRef.current && state === 'playing') {
            audioRef.current.play().catch(err => {
                console.error('Error playing audio:', err);
                setError('Failed to play audio');
                setState('idle');
            });
        }
    }, [state]);

    const startRecording = async () => {
        try {
            setError(null);
            setTranscript('');
            setAiResponse('');

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Create MediaRecorder with webm format
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm',
            });

            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            // Collect audio chunks
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            // Handle recording stop
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());

                // Upload to backend
                await uploadAudio(audioBlob);
            };

            mediaRecorder.start();
            setState('recording');
        } catch (err) {
            console.error('Error starting recording:', err);
            setError('Failed to access microphone');
            setState('idle');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
            setState('processing');
        }
    };

    const uploadAudio = async (audioBlob: Blob) => {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const response = await fetch('/api/voice/ingest', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Upload successful:', result);

            // Display transcript and AI response
            if (result.transcript) {
                setTranscript(result.transcript);
            }
            if (result.ai_response) {
                setAiResponse(result.ai_response);
            }

            // Play TTS audio if available
            if (result.audio_base64) {
                try {
                    // Decode base64 to audio
                    const audioData = atob(result.audio_base64);
                    const audioArray = new Uint8Array(audioData.length);
                    for (let i = 0; i < audioData.length; i++) {
                        audioArray[i] = audioData.charCodeAt(i);
                    }
                    const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
                    const audioUrl = URL.createObjectURL(audioBlob);

                    // Create audio element and play
                    const audio = new Audio(audioUrl);
                    audioRef.current = audio;

                    audio.onended = () => {
                        setState('idle');
                        URL.revokeObjectURL(audioUrl);
                    };

                    audio.onerror = () => {
                        console.error('Audio playback error');
                        setState('idle');
                        URL.revokeObjectURL(audioUrl);
                    };

                    setState('playing');
                    // Audio will auto-play via useEffect
                } catch (err) {
                    console.error('Error decoding audio:', err);
                    setState('idle');
                }
            } else {
                setState('idle');
            }
        } catch (err) {
            console.error('Error uploading audio:', err);
            setError('Failed to upload audio');
            setState('idle');
        }
    };

    const handleMouseDown = () => {
        if (state === 'idle') {
            startRecording();
        }
    };

    const handleMouseUp = () => {
        if (state === 'recording') {
            stopRecording();
        }
    };

    const getButtonText = () => {
        switch (state) {
            case 'idle':
                return 'Hold to Speak';
            case 'recording':
                return 'Recording...';
            case 'processing':
                return 'Processing...';
            case 'playing':
                return '🔊 Playing...';
        }
    };

    return (
        <div>
            <button
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                disabled={state === 'processing' || state === 'playing'}
                style={{
                    padding: '16px 32px',
                    fontSize: '16px',
                    cursor: (state === 'processing' || state === 'playing') ? 'not-allowed' : 'pointer',
                    backgroundColor: state === 'recording' ? '#ef4444' : state === 'playing' ? '#10b981' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                }}
            >
                {getButtonText()}
            </button>

            {error && (
                <div style={{ color: 'red', marginTop: '8px' }}>
                    Error: {error}
                </div>
            )}

            {transcript && (
                <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>You said:</div>
                    <div style={{ fontSize: '16px', color: '#111' }}>{transcript}</div>
                </div>
            )}

            {aiResponse && (
                <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#e0f2fe', borderRadius: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#0369a1', marginBottom: '4px' }}>Jarvis:</div>
                    <div style={{ fontSize: '16px', color: '#111' }}>{aiResponse}</div>
                </div>
            )}

            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
                State: {state}
            </div>
        </div>
    );
}
