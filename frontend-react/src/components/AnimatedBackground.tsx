import { motion } from 'framer-motion';

const Crystal = ({ delay, size, x, y }: {
  delay: number;
  size: number;
  x: number;
  y: number;
}) => {
  return (
    <motion.div
      className="absolute crystal-glow"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        width: `${size}px`,
        height: `${size}px`,
      }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{
        opacity: 0.7,
        scale: 1,
        rotate: [0, 360],
        y: [-20, 20, -20],
      }}
      transition={{
        duration: 6 + delay,
        repeat: Infinity,
        ease: 'easeInOut',
        rotate: {
          duration: 20 + delay * 2,
          repeat: Infinity,
          ease: 'linear',
        },
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        className="drop-shadow-2xl"
      >
        <defs>
          <linearGradient id={`crystal-gradient-${x}-${y}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#14b8a6" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.4" />
          </linearGradient>
        </defs>
        <polygon
          points="50,10 90,35 70,85 30,85 10,35"
          fill={`url(#crystal-gradient-${x}-${y})`}
          stroke="rgba(255,255,255,0.3)"
          strokeWidth="1"
        />
      </svg>
    </motion.div>
  );
};

const MolecularBond = ({ x1, y1, x2, y2, delay }: {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  delay: number;
}) => {
  return (
    <motion.div
      className="absolute"
      style={{
        left: 0,
        top: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    >
      <svg
        width="100%"
        height="100%"
        className="absolute inset-0"
      >
        <motion.line
          x1={`${x1}%`}
          y1={`${y1}%`}
          x2={`${x2}%`}
          y2={`${y2}%`}
          stroke="rgba(167, 139, 250, 0.3)"
          strokeWidth="2"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{
            duration: 2,
            delay,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut',
          }}
        />
      </svg>
    </motion.div>
  );
};

export const AnimatedBackground = () => {
  const crystals = [
    { delay: 0, size: 40, x: 10, y: 20 },
    { delay: 1, size: 30, x: 85, y: 10 },
    { delay: 2, size: 35, x: 20, y: 70 },
    { delay: 1.5, size: 25, x: 90, y: 80 },
    { delay: 0.5, size: 20, x: 50, y: 15 },
    { delay: 2.5, size: 30, x: 75, y: 50 },
    { delay: 3, size: 25, x: 15, y: 45 },
  ];

  const bonds = [
    { x1: 20, y1: 30, x2: 35, y2: 45, delay: 0 },
    { x1: 60, y1: 20, x2: 80, y2: 40, delay: 1 },
    { x1: 15, y1: 60, x2: 40, y2: 80, delay: 2 },
    { x1: 70, y1: 70, x2: 85, y2: 85, delay: 1.5 },
  ];

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {crystals.map((crystal, index) => (
        <Crystal key={index} {...crystal} />
      ))}
      {bonds.map((bond, index) => (
        <MolecularBond key={index} {...bond} />
      ))}
      
      {/* Hexagonal Grid Background */}
      <div className="absolute inset-0 opacity-10">
        <svg width="100%" height="100%" className="absolute inset-0">
          <defs>
            <pattern id="hexagons" width="50" height="43.4" patternUnits="userSpaceOnUse">
              <path
                d="M25 0L50 14.4V28.9L25 43.4L0 28.9V14.4L25 0Z"
                fill="none"
                stroke="rgba(167, 139, 250, 0.3)"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hexagons)" />
        </svg>
      </div>
    </div>
  );
};