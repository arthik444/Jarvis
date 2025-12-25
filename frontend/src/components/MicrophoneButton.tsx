import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';

interface MicrophoneButtonProps {
  isActive: boolean;
  onPressStart: () => void;
  onPressEnd: () => void;
}

export const MicrophoneButton = forwardRef<HTMLButtonElement, MicrophoneButtonProps>(
  ({ isActive, onPressStart, onPressEnd }, ref) => {
    return (
      <motion.button
        ref={ref}
        onMouseDown={onPressStart}
        onMouseUp={onPressEnd}
        onMouseLeave={onPressEnd}
        onTouchStart={onPressStart}
        onTouchEnd={onPressEnd}
        className="relative flex items-center justify-center w-16 h-16 rounded-full glass-panel cursor-pointer select-none"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
          borderWidth: 2,
          borderColor: isActive ? 'hsl(185, 85%, 50%)' : 'hsl(220, 20%, 18%)',
        }}
      >
        {/* Glow effect when active */}
        {isActive && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'radial-gradient(circle, hsl(185, 85%, 50% / 0.3) 0%, transparent 70%)',
                filter: 'blur(10px)',
              }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 0.8, 0.5],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                boxShadow: '0 0 30px hsl(185, 85%, 50% / 0.5), 0 0 60px hsl(185, 85%, 50% / 0.3)',
              }}
              animate={{
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </>
        )}

        {/* Microphone icon */}
        <motion.div
          style={{
            color: isActive ? 'hsl(185, 85%, 50%)' : 'hsl(210, 20%, 98%)',
          }}
        >
          <Mic size={24} />
        </motion.div>
      </motion.button>
    );
  }
);

MicrophoneButton.displayName = 'MicrophoneButton';
