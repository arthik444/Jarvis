import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { Calendar, CheckCircle, Cloud, Brain, MessageSquare, X } from 'lucide-react';

export type CardType = 'calendar' | 'task' | 'weather' | 'memory' | 'info';

interface AcknowledgmentCardProps {
  type: CardType;
  title: string;
  subtitle?: string;
  onDismiss?: () => void;
  index?: number;
}

const cardConfig = {
  calendar: {
    icon: Calendar,
    accentColor: 'hsl(185, 85%, 50%)',
    label: 'CALENDAR',
  },
  task: {
    icon: CheckCircle,
    accentColor: 'hsl(160, 70%, 45%)',
    label: 'TASK',
  },
  weather: {
    icon: Cloud,
    accentColor: 'hsl(200, 60%, 50%)',
    label: 'WEATHER',
  },
  memory: {
    icon: Brain,
    accentColor: 'hsl(265, 60%, 55%)',
    label: 'MEMORY',
  },
  info: {
    icon: MessageSquare,
    accentColor: 'hsl(215, 50%, 55%)',
    label: 'INFO',
  },
};

export const AcknowledgmentCard = forwardRef<HTMLDivElement, AcknowledgmentCardProps>(
  ({ type, title, subtitle, onDismiss, index = 0 }, ref) => {
    const config = cardConfig[type];
    const Icon = config.icon;

    return (
      <motion.div
        ref={ref}
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 100, opacity: 0 }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 30,
          delay: index * 0.1,
        }}
        className="glass-panel rounded-lg p-4 w-72 cursor-pointer hover:border-primary/40 transition-colors relative"
        onClick={onDismiss}
        style={{
          borderLeft: `3px solid ${config.accentColor}`,
        }}
      >
        <div className="flex items-start gap-3">
          <div
            className="p-2 rounded-md flex-shrink-0"
            style={{
              background: `${config.accentColor}15`,
            }}
          >
            <Icon
              size={16}
              style={{ color: config.accentColor }}
            />
          </div>
          <div className="flex-1 min-w-0 pr-6">
            <span
              className="text-[10px] font-medium tracking-widest text-mono block mb-1"
              style={{ color: config.accentColor }}
            >
              {config.label}
            </span>
            <p className="text-sm font-medium text-foreground line-clamp-2">
              {title}
            </p>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-0.5 truncate">
                {subtitle}
              </p>
            )}
          </div>
          <button
            className="absolute top-2 right-2 p-1 rounded hover:bg-muted/30 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onDismiss?.();
            }}
          >
            <X size={14} className="text-muted-foreground" />
          </button>
        </div>
      </motion.div>
    );
  }
);

AcknowledgmentCard.displayName = 'AcknowledgmentCard';
