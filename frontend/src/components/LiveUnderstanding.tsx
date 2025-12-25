import { forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface LiveUnderstandingProps {
  isVisible: boolean;
  intent: string;
  entities?: any[];
}

export const LiveUnderstanding = forwardRef<HTMLDivElement, LiveUnderstandingProps>(
  ({ isVisible, intent, entities = [] }, ref) => {
    return (
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 30,
            }}
            className="glass-panel rounded-lg p-4 min-w-[280px] max-w-md"
          >
            <div className="space-y-2">
              {/* Intent */}
              <div>
                <span className="text-[10px] font-medium tracking-widest text-primary text-mono block mb-1">
                  UNDERSTANDING
                </span>
                <p className="text-sm text-foreground">
                  {intent || 'Listening...'}
                </p>
              </div>

              {/* Entities (if any) */}
              {entities && entities.length > 0 && (
                <div className="pt-2 border-t border-border/50">
                  <span className="text-[10px] font-medium tracking-widest text-secondary text-mono block mb-2">
                    DETECTED
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {entities.map((entity, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-1 rounded bg-muted/30 text-muted-foreground"
                      >
                        {entity.type}: {entity.value}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    );
  }
);

LiveUnderstanding.displayName = 'LiveUnderstanding';
