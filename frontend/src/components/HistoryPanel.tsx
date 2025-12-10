import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getRecentHistory,
  deleteHistoryEntry,
  clearHistory,
  getHistoryStats,
  searchHistory,
} from '../services/api';
import type { HistoryEntry } from '../types';

interface HistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectEntry: (entry: HistoryEntry) => void;
}

export default function HistoryPanel({ isOpen, onClose, onSelectEntry }: HistoryPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  // Fetch history
  const historyQuery = useQuery({
    queryKey: ['history', 'recent'],
    queryFn: () => getRecentHistory(20),
    enabled: isOpen,
  });

  // Search query
  const searchResults = useQuery({
    queryKey: ['history', 'search', searchQuery],
    queryFn: () => searchHistory(searchQuery),
    enabled: isOpen && searchQuery.length > 0,
  });

  // Stats query
  const statsQuery = useQuery({
    queryKey: ['history', 'stats'],
    queryFn: getHistoryStats,
    enabled: isOpen,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteHistoryEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });

  // Clear all mutation
  const clearMutation = useMutation({
    mutationFn: clearHistory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });

  const entries = searchQuery ? searchResults.data?.entries : historyQuery.data?.entries;
  const isLoading = historyQuery.isLoading || (searchQuery && searchResults.isLoading);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-full max-w-md bg-dark-900 border-r border-dark-700 z-50 overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="sticky top-0 bg-dark-900/95 backdrop-blur-sm border-b border-dark-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-dark-100">History</h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-dark-400" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>

              {/* Search */}
              <div className="relative">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                    clipRule="evenodd"
                  />
                </svg>
                <input
                  type="text"
                  placeholder="Search history..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-dark-200 text-sm placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Stats */}
            {statsQuery.data && (
              <div className="px-6 py-4 border-b border-dark-800">
                <div className="grid grid-cols-3 gap-4">
                  <StatCard
                    label="Total"
                    value={statsQuery.data.conversions.total}
                  />
                  <StatCard
                    label="Success"
                    value={statsQuery.data.conversions.completed}
                    color="primary"
                  />
                  <StatCard
                    label="Failed"
                    value={statsQuery.data.conversions.failed}
                    color="red"
                  />
                </div>
              </div>
            )}

            {/* History list */}
            <div className="flex-1 overflow-y-auto p-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : entries && entries.length > 0 ? (
                <div className="space-y-2">
                  {entries.map((entry, index) => (
                    <motion.div
                      key={entry.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <HistoryItem
                        entry={entry}
                        onSelect={() => onSelectEntry(entry)}
                        onDelete={() => deleteMutation.mutate(entry.id)}
                        isDeleting={deleteMutation.isPending}
                      />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-800 flex items-center justify-center">
                    <svg
                      className="w-8 h-8 text-dark-500"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <p className="text-dark-400">
                    {searchQuery ? 'No results found' : 'No conversion history yet'}
                  </p>
                </div>
              )}
            </div>

            {/* Footer */}
            {entries && entries.length > 0 && (
              <div className="p-4 border-t border-dark-700">
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to clear all history?')) {
                      clearMutation.mutate();
                    }
                  }}
                  disabled={clearMutation.isPending}
                  className="w-full py-2 px-4 bg-dark-800 hover:bg-red-500/20 hover:text-red-400 text-dark-400 text-sm rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  {clearMutation.isPending ? (
                    <div className="w-4 h-4 border-2 border-dark-400 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                      <path
                        fillRule="evenodd"
                        d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  Clear All History
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// Stat Card Component
interface StatCardProps {
  label: string;
  value: number;
  color?: 'primary' | 'red';
}

function StatCard({ label, value, color }: StatCardProps) {
  const colorClasses = {
    primary: 'text-primary-400',
    red: 'text-red-400',
  };

  return (
    <div className="bg-dark-800/50 rounded-lg p-3 text-center">
      <p className={`text-xl font-bold ${color ? colorClasses[color] : 'text-dark-200'}`}>
        {value}
      </p>
      <p className="text-xs text-dark-500">{label}</p>
    </div>
  );
}

// History Item Component
interface HistoryItemProps {
  entry: HistoryEntry;
  onSelect: () => void;
  onDelete: () => void;
  isDeleting: boolean;
}

function HistoryItem({ entry, onSelect, onDelete, isDeleting }: HistoryItemProps) {
  const statusColors: Record<string, string> = {
    completed: 'bg-primary-500',
    failed: 'bg-red-500',
    pending: 'bg-yellow-500',
    processing: 'bg-blue-500',
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="group bg-dark-800/50 hover:bg-dark-800 rounded-xl p-4 transition-colors duration-200">
      <div className="flex items-start gap-3">
        {/* Status indicator */}
        <div className={`w-2 h-2 mt-2 rounded-full ${statusColors[entry.status] || 'bg-dark-500'}`} />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <button
            onClick={onSelect}
            className="w-full text-left"
            disabled={entry.status !== 'completed'}
          >
            <p className="font-medium text-dark-200 truncate">{entry.original_filename}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-dark-500">{formatDate(entry.created_at)}</span>
              {entry.file_size && (
                <>
                  <span className="text-dark-600">•</span>
                  <span className="text-xs text-dark-500">{formatFileSize(entry.file_size)}</span>
                </>
              )}
              {entry.input_format && (
                <>
                  <span className="text-dark-600">•</span>
                  <span className="text-xs text-dark-500 uppercase">{entry.input_format}</span>
                </>
              )}
            </div>
            {entry.error_message && (
              <p className="text-xs text-red-400 mt-1 truncate">{entry.error_message}</p>
            )}
          </button>
        </div>

        {/* Delete button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          disabled={isDeleting}
          className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-dark-700 rounded-lg transition-all duration-200"
        >
          {isDeleting ? (
            <div className="w-4 h-4 border-2 border-dark-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-4 h-4 text-dark-400 hover:text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

