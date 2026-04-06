import { motion } from 'framer-motion';
import { systemCapabilities } from '../data/metrics';

const StatCard = ({ title, value, description, color, index }: {
  title: string;
  value: string;
  description: string;
  color: string;
  index: number;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.6 }}
      whileHover={{ scale: 1.05, y: -5 }}
      className="glass-morphism rounded-xl p-6 hover:bg-white/20 transition-all duration-300"
    >
      <div className="text-center">
        <div className={`text-4xl font-bold ${color} text-glow mb-2`}>
          {value}
        </div>
        <div className="text-white font-semibold mb-2">
          {title}
        </div>
        <div className="text-gray-300 text-sm">
          {description}
        </div>
      </div>
    </motion.div>
  );
};

export const StatsGrid = () => {
  return (
    <div className="py-20 px-8">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-6xl mx-auto"
      >
        <h2 className="text-4xl font-bold text-center mb-4 text-glow">
          Framework Performance
        </h2>
        <p className="text-gray-300 text-center mb-12 text-lg">
          Comprehensive testing results from aggressive 10-test validation suite
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systemCapabilities.map((stat, index) => (
            <StatCard
              key={stat.title}
              {...stat}
              index={index}
            />
          ))}
        </div>
      </motion.div>
    </div>
  );
};