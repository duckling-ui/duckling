import { motion, AnimatePresence } from "framer-motion";
import { useAllSettings } from "../hooks/useSettings";
import { useTranslation } from "react-i18next";

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { t } = useTranslation();
  const {
    ocr,
    tables,
    images,
    enrichment,
    output,
    performance,
    chunking,
    isLoading,
    settings,
  } = useAllSettings();

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
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-lg bg-dark-900 border-l border-dark-700 z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-dark-900/95 backdrop-blur-sm border-b border-dark-700 p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-dark-100">
                {t("settingsPanel.title")}
              </h2>
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

            {isLoading ? (
              <div className="p-6 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <div className="p-6 space-y-6">
                {/* OCR Settings */}
                <SettingsSection title={t("settings.sections.ocr")} icon="eye">
                  <ToggleSetting
                    label={t("settings.ocr.enable.label")}
                    description={t("settings.ocr.enable.description")}
                    checked={ocr.ocr?.enabled ?? true}
                    onChange={(enabled) => ocr.updateOcr({ enabled })}
                    disabled={ocr.isUpdating}
                  />
                  <div className="space-y-2">
                    <SelectSetting
                      label={t("settings.ocr.backend.label")}
                      description={t("settings.ocr.backend.description")}
                      value={ocr.ocr?.backend ?? "easyocr"}
                      options={ocr.availableBackends.map((b) => {
                        const status = ocr.backendsStatus.find(
                          (s) => s.id === b.id
                        );
                        let statusLabel = "";
                        if (status?.available) {
                          statusLabel = t(
                            "settings.ocr.backendStatus.availableSuffix"
                          );
                        } else if (status?.requires_system_install) {
                          statusLabel = t(
                            "settings.ocr.backendStatus.needsSystemInstallSuffix"
                          );
                        } else if (status?.installed) {
                          statusLabel = t(
                            "settings.ocr.backendStatus.notConfiguredSuffix"
                          );
                        } else {
                          statusLabel = t(
                            "settings.ocr.backendStatus.notInstalledSuffix"
                          );
                        }
                        return {
                          value: b.id,
                          label: `${b.name}${statusLabel}`,
                        };
                      })}
                      onChange={(backend) => ocr.updateOcr({ backend }, true)}
                      disabled={
                        ocr.isUpdating || ocr.isInstalling || !ocr.ocr?.enabled
                      }
                    />

                    {/* Backend status indicator */}
                    {ocr.ocr?.backend &&
                      (() => {
                        const status = ocr.backendsStatus.find(
                          (s) => s.id === ocr.ocr?.backend
                        );
                        if (!status) return null;

                        if (status.available) {
                          return (
                            <div className="flex items-center gap-2 text-xs text-green-400">
                              <svg
                                className="w-3.5 h-3.5"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                  clipRule="evenodd"
                                />
                              </svg>
                              {t("settings.ocr.status.installedReady", {
                                name: status.name,
                              })}
                            </div>
                          );
                        }

                        // Show system install requirement BEFORE the pip-installable check
                        if (status.requires_system_install) {
                          return (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2 text-xs text-orange-400">
                                <svg
                                  className="w-3.5 h-3.5"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                                {t("settings.ocr.status.requiresManual")}
                              </div>
                              <div className="p-3 bg-dark-800/50 rounded-lg border border-dark-700 space-y-2">
                                <p className="text-xs text-dark-300">
                                  {t("settings.ocr.status.cannotInstallInUi", {
                                    name: status.name,
                                  })}
                                </p>
                                {status.id === "tesseract" && (
                                  <div className="space-y-1 text-xs text-dark-400 font-mono">
                                    <p>
                                      <span className="text-dark-500">
                                        # macOS:
                                      </span>{" "}
                                      brew install tesseract
                                    </p>
                                    <p>
                                      <span className="text-dark-500">
                                        # Ubuntu:
                                      </span>{" "}
                                      apt-get install tesseract-ocr
                                    </p>
                                    <p>
                                      <span className="text-dark-500">
                                        # Windows:
                                      </span>{" "}
                                      {t(
                                        "settings.ocr.status.downloadFromGithub"
                                      )}
                                    </p>
                                  </div>
                                )}
                                {status.note &&
                                  !status.id.includes("tesseract") && (
                                    <p className="text-xs text-dark-400">
                                      {status.note}
                                    </p>
                                  )}
                              </div>
                            </div>
                          );
                        }

                        if (!status.installed && status.pip_installable) {
                          return (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2 text-xs text-yellow-400">
                                <svg
                                  className="w-3.5 h-3.5"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                                {t("settings.ocr.status.notInstalled", {
                                  name: status.name,
                                })}
                              </div>
                              <button
                                onClick={() => ocr.installBackend(status.id)}
                                disabled={ocr.isInstalling}
                                className="px-3 py-1.5 bg-primary-500 hover:bg-primary-600 disabled:bg-dark-600 text-dark-950 text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
                              >
                                {ocr.isInstalling ? (
                                  <>
                                    <div className="w-3 h-3 border-2 border-dark-950 border-t-transparent rounded-full animate-spin" />
                                    {t("settings.actions.installing")}
                                  </>
                                ) : (
                                  <>
                                    <svg
                                      className="w-3.5 h-3.5"
                                      viewBox="0 0 20 20"
                                      fill="currentColor"
                                    >
                                      <path
                                        fillRule="evenodd"
                                        d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                                        clipRule="evenodd"
                                      />
                                    </svg>
                                    {t("settings.actions.install", {
                                      name: status.name,
                                    })}
                                  </>
                                )}
                              </button>
                              {status.note && (
                                <p className="text-xs text-dark-500">
                                  {status.note}
                                </p>
                              )}
                            </div>
                          );
                        }

                        if (status.error) {
                          return (
                            <div className="text-xs text-red-400">
                              Error: {status.error}
                            </div>
                          );
                        }

                        return null;
                      })()}

                    {/* Install error message */}
                    {ocr.installError && (
                      <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
                        {ocr.installError}
                        <button
                          onClick={() => ocr.clearInstallError()}
                          className="ml-2 underline hover:no-underline"
                        >
                          {t("settings.actions.dismiss")}
                        </button>
                      </div>
                    )}
                  </div>
                  <SelectSetting
                    label={t("settings.ocr.language.label")}
                    description={t("settings.ocr.language.description")}
                    value={ocr.ocr?.language ?? "en"}
                    options={ocr.availableLanguages.map((lang) => ({
                      value: lang.code,
                      label: lang.name,
                    }))}
                    onChange={(language) => ocr.updateOcr({ language })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                  <ToggleSetting
                    label={t("settings.ocr.forceFullPage.label")}
                    description={t("settings.ocr.forceFullPage.description")}
                    checked={ocr.ocr?.force_full_page_ocr ?? false}
                    onChange={(force_full_page_ocr) =>
                      ocr.updateOcr({ force_full_page_ocr })
                    }
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                  <ToggleSetting
                    label={t("settings.ocr.useGpu.label")}
                    description={t("settings.ocr.useGpu.description")}
                    checked={ocr.ocr?.use_gpu ?? false}
                    onChange={(use_gpu) => ocr.updateOcr({ use_gpu })}
                    disabled={
                      ocr.isUpdating ||
                      !ocr.ocr?.enabled ||
                      ocr.ocr?.backend !== "easyocr"
                    }
                  />
                  <SliderSetting
                    label={t("settings.ocr.confidence.label")}
                    description={t("settings.ocr.confidence.description")}
                    value={ocr.ocr?.confidence_threshold ?? 0.5}
                    min={0}
                    max={1}
                    step={0.05}
                    onChange={(confidence_threshold) =>
                      ocr.updateOcr({ confidence_threshold })
                    }
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                </SettingsSection>

                {/* Table Settings */}
                <SettingsSection
                  title={t("settings.sections.tables")}
                  icon="table"
                >
                  <ToggleSetting
                    label={t("settings.tables.enable.label")}
                    description={t("settings.tables.enable.description")}
                    checked={tables.tables?.enabled ?? true}
                    onChange={(enabled) => tables.updateTables({ enabled })}
                    disabled={tables.isUpdating}
                  />
                  <SelectSetting
                    label={t("settings.tables.mode.label")}
                    description={t("settings.tables.mode.description")}
                    value={tables.tables?.mode ?? "accurate"}
                    options={tables.availableModes.map((m) => ({
                      value: m.id,
                      label: m.name,
                    }))}
                    onChange={(mode) => tables.updateTables({ mode })}
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                  <ToggleSetting
                    label={t("settings.tables.structure.label")}
                    description={t("settings.tables.structure.description")}
                    checked={tables.tables?.structure_extraction ?? true}
                    onChange={(structure_extraction) =>
                      tables.updateTables({ structure_extraction })
                    }
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                  <ToggleSetting
                    label={t("settings.tables.cellMatching.label")}
                    description={t("settings.tables.cellMatching.description")}
                    checked={tables.tables?.do_cell_matching ?? true}
                    onChange={(do_cell_matching) =>
                      tables.updateTables({ do_cell_matching })
                    }
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                </SettingsSection>

                {/* Image Settings */}
                <SettingsSection
                  title={t("settings.sections.images")}
                  icon="image"
                >
                  <ToggleSetting
                    label={t("settings.images.extract.label")}
                    description={t("settings.images.extract.description")}
                    checked={images.images?.extract ?? true}
                    onChange={(extract) => images.updateImages({ extract })}
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.images.classify.label")}
                    description={t("settings.images.classify.description")}
                    checked={images.images?.classify ?? true}
                    onChange={(classify) => images.updateImages({ classify })}
                    disabled={images.isUpdating || !images.images?.extract}
                  />
                  <ToggleSetting
                    label={t("settings.images.generatePage.label")}
                    description={t("settings.images.generatePage.description")}
                    checked={images.images?.generate_page_images ?? false}
                    onChange={(generate_page_images) =>
                      images.updateImages({ generate_page_images })
                    }
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.images.generatePictures.label")}
                    description={t(
                      "settings.images.generatePictures.description"
                    )}
                    checked={images.images?.generate_picture_images ?? true}
                    onChange={(generate_picture_images) =>
                      images.updateImages({ generate_picture_images })
                    }
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.images.generateTables.label")}
                    description={t(
                      "settings.images.generateTables.description"
                    )}
                    checked={images.images?.generate_table_images ?? true}
                    onChange={(generate_table_images) =>
                      images.updateImages({ generate_table_images })
                    }
                    disabled={images.isUpdating}
                  />
                  <SliderSetting
                    label={t("settings.images.scale.label")}
                    description={t("settings.images.scale.description")}
                    value={images.images?.images_scale ?? 1.0}
                    min={0.1}
                    max={4.0}
                    step={0.1}
                    onChange={(images_scale) =>
                      images.updateImages({ images_scale })
                    }
                    disabled={images.isUpdating}
                  />
                </SettingsSection>

                {/* Performance Settings */}
                <SettingsSection
                  title={t("settings.sections.performance")}
                  icon="bolt"
                >
                  <SelectSetting
                    label={t("settings.performance.device.label")}
                    description={t("settings.performance.device.description")}
                    value={performance.performance?.device ?? "auto"}
                    options={performance.availableDevices.map((d) => ({
                      value: d.id,
                      label: d.name,
                    }))}
                    onChange={(device) =>
                      performance.updatePerformance({ device })
                    }
                    disabled={performance.isUpdating}
                  />
                  <NumberSetting
                    label={t("settings.performance.threads.label")}
                    description={t("settings.performance.threads.description")}
                    value={performance.performance?.num_threads ?? 4}
                    min={1}
                    max={32}
                    onChange={(num_threads) =>
                      performance.updatePerformance({ num_threads })
                    }
                    disabled={performance.isUpdating}
                  />
                  <NumberSetting
                    label={t("settings.performance.timeout.label")}
                    description={t("settings.performance.timeout.description")}
                    value={performance.performance?.document_timeout ?? 0}
                    min={0}
                    max={3600}
                    onChange={(document_timeout) =>
                      performance.updatePerformance({
                        document_timeout: document_timeout || null,
                      })
                    }
                    disabled={performance.isUpdating}
                  />
                </SettingsSection>

                {/* RAG/Chunking Settings */}
                <SettingsSection
                  title={t("settings.sections.chunking")}
                  icon="puzzle"
                >
                  <ToggleSetting
                    label={t("settings.chunking.enable.label")}
                    description={t("settings.chunking.enable.description")}
                    checked={chunking.chunking?.enabled ?? false}
                    onChange={(enabled) => chunking.updateChunking({ enabled })}
                    disabled={chunking.isUpdating}
                  />
                  <NumberSetting
                    label={t("settings.chunking.maxTokens.label")}
                    description={t("settings.chunking.maxTokens.description")}
                    value={chunking.chunking?.max_tokens ?? 512}
                    min={64}
                    max={8192}
                    onChange={(max_tokens) =>
                      chunking.updateChunking({ max_tokens })
                    }
                    disabled={
                      chunking.isUpdating || !chunking.chunking?.enabled
                    }
                  />
                  <ToggleSetting
                    label={t("settings.chunking.mergePeers.label")}
                    description={t("settings.chunking.mergePeers.description")}
                    checked={chunking.chunking?.merge_peers ?? true}
                    onChange={(merge_peers) =>
                      chunking.updateChunking({ merge_peers })
                    }
                    disabled={
                      chunking.isUpdating || !chunking.chunking?.enabled
                    }
                  />
                </SettingsSection>

                {/* Enrichment Settings */}
                <SettingsSection
                  title={t("settings.sections.enrichment")}
                  icon="sparkles"
                >
                  <ToggleSetting
                    label={t("settings.enrichment.code.label")}
                    description={t("settings.enrichment.code.description")}
                    checked={enrichment.enrichment?.code_enrichment ?? false}
                    onChange={(code_enrichment) =>
                      enrichment.updateEnrichment({ code_enrichment })
                    }
                    disabled={enrichment.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.enrichment.formula.label")}
                    description={t("settings.enrichment.formula.description")}
                    checked={enrichment.enrichment?.formula_enrichment ?? false}
                    onChange={(formula_enrichment) =>
                      enrichment.updateEnrichment({ formula_enrichment })
                    }
                    disabled={enrichment.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.enrichment.pictureClassification.label")}
                    description={t(
                      "settings.enrichment.pictureClassification.description"
                    )}
                    checked={
                      enrichment.enrichment?.picture_classification ?? false
                    }
                    onChange={(picture_classification) =>
                      enrichment.updateEnrichment({ picture_classification })
                    }
                    disabled={enrichment.isUpdating}
                  />
                  <ToggleSetting
                    label={t("settings.enrichment.pictureDescription.label")}
                    description={t(
                      "settings.enrichment.pictureDescription.description"
                    )}
                    checked={
                      enrichment.enrichment?.picture_description ?? false
                    }
                    onChange={(picture_description) =>
                      enrichment.updateEnrichment({ picture_description })
                    }
                    disabled={enrichment.isUpdating}
                  />
                  {(enrichment.enrichment?.picture_description ||
                    enrichment.enrichment?.formula_enrichment) && (
                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                      <p className="text-xs text-yellow-400">
                        {t("settings.enrichment.warning")}
                      </p>
                    </div>
                  )}

                  {/* Model Pre-Download Section */}
                  {enrichment.models && enrichment.models.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-dark-700">
                      <h4 className="text-sm font-medium text-dark-200 mb-3">
                        {t("settings.enrichment.preDownload.title")}
                      </h4>
                      <p className="text-xs text-dark-400 mb-3">
                        {t("settings.enrichment.preDownload.description")}
                      </p>
                      <div className="space-y-2">
                        {enrichment.models.map((model) => (
                          <div
                            key={model.id}
                            className={`p-3 bg-dark-800 rounded-lg ${
                              model.error ? "border border-yellow-500/30" : ""
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-dark-200">
                                    {model.name}
                                  </span>
                                  {model.downloaded ? (
                                    <span className="text-xs text-green-400">
                                      {t("settings.enrichment.model.ready")}
                                    </span>
                                  ) : model.error ? (
                                    <span className="text-xs text-yellow-400">
                                      {t(
                                        "settings.enrichment.model.unavailable"
                                      )}
                                    </span>
                                  ) : (
                                    <span className="text-xs text-dark-500">
                                      ~{model.size_mb}MB
                                    </span>
                                  )}
                                </div>
                                <p className="text-xs text-dark-500 truncate">
                                  {model.description}
                                </p>
                              </div>

                              {/* Action buttons */}
                              {!model.error &&
                                !model.downloaded &&
                                !enrichment.downloadingModels[model.id] && (
                                  <button
                                    onClick={() =>
                                      enrichment.downloadModel(model.id)
                                    }
                                    className="ml-3 px-3 py-1.5 text-xs bg-primary-500/20 text-primary-400
                                           hover:bg-primary-500/30 rounded-lg transition-colors"
                                  >
                                    {t("settings.actions.download")}
                                  </button>
                                )}

                              {enrichment.downloadingModels[model.id] && (
                                <div className="ml-3 w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                              )}

                              {model.downloaded && (
                                <span className="ml-3 text-green-500">
                                  <svg
                                    className="w-5 h-5"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                  >
                                    <path
                                      fillRule="evenodd"
                                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                      clipRule="evenodd"
                                    />
                                  </svg>
                                </span>
                              )}
                            </div>

                            {/* Error/upgrade message */}
                            {model.error && (
                              <div className="mt-2 p-2 bg-yellow-500/10 rounded text-xs text-yellow-400">
                                {model.error}
                              </div>
                            )}

                            {/* Download Progress */}
                            {enrichment.downloadingModels[model.id] &&
                              enrichment.downloadProgress[model.id] && (
                                <div className="mt-2">
                                  <div className="flex items-center gap-2 mb-1">
                                    <div className="flex-1 h-1.5 bg-dark-700 rounded-full overflow-hidden">
                                      <div
                                        className={`h-full transition-all duration-300 ${
                                          enrichment.downloadProgress[model.id]
                                            .status === "error"
                                            ? "bg-red-500"
                                            : "bg-primary-500"
                                        }`}
                                        style={{
                                          width: `${
                                            enrichment.downloadProgress[
                                              model.id
                                            ].progress
                                          }%`,
                                        }}
                                      />
                                    </div>
                                    <span className="text-xs text-dark-400">
                                      {
                                        enrichment.downloadProgress[model.id]
                                          .progress
                                      }
                                      %
                                    </span>
                                  </div>
                                  <p
                                    className={`text-xs ${
                                      enrichment.downloadProgress[model.id]
                                        .status === "error"
                                        ? "text-red-400"
                                        : "text-dark-400"
                                    }`}
                                  >
                                    {
                                      enrichment.downloadProgress[model.id]
                                        .message
                                    }
                                  </p>
                                </div>
                              )}
                          </div>
                        ))}
                      </div>

                      {/* Docling upgrade hint */}
                      {enrichment.models.some((m) => m.requires_upgrade) && (
                        <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                          <p className="text-xs text-blue-400">
                            {t("settings.enrichment.upgradeTip")}
                          </p>
                          <code className="mt-1 block text-xs text-blue-300 bg-blue-500/10 p-2 rounded font-mono">
                            pip install --upgrade docling
                          </code>
                        </div>
                      )}
                    </div>
                  )}
                </SettingsSection>

                {/* Output Settings */}
                <SettingsSection
                  title={t("settings.sections.output")}
                  icon="document"
                >
                  <SelectSetting
                    label={t("settings.output.defaultFormat.label")}
                    description={t("settings.output.defaultFormat.description")}
                    value={output.output?.default_format ?? "markdown"}
                    options={output.availableFormats.map((fmt) => ({
                      value: fmt.id,
                      label: fmt.name,
                    }))}
                    onChange={(default_format) =>
                      output.updateOutput({ default_format })
                    }
                    disabled={output.isUpdating}
                  />
                </SettingsSection>

                {/* Reset Button */}
                <div className="pt-4 border-t border-dark-700">
                  <button
                    onClick={() => settings.resetSettings()}
                    disabled={settings.isResetting}
                    className="w-full py-3 px-4 bg-dark-800 hover:bg-dark-700 text-dark-300 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
                  >
                    {settings.isResetting ? (
                      <div className="w-4 h-4 border-2 border-dark-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <svg
                        className="w-4 h-4"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                    {t("settings.actions.resetDefaults")}
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// Settings Section Component
interface SettingsSectionProps {
  title: string;
  icon: string;
  children: React.ReactNode;
}

function SettingsSection({ title, icon, children }: SettingsSectionProps) {
  const icons: Record<string, React.ReactNode> = {
    eye: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z"
      />
    ),
    table: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125m0 0h7.5"
      />
    ),
    image: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
      />
    ),
    document: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
      />
    ),
    bolt: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
      />
    ),
    puzzle: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M14.25 6.087c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003 0-1.036-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003.215.283.401.604.401.959v0a.64.64 0 01-.657.643 48.39 48.39 0 01-4.163-.3c.186 1.613.293 3.25.315 4.907a.656.656 0 01-.658.663v0c-.355 0-.676-.186-.959-.401a1.647 1.647 0 00-1.003-.349c-1.036 0-1.875 1.007-1.875 2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401v0c.31 0 .555.26.532.57a48.039 48.039 0 01-.642 5.056c1.518.19 3.058.309 4.616.354a.64.64 0 00.657-.643v0c0-.355-.186-.676-.401-.959a1.647 1.647 0 01-.349-1.003c0-1.035 1.008-1.875 2.25-1.875 1.243 0 2.25.84 2.25 1.875 0 .369-.128.713-.349 1.003-.215.283-.4.604-.4.959v0c0 .333.277.599.61.58a48.1 48.1 0 005.427-.63 48.05 48.05 0 00.582-4.717.532.532 0 00-.533-.57v0c-.355 0-.676.186-.959.401-.29.221-.634.349-1.003.349-1.035 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25c.37 0 .713.128 1.003.349.283.215.604.401.96.401v0a.656.656 0 00.658-.663 48.422 48.422 0 00-.37-5.36c-1.886.342-3.81.574-5.766.689a.578.578 0 01-.61-.58v0z"
      />
    ),
    sparkles: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
      />
    ),
  };

  return (
    <div className="bg-dark-800/50 rounded-xl p-5">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
          <svg
            className="w-4 h-4 text-primary-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            {icons[icon]}
          </svg>
        </div>
        <h3 className="font-semibold text-dark-100">{title}</h3>
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

// Toggle Setting Component
interface ToggleSettingProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

function ToggleSetting({
  label,
  description,
  checked,
  onChange,
  disabled,
}: ToggleSettingProps) {
  return (
    <div
      className={`flex items-start justify-between gap-4 ${
        disabled ? "opacity-50" : ""
      }`}
    >
      <div className="flex-1">
        <p className="text-sm font-medium text-dark-200">{label}</p>
        <p className="text-xs text-dark-400 mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        disabled={disabled}
        className={`
          relative w-11 h-6 rounded-full transition-colors duration-200
          ${checked ? "bg-primary-500" : "bg-dark-600"}
          ${disabled ? "cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        <motion.div
          className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm"
          animate={{ left: checked ? "24px" : "4px" }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
      </button>
    </div>
  );
}

// Select Setting Component
interface SelectSettingProps {
  label: string;
  description: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

function SelectSetting({
  label,
  description,
  value,
  options,
  onChange,
  disabled,
}: SelectSettingProps) {
  return (
    <div className={`${disabled ? "opacity-50" : ""}`}>
      <div className="mb-2">
        <p className="text-sm font-medium text-dark-200">{label}</p>
        <p className="text-xs text-dark-400 mt-0.5">{description}</p>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-dark-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:cursor-not-allowed"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

// Slider Setting Component
interface SliderSettingProps {
  label: string;
  description: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

function SliderSetting({
  label,
  description,
  value,
  min,
  max,
  step,
  onChange,
  disabled,
}: SliderSettingProps) {
  return (
    <div className={`${disabled ? "opacity-50" : ""}`}>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-dark-200">{label}</p>
          <p className="text-xs text-dark-400 mt-0.5">{description}</p>
        </div>
        <span className="text-sm font-mono text-primary-400">
          {value.toFixed(2)}
        </span>
      </div>
      <input
        type="range"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        disabled={disabled}
        className="w-full h-2 bg-dark-600 rounded-lg appearance-none cursor-pointer accent-primary-500 disabled:cursor-not-allowed"
      />
      <div className="flex justify-between text-xs text-dark-500 mt-1">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

// Number Setting Component
interface NumberSettingProps {
  label: string;
  description: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

function NumberSetting({
  label,
  description,
  value,
  min,
  max,
  onChange,
  disabled,
}: NumberSettingProps) {
  return (
    <div className={`${disabled ? "opacity-50" : ""}`}>
      <div className="mb-2">
        <p className="text-sm font-medium text-dark-200">{label}</p>
        <p className="text-xs text-dark-400 mt-0.5">{description}</p>
      </div>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={(e) => onChange(parseInt(e.target.value) || 0)}
        disabled={disabled}
        className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-dark-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:cursor-not-allowed"
      />
    </div>
  );
}
