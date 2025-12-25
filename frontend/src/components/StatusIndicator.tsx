import { motion } from 'framer-motion';
import type { OrbState } from './JarvisOrb';

interface StatusIndicatorProps {
  state: OrbState;
}

const stateConfig = {
  idle: {
    label: 'IDLE',
    color: 'hsl(210, 20%, 65%)',
  },
  listening: {
    label: 'LISTENING',
    color: 'hsl(185, 85%, 50%)',
  },
  thinking: {
    label: 'THINKING',
    color: 'hsl(265, 60%, 55%)',
  },
  speaking: {
    label: 'SPEAKING',
    color: 'hsl(160, 70%, 45%)',
  },
};

export function StatusIndicator({ state }: StatusIndicatorProps) {
  const config = stateConfig[state];

  return (
    <div className="flex items-center gap-2">
      <motion.div
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: config.color }}
        animate={{
          opacity: state === 'idle' ? 0.5 : [0.5, 1, 0.5],
          scale: state === 'idle' ? 1 : [1, 1.2, 1],
        }}
        transition={{
          duration: state === 'idle' ? 0 : 1.5,
          repeat: state === 'idle' ? 0 : Infinity,
          ease: 'easeInOut',
        }}
      />
      <span
        className="text-[10px] font-medium tracking-widest text-mono"
        style={{ color: config.color }}
      >
        {config.label}
      </span>
    </div>
  );
}
