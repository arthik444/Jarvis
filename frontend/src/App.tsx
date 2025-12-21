import { useState } from 'react';
import PushToTalk from './components/PushToTalk';
import ChatInput from './components/ChatInput';

type InterfaceMode = 'voice' | 'text';

function App() {
    const [mode, setMode] = useState<InterfaceMode>('voice');

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            minHeight: '100vh',
            backgroundColor: '#f9fafb',
        }}>
            <div style={{
                width: '100%',
                maxWidth: '800px',
                padding: '20px',
            }}>
                <h1 style={{ textAlign: 'center', marginBottom: '24px' }}>Mini Jarvis</h1>

                {/* Mode Tabs */}
                <div style={{
                    display: 'flex',
                    gap: '8px',
                    marginBottom: '20px',
                    borderBottom: '2px solid #e5e7eb',
                }}>
                    <button
                        onClick={() => setMode('voice')}
                        style={{
                            flex: 1,
                            padding: '12px 20px',
                            fontSize: '15px',
                            fontWeight: '500',
                            border: 'none',
                            borderBottom: mode === 'voice' ? '3px solid #3b82f6' : '3px solid transparent',
                            backgroundColor: mode === 'voice' ? '#eff6ff' : 'transparent',
                            color: mode === 'voice' ? '#3b82f6' : '#6b7280',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                        }}
                    >
                        🎤 Voice
                    </button>
                    <button
                        onClick={() => setMode('text')}
                        style={{
                            flex: 1,
                            padding: '12px 20px',
                            fontSize: '15px',
                            fontWeight: '500',
                            border: 'none',
                            borderBottom: mode === 'text' ? '3px solid #3b82f6' : '3px solid transparent',
                            backgroundColor: mode === 'text' ? '#eff6ff' : 'transparent',
                            color: mode === 'text' ? '#3b82f6' : '#6b7280',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                        }}
                    >
                        💬 Text Chat
                    </button>
                </div>

                {/* Interface Container */}
                <div style={{
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                    overflow: 'hidden',
                    minHeight: mode === 'text' ? '500px' : 'auto',
                }}>
                    {mode === 'voice' ? (
                        <div style={{ padding: '24px' }}>
                            <PushToTalk />
                        </div>
                    ) : (
                        <div style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
                            <ChatInput />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
