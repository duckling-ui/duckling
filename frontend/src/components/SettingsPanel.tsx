import { motion, AnimatePresence } from 'framer-motion';
import { useAllSettings } from '../hooks/useSettings';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { ocr, tables, images, output, performance, chunking, isLoading, settings } = useAllSettings();

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
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-lg bg-dark-900 border-l border-dark-700 z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-dark-900/95 backdrop-blur-sm border-b border-dark-700 p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-dark-100">Settings</h2>
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

            {isLoading ? (
              <div className="p-6 flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <div className="p-6 space-y-6">
                {/* OCR Settings */}
                <SettingsSection title="OCR (Optical Character Recognition)" icon="eye">
                  <ToggleSetting
                    label="Enable OCR"
                    description="Extract text from scanned documents and images"
                    checked={ocr.ocr?.enabled ?? true}
                    onChange={(enabled) => ocr.updateOcr({ enabled })}
                    disabled={ocr.isUpdating}
                  />
                  <SelectSetting
                    label="OCR Backend"
                    description="Engine used for text recognition"
                    value={ocr.ocr?.backend ?? 'easyocr'}
                    options={ocr.availableBackends.map((b) => ({
                      value: b.id,
                      label: b.name,
                    }))}
                    onChange={(backend) => ocr.updateOcr({ backend })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                  <SelectSetting
                    label="OCR Language"
                    description="Primary language for text recognition"
                    value={ocr.ocr?.language ?? 'en'}
                    options={ocr.availableLanguages.map((lang) => ({
                      value: lang.code,
                      label: lang.name,
                    }))}
                    onChange={(language) => ocr.updateOcr({ language })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                  <ToggleSetting
                    label="Force Full Page OCR"
                    description="OCR the entire page instead of just detected text regions"
                    checked={ocr.ocr?.force_full_page_ocr ?? false}
                    onChange={(force_full_page_ocr) => ocr.updateOcr({ force_full_page_ocr })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                  <ToggleSetting
                    label="Use GPU"
                    description="Enable GPU acceleration (EasyOCR only)"
                    checked={ocr.ocr?.use_gpu ?? false}
                    onChange={(use_gpu) => ocr.updateOcr({ use_gpu })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled || ocr.ocr?.backend !== 'easyocr'}
                  />
                  <SliderSetting
                    label="Confidence Threshold"
                    description="Minimum confidence for OCR results"
                    value={ocr.ocr?.confidence_threshold ?? 0.5}
                    min={0}
                    max={1}
                    step={0.05}
                    onChange={(confidence_threshold) => ocr.updateOcr({ confidence_threshold })}
                    disabled={ocr.isUpdating || !ocr.ocr?.enabled}
                  />
                </SettingsSection>

                {/* Table Settings */}
                <SettingsSection title="Table Extraction" icon="table">
                  <ToggleSetting
                    label="Enable Table Extraction"
                    description="Detect and extract tables from documents"
                    checked={tables.tables?.enabled ?? true}
                    onChange={(enabled) => tables.updateTables({ enabled })}
                    disabled={tables.isUpdating}
                  />
                  <SelectSetting
                    label="Detection Mode"
                    description="Balance between speed and accuracy"
                    value={tables.tables?.mode ?? 'accurate'}
                    options={tables.availableModes.map((m) => ({
                      value: m.id,
                      label: m.name,
                    }))}
                    onChange={(mode) => tables.updateTables({ mode })}
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                  <ToggleSetting
                    label="Structure Extraction"
                    description="Preserve table structure and cell relationships"
                    checked={tables.tables?.structure_extraction ?? true}
                    onChange={(structure_extraction) => tables.updateTables({ structure_extraction })}
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                  <ToggleSetting
                    label="Cell Matching"
                    description="Match cell content to table structure"
                    checked={tables.tables?.do_cell_matching ?? true}
                    onChange={(do_cell_matching) => tables.updateTables({ do_cell_matching })}
                    disabled={tables.isUpdating || !tables.tables?.enabled}
                  />
                </SettingsSection>

                {/* Image Settings */}
                <SettingsSection title="Image Handling" icon="image">
                  <ToggleSetting
                    label="Extract Images"
                    description="Extract embedded images from documents"
                    checked={images.images?.extract ?? true}
                    onChange={(extract) => images.updateImages({ extract })}
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label="Classify Images"
                    description="Automatically classify and tag images"
                    checked={images.images?.classify ?? true}
                    onChange={(classify) => images.updateImages({ classify })}
                    disabled={images.isUpdating || !images.images?.extract}
                  />
                  <ToggleSetting
                    label="Generate Page Images"
                    description="Create images of each page"
                    checked={images.images?.generate_page_images ?? false}
                    onChange={(generate_page_images) => images.updateImages({ generate_page_images })}
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label="Generate Picture Images"
                    description="Extract embedded pictures as separate files"
                    checked={images.images?.generate_picture_images ?? true}
                    onChange={(generate_picture_images) => images.updateImages({ generate_picture_images })}
                    disabled={images.isUpdating}
                  />
                  <ToggleSetting
                    label="Generate Table Images"
                    description="Extract tables as images"
                    checked={images.images?.generate_table_images ?? true}
                    onChange={(generate_table_images) => images.updateImages({ generate_table_images })}
                    disabled={images.isUpdating}
                  />
                  <SliderSetting
                    label="Image Scale"
                    description="Scale factor for extracted images (1.0 = original)"
                    value={images.images?.images_scale ?? 1.0}
                    min={0.1}
                    max={4.0}
                    step={0.1}
                    onChange={(images_scale) => images.updateImages({ images_scale })}
                    disabled={images.isUpdating}
                  />
                </SettingsSection>

                {/* Performance Settings */}
                <SettingsSection title="Performance" icon="bolt">
                  <SelectSetting
                    label="Processing Device"
                    description="Hardware for document processing"
                    value={performance.performance?.device ?? 'auto'}
                    options={performance.availableDevices.map((d) => ({
                      value: d.id,
                      label: d.name,
                    }))}
                    onChange={(device) => performance.updatePerformance({ device })}
                    disabled={performance.isUpdating}
                  />
                  <NumberSetting
                    label="CPU Threads"
                    description="Number of threads for processing"
                    value={performance.performance?.num_threads ?? 4}
                    min={1}
                    max={32}
                    onChange={(num_threads) => performance.updatePerformance({ num_threads })}
                    disabled={performance.isUpdating}
                  />
                  <NumberSetting
                    label="Document Timeout (seconds)"
                    description="Maximum processing time (0 = no limit)"
                    value={performance.performance?.document_timeout ?? 0}
                    min={0}
                    max={3600}
                    onChange={(document_timeout) => performance.updatePerformance({ document_timeout: document_timeout || null })}
                    disabled={performance.isUpdating}
                  />
                </SettingsSection>

                {/* RAG/Chunking Settings */}
                <SettingsSection title="RAG / Chunking" icon="puzzle">
                  <ToggleSetting
                    label="Enable Chunking"
                    description="Split documents into chunks for RAG applications"
                    checked={chunking.chunking?.enabled ?? false}
                    onChange={(enabled) => chunking.updateChunking({ enabled })}
                    disabled={chunking.isUpdating}
                  />
                  <NumberSetting
                    label="Max Tokens per Chunk"
                    description="Maximum tokens in each chunk"
                    value={chunking.chunking?.max_tokens ?? 512}
                    min={64}
                    max={8192}
                    onChange={(max_tokens) => chunking.updateChunking({ max_tokens })}
                    disabled={chunking.isUpdating || !chunking.chunking?.enabled}
                  />
                  <ToggleSetting
                    label="Merge Peers"
                    description="Combine undersized chunks with similar metadata"
                    checked={chunking.chunking?.merge_peers ?? true}
                    onChange={(merge_peers) => chunking.updateChunking({ merge_peers })}
                    disabled={chunking.isUpdating || !chunking.chunking?.enabled}
                  />
                </SettingsSection>

                {/* Output Settings */}
                <SettingsSection title="Output Preferences" icon="document">
                  <SelectSetting
                    label="Default Format"
                    description="Preferred output format for downloads"
                    value={output.output?.default_format ?? 'markdown'}
                    options={output.availableFormats.map((fmt) => ({
                      value: fmt.id,
                      label: fmt.name,
                    }))}
                    onChange={(default_format) => output.updateOutput({ default_format })}
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
                      <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                        <path
                          fillRule="evenodd"
                          d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                    Reset to Defaults
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

function ToggleSetting({ label, description, checked, onChange, disabled }: ToggleSettingProps) {
  return (
    <div className={`flex items-start justify-between gap-4 ${disabled ? 'opacity-50' : ''}`}>
      <div className="flex-1">
        <p className="text-sm font-medium text-dark-200">{label}</p>
        <p className="text-xs text-dark-400 mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        disabled={disabled}
        className={`
          relative w-11 h-6 rounded-full transition-colors duration-200
          ${checked ? 'bg-primary-500' : 'bg-dark-600'}
          ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <motion.div
          className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm"
          animate={{ left: checked ? '24px' : '4px' }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
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

function SelectSetting({ label, description, value, options, onChange, disabled }: SelectSettingProps) {
  return (
    <div className={`${disabled ? 'opacity-50' : ''}`}>
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

function SliderSetting({ label, description, value, min, max, step, onChange, disabled }: SliderSettingProps) {
  return (
    <div className={`${disabled ? 'opacity-50' : ''}`}>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-dark-200">{label}</p>
          <p className="text-xs text-dark-400 mt-0.5">{description}</p>
        </div>
        <span className="text-sm font-mono text-primary-400">{value.toFixed(2)}</span>
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

function NumberSetting({ label, description, value, min, max, onChange, disabled }: NumberSettingProps) {
  return (
    <div className={`${disabled ? 'opacity-50' : ''}`}>
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

