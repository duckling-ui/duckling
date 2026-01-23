import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";

interface ConversionProgressProps {
  progress: number;
  message: string;
  filename?: string;
}

export default function ConversionProgress({
  progress,
  message,
  filename,
}: ConversionProgressProps) {
  const { t } = useTranslation();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-xl mx-auto"
    >
      <div className="glass rounded-2xl p-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative">
            <motion.div
              className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <svg
                className="w-6 h-6 text-primary-400 animate-spin-slow"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </motion.div>
            {/* Pulsing ring */}
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-primary-500/30"
              animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-dark-100">
              {t("progress.title")}
            </h3>
            {filename && (
              <p className="text-sm text-dark-400 truncate max-w-xs">
                {filename}
              </p>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-dark-300">{message}</span>
            <span className="text-sm font-mono text-primary-400">
              {progress}%
            </span>
          </div>
          <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full progress-bar rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Status steps */}
        <div className="space-y-2">
          <StatusStep
            label={t("progress.uploadComplete")}
            isComplete={progress >= 10}
            isActive={progress < 10}
          />
          <StatusStep
            label={t("progress.analyzing")}
            isComplete={progress >= 30}
            isActive={progress >= 10 && progress < 30}
          />
          <StatusStep
            label={t("progress.extracting")}
            isComplete={progress >= 70}
            isActive={progress >= 30 && progress < 70}
          />
          <StatusStep
            label={t("progress.generating")}
            isComplete={progress >= 90}
            isActive={progress >= 70 && progress < 90}
          />
          <StatusStep
            label={t("progress.finalizing")}
            isComplete={progress >= 100}
            isActive={progress >= 90 && progress < 100}
          />
        </div>
      </div>
    </motion.div>
  );
}

interface StatusStepProps {
  label: string;
  isComplete: boolean;
  isActive: boolean;
}

function StatusStep({ label, isComplete, isActive }: StatusStepProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`
          w-5 h-5 rounded-full flex items-center justify-center transition-all duration-300
          ${
            isComplete
              ? "bg-primary-500"
              : isActive
              ? "bg-primary-500/30 ring-2 ring-primary-500/50"
              : "bg-dark-700"
          }
        `}
      >
        {isComplete ? (
          <svg
            className="w-3 h-3 text-dark-950"
            viewBox="0 0 12 12"
            fill="none"
          >
            <path
              d="M2 6l3 3 5-6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : isActive ? (
          <motion.div
            className="w-2 h-2 rounded-full bg-primary-400"
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        ) : null}
      </div>
      <span
        className={`
          text-sm transition-colors duration-300
          ${
            isComplete
              ? "text-dark-200"
              : isActive
              ? "text-primary-400"
              : "text-dark-500"
          }
        `}
      >
        {label}
      </span>
    </div>
  );
}
