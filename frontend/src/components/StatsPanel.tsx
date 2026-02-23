/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-present David G. Simmons
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getHistoryStats } from "../services/api";

interface StatsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
}

interface InfoTooltipProps {
  text: string;
  className?: string;
}

function InfoTooltip({ text, className = "" }: InfoTooltipProps) {
  return (
    <span
      className={`group relative inline-flex cursor-help ${className}`}
      role="img"
      aria-label={text}
    >
      <span className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-dark-500 bg-dark-700 text-[10px] font-medium text-dark-400">
        i
      </span>
      <span className="pointer-events-none absolute left-1/2 top-full z-10 mt-1 w-48 -translate-x-1/2 rounded bg-dark-700 px-2 py-1.5 text-left text-xs leading-snug text-dark-200 opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
        {text}
      </span>
    </span>
  );
}

interface StatCardProps {
  label: string;
  value: number | string;
  color?: "primary" | "red";
  tooltip?: string;
}

function StatCard({ label, value, color, tooltip }: StatCardProps) {
  const colorClasses = {
    primary: "text-primary-400",
    red: "text-red-400",
  };

  return (
    <div className="bg-dark-800/50 rounded-lg p-3 text-center">
      <p
        className={`text-xl font-bold ${
          color ? colorClasses[color] : "text-dark-200"
        }`}
      >
        {value}
      </p>
      <p className="text-xs text-dark-500 flex items-center justify-center gap-1">
        {label}
        {tooltip && <InfoTooltip text={tooltip} />}
      </p>
    </div>
  );
}

interface BreakdownBarProps {
  label: string;
  count: number;
  max: number;
}

function BreakdownBar({ label, count, max }: BreakdownBarProps) {
  const widthPercent = max > 0 ? (count / max) * 100 : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-dark-300">{label}</span>
        <span className="text-dark-400">{count}</span>
      </div>
      <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary-500/70 rounded-full transition-all duration-300"
          style={{ width: `${widthPercent}%` }}
        />
      </div>
    </div>
  );
}

interface BreakdownSectionProps {
  title: string;
  data: Record<string, number> | undefined;
  emptyMessage: string;
}

function BreakdownSection({
  title,
  data,
  emptyMessage,
}: BreakdownSectionProps) {
  const entries = data ? Object.entries(data) : [];
  const maxCount = entries.length
    ? Math.max(...entries.map(([, v]) => v))
    : 0;

  if (entries.length === 0) {
    return (
      <section>
        <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-3">
          {title}
        </h3>
        <p className="text-sm text-dark-500">{emptyMessage}</p>
      </section>
    );
  }

  return (
    <section>
      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-3">
        {title}
      </h3>
      <div className="space-y-3">
        {entries.map(([key, count]) => (
          <BreakdownBar
            key={key}
            label={key}
            count={count}
            max={maxCount}
          />
        ))}
      </div>
    </section>
  );
}

export default function StatsPanel({ isOpen, onClose }: StatsPanelProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const statsQuery = useQuery({
    queryKey: ["history", "stats"],
    queryFn: getHistoryStats,
    enabled: isOpen,
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["history", "stats"] });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-xl bg-dark-900 border-l border-dark-700 z-50 overflow-y-auto"
          >
            <div className="sticky top-0 bg-dark-900/95 backdrop-blur-sm border-b border-dark-700 p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-dark-100">
                {t("statsPanel.title")}
              </h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleRefresh}
                  disabled={statsQuery.isLoading}
                  className="p-2 hover:bg-dark-800 rounded-lg transition-colors disabled:opacity-50"
                  title={t("statsPanel.refresh")}
                >
                  <svg
                    className={`w-5 h-5 text-dark-400 ${statsQuery.isLoading ? "animate-spin" : ""}`}
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885 6.994 6.994 0 00-5.716-2.566V5a1 1 0 011-1h2zm10 14a1 1 0 01-1 1H5a1 1 0 01-1-1v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 011.885 6.994 6.994 0 005.716 2.566V15a1 1 0 011 1h2z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
                >
                  <svg
                    className="w-5 h-5 text-dark-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>

            {statsQuery.isLoading ? (
              <div className="p-12 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : statsQuery.error ? (
              <div className="p-6">
                <p className="text-red-400">
                  {t("statsPanel.error") || "Failed to load statistics"}
                </p>
              </div>
            ) : statsQuery.data ? (
              <div className="p-6 space-y-8">
                {/* Overview */}
                <section>
                  <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4">
                    {t("statsPanel.overview")}
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <StatCard
                      label={t("historyPanel.total")}
                      value={statsQuery.data.conversions.total}
                    />
                    <StatCard
                      label={t("historyPanel.success")}
                      value={statsQuery.data.conversions.completed}
                      color="primary"
                    />
                    <StatCard
                      label={t("historyPanel.failed")}
                      value={statsQuery.data.conversions.failed}
                      color="red"
                    />
                    <StatCard
                      label={t("statsPanel.successRate")}
                      value={`${statsQuery.data.conversions.success_rate}%`}
                      tooltip={t("statsPanel.tooltipSuccessRate")}
                    />
                    {statsQuery.data.conversions.avg_processing_seconds != null && (
                      <StatCard
                        label={t("historyPanel.avgProcessingTime")}
                        value={formatDuration(
                          statsQuery.data.conversions.avg_processing_seconds
                        )}
                        tooltip={t("statsPanel.tooltipAvgProcessingTime")}
                      />
                    )}
                    {statsQuery.data.conversions.avg_pages_per_second != null && (
                      <StatCard
                        label={t("statsPanel.avgPagesPerSec")}
                        value={statsQuery.data.conversions.avg_pages_per_second.toFixed(2)}
                        tooltip={t("statsPanel.tooltipAvgPagesPerSec")}
                      />
                    )}
                    {statsQuery.data.conversions.avg_pages_per_second_per_cpu != null && (
                      <StatCard
                        label={t("statsPanel.avgPagesPerSecPerCpu")}
                        value={statsQuery.data.conversions.avg_pages_per_second_per_cpu.toFixed(2)}
                        tooltip={t("statsPanel.tooltipAvgPagesPerSecPerCpu")}
                      />
                    )}
                    {statsQuery.data.queue_depth != null && (
                      <StatCard
                        label={t("historyPanel.queueDepth")}
                        value={statsQuery.data.queue_depth}
                        tooltip={t("statsPanel.tooltipQueueDepth")}
                      />
                    )}
                  </div>
                </section>

                {/* System */}
                {statsQuery.data.conversions.system &&
                  (statsQuery.data.conversions.system.cpu_count != null ||
                    statsQuery.data.conversions.system.hardware_type ||
                    statsQuery.data.conversions.system.cpu_usage_current != null) && (
                    <section>
                      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4">
                        {t("statsPanel.system")}
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        {statsQuery.data.conversions.system.hardware_type && (
                          <div className="bg-dark-800/50 rounded-lg p-4">
                            <p className="text-sm text-dark-500 flex items-center gap-1">
                              {t("statsPanel.hardwareType")}
                              <InfoTooltip text={t("statsPanel.tooltipHardwareType")} />
                            </p>
                            <p className="text-lg font-bold text-dark-200 capitalize">
                              {statsQuery.data.conversions.system.hardware_type}
                            </p>
                          </div>
                        )}
                        {statsQuery.data.conversions.system.cpu_count != null && (
                          <div className="bg-dark-800/50 rounded-lg p-4">
                            <p className="text-sm text-dark-500 flex items-center gap-1">
                              {t("statsPanel.cpuCount")}
                              <InfoTooltip text={t("statsPanel.tooltipCpuCount")} />
                            </p>
                            <p className="text-lg font-bold text-dark-200">
                              {statsQuery.data.conversions.system.cpu_count}
                            </p>
                          </div>
                        )}
                        {statsQuery.data.conversions.system.cpu_usage_current != null && (
                          <div className="bg-dark-800/50 rounded-lg p-4">
                            <p className="text-sm text-dark-500 flex items-center gap-1">
                              {t("statsPanel.currentCpuUsage")}
                              <InfoTooltip text={t("statsPanel.tooltipCurrentCpuUsage")} />
                            </p>
                            <p className="text-lg font-bold text-dark-200">
                              {statsQuery.data.conversions.system.cpu_usage_current.toFixed(1)}%
                            </p>
                          </div>
                        )}
                        {statsQuery.data.conversions.system.gpu_name && (
                          <div className="col-span-2 bg-dark-800/50 rounded-lg p-4">
                            <p className="text-sm text-dark-500 flex items-center gap-1">
                              {t("statsPanel.gpuInfo")}
                              <InfoTooltip text={t("statsPanel.tooltipGpuInfo")} />
                            </p>
                            <p className="text-lg font-bold text-dark-200">
                              {statsQuery.data.conversions.system.gpu_name}
                              {statsQuery.data.conversions.system.gpu_memory_mb != null &&
                                ` (${statsQuery.data.conversions.system.gpu_memory_mb} MB)`}
                            </p>
                          </div>
                        )}
                      </div>
                    </section>
                  )}

                {/* Conversion time distribution */}
                {statsQuery.data.conversions.conversion_time_distribution && (
                  <section>
                    <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                      {t("statsPanel.conversionTimeDistribution")}
                      <InfoTooltip text={t("statsPanel.tooltipConversionTimeDistribution")} />
                    </h3>
                    <div className="grid grid-cols-3 gap-4">
                      <StatCard
                        label={t("statsPanel.conversionTimeP50")}
                        value={formatDuration(
                          statsQuery.data.conversions.conversion_time_distribution.p50
                        )}
                        tooltip={t("statsPanel.tooltipConversionTimeP50")}
                      />
                      <StatCard
                        label={t("statsPanel.conversionTimeP95")}
                        value={formatDuration(
                          statsQuery.data.conversions.conversion_time_distribution.p95
                        )}
                        tooltip={t("statsPanel.tooltipConversionTimeP95")}
                      />
                      <StatCard
                        label={t("statsPanel.conversionTimeP99")}
                        value={formatDuration(
                          statsQuery.data.conversions.conversion_time_distribution.p99
                        )}
                        tooltip={t("statsPanel.tooltipConversionTimeP99")}
                      />
                    </div>
                  </section>
                )}

                {/* Pages/sec over time chart */}
                {statsQuery.data.conversions.pages_per_second_over_time &&
                  statsQuery.data.conversions.pages_per_second_over_time.length > 0 && (
                    <section>
                      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        {t("statsPanel.pagesPerSecOverTime")}
                        <InfoTooltip text={t("statsPanel.tooltipPagesPerSecOverTime")} />
                      </h3>
                      <div className="h-48">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={statsQuery.data.conversions.pages_per_second_over_time.map(
                              (p) => ({
                                ...p,
                                time: p.created_at
                                  ? new Date(p.created_at).toLocaleTimeString()
                                  : p.job_id.slice(0, 8),
                              })
                            )}
                            margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" className="stroke-dark-700" />
                            <XAxis
                              dataKey="time"
                              tick={{ fill: "#9ca3af", fontSize: 10 }}
                              stroke="#6b7280"
                            />
                            <YAxis
                              tick={{ fill: "#9ca3af", fontSize: 10 }}
                              stroke="#6b7280"
                            />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: "#1f2937",
                                border: "1px solid #374151",
                                borderRadius: "0.5rem",
                              }}
                              labelStyle={{ color: "#9ca3af" }}
                              formatter={(value: number | undefined) => [value != null ? value.toFixed(2) : "—", "pages/sec"]}
                            />
                            <Line
                              type="monotone"
                              dataKey="pages_per_sec"
                              stroke="#6366f1"
                              strokeWidth={2}
                              dot={{ fill: "#6366f1", r: 3 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </section>
                  )}

                {/* Performance by hardware */}
                {statsQuery.data.conversions.by_hardware &&
                  Object.keys(statsQuery.data.conversions.by_hardware).length > 0 && (
                    <section>
                      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        {t("statsPanel.performanceByHardware")}
                        <InfoTooltip text={t("statsPanel.tooltipPerformanceByHardware")} />
                      </h3>
                      <div className="space-y-3">
                        {Object.entries(
                          statsQuery.data.conversions.by_hardware
                        ).map(([hw, data]) => (
                          <div
                            key={hw}
                            className="bg-dark-800/50 rounded-lg p-4"
                          >
                            <p className="text-sm font-medium text-dark-300 capitalize mb-2">
                              {hw}
                            </p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                              <span className="text-dark-500">
                                {data.count} conversions
                              </span>
                              {data.avg_pages_per_second != null && (
                                <span>
                                  {data.avg_pages_per_second.toFixed(2)} pages/s
                                </span>
                              )}
                              {data.avg_processing_seconds != null && (
                                <span>
                                  {formatDuration(data.avg_processing_seconds)}{" "}
                                  avg
                                </span>
                              )}
                              {data.conversion_time_p50 != null && (
                                <span className="inline-flex items-center gap-1">
                                  p50: {formatDuration(data.conversion_time_p50)}
                                  <InfoTooltip text={t("statsPanel.tooltipP50")} className="ml-0.5" />
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                {/* Performance by OCR backend */}
                {statsQuery.data.conversions.by_ocr_backend &&
                  Object.keys(statsQuery.data.conversions.by_ocr_backend)
                    .length > 0 && (
                    <section>
                      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        {t("statsPanel.performanceByOcrBackend")}
                        <InfoTooltip text={t("statsPanel.tooltipPerformanceByOcrBackend")} />
                      </h3>
                      <div className="space-y-3">
                        {Object.entries(
                          statsQuery.data.conversions.by_ocr_backend
                        ).map(([backend, data]) => (
                          <div
                            key={backend}
                            className="bg-dark-800/50 rounded-lg p-4"
                          >
                            <p className="text-sm font-medium text-dark-300 mb-2">
                              {backend}
                            </p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                              <span className="text-dark-500">
                                {data.count} conversions
                              </span>
                              {data.avg_pages_per_second != null && (
                                <span>
                                  {data.avg_pages_per_second.toFixed(2)} pages/s
                                </span>
                              )}
                              {data.avg_processing_seconds != null && (
                                <span>
                                  {formatDuration(data.avg_processing_seconds)}{" "}
                                  avg
                                </span>
                              )}
                              {data.conversion_time_p50 != null && (
                                <span className="inline-flex items-center gap-1">
                                  p50: {formatDuration(data.conversion_time_p50)}
                                  <InfoTooltip text={t("statsPanel.tooltipP50")} className="ml-0.5" />
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                {/* Performance by image classifier */}
                {statsQuery.data.conversions.by_images_classify &&
                  Object.keys(statsQuery.data.conversions.by_images_classify)
                    .length > 0 && (
                    <section>
                      <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        {t("statsPanel.performanceByImageClassifier")}
                        <InfoTooltip text={t("statsPanel.tooltipPerformanceByImageClassifier")} />
                      </h3>
                      <div className="space-y-3">
                        {Object.entries(
                          statsQuery.data.conversions.by_images_classify
                        ).map(([enabled, data]) => (
                          <div
                            key={enabled}
                            className="bg-dark-800/50 rounded-lg p-4"
                          >
                            <p className="text-sm font-medium text-dark-300 mb-2">
                              {enabled === "true"
                                ? t("statsPanel.imageClassifierOn")
                                : t("statsPanel.imageClassifierOff")}
                            </p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                              <span className="text-dark-500">
                                {data.count} conversions
                              </span>
                              {data.avg_pages_per_second != null && (
                                <span>
                                  {data.avg_pages_per_second.toFixed(2)} pages/s
                                </span>
                              )}
                              {data.avg_processing_seconds != null && (
                                <span>
                                  {formatDuration(data.avg_processing_seconds)}{" "}
                                  avg
                                </span>
                              )}
                              {data.conversion_time_p50 != null && (
                                <span className="inline-flex items-center gap-1">
                                  p50: {formatDuration(data.conversion_time_p50)}
                                  <InfoTooltip text={t("statsPanel.tooltipP50")} className="ml-0.5" />
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                {/* Storage */}
                <section>
                  <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-4">
                    {t("statsPanel.storage")}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-dark-800/50 rounded-lg p-4">
                      <p className="text-sm text-dark-500">
                        {t("statsPanel.uploads")}
                      </p>
                      <p className="text-lg font-bold text-dark-200">
                        {statsQuery.data.storage.uploads.count} files (
                        {statsQuery.data.storage.uploads.size_mb} MB)
                      </p>
                    </div>
                    <div className="bg-dark-800/50 rounded-lg p-4">
                      <p className="text-sm text-dark-500">
                        {t("statsPanel.outputs")}
                      </p>
                      <p className="text-lg font-bold text-dark-200">
                        {statsQuery.data.storage.outputs.count} outputs (
                        {statsQuery.data.storage.outputs.size_mb} MB)
                      </p>
                    </div>
                    <div className="col-span-2 bg-dark-800/50 rounded-lg p-4">
                      <p className="text-sm text-dark-500">
                        {t("statsPanel.totalStorage")}
                      </p>
                      <p className="text-lg font-bold text-dark-200">
                        {statsQuery.data.storage.total_size_mb} MB
                      </p>
                    </div>
                  </div>
                </section>

                {/* Breakdowns */}
                <BreakdownSection
                  title={t("statsPanel.inputFormats")}
                  data={statsQuery.data.conversions.format_breakdown}
                  emptyMessage={t("statsPanel.noData")}
                />

                <BreakdownSection
                  title={t("statsPanel.ocrBackends")}
                  data={statsQuery.data.conversions.ocr_backend_breakdown}
                  emptyMessage={t("statsPanel.noData")}
                />

                <BreakdownSection
                  title={t("statsPanel.outputFormats")}
                  data={statsQuery.data.conversions.output_format_breakdown}
                  emptyMessage={t("statsPanel.noData")}
                />

                <BreakdownSection
                  title={t("statsPanel.performanceDevices")}
                  data={
                    statsQuery.data.conversions.performance_device_breakdown
                  }
                  emptyMessage={t("statsPanel.noData")}
                />

                <BreakdownSection
                  title={t("statsPanel.sourceTypes")}
                  data={statsQuery.data.conversions.source_type_breakdown}
                  emptyMessage={t("statsPanel.noData")}
                />

                {statsQuery.data.conversions.failed > 0 && (
                  <BreakdownSection
                    title={t("statsPanel.errors")}
                    data={
                      statsQuery.data.conversions.error_category_breakdown
                    }
                    emptyMessage={t("statsPanel.noData")}
                  />
                )}

                {/* Chunking */}
                {statsQuery.data.conversions.chunking_enabled_count != null && (
                  <section>
                    <h3 className="text-sm font-semibold text-dark-400 uppercase tracking-wider mb-3">
                      {t("statsPanel.chunkingEnabled")}
                    </h3>
                    <p className="text-dark-200">
                      {statsQuery.data.conversions.chunking_enabled_count}{" "}
                      {t("statsPanel.conversionsWithChunking")}
                    </p>
                  </section>
                )}
              </div>
            ) : null}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
