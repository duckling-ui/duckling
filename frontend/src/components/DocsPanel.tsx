import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./DocsPanel.css";

interface DocFile {
  id: string;
  name: string;
  filename: string;
}

interface DocContent {
  name: string;
  filename: string;
  content_md: string;
  content_html: string;
}

interface DocsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DocsPanel({ isOpen, onClose }: DocsPanelProps) {
  const [docs, setDocs] = useState<DocFile[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [docContent, setDocContent] = useState<DocContent | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetch("/api/docs")
        .then((res) => res.json())
        .then((data) => {
          setDocs(data.docs || []);
          if (!selectedDoc && data.docs?.length > 0) {
            setSelectedDoc(data.docs[0].id);
          }
        })
        .catch(() => setError("Failed to load documentation"));
    }
  }, [isOpen]);

  // Rewrite image URLs to point to the API endpoint
  const processHtml = (html: string): string => {
    // Replace relative image paths with API endpoint
    // Matches: src="./filename.png" or src="filename.png"
    return html.replace(
      /src="\.?\/?([^"]+\.(png|jpg|jpeg|gif|svg|webp))"/gi,
      'src="/api/docs/images/$1"'
    );
  };

  useEffect(() => {
    if (selectedDoc) {
      setLoading(true);
      setError(null);
      fetch(`/api/docs/${selectedDoc}`)
        .then((res) => {
          if (!res.ok) throw new Error("Doc not found");
          return res.json();
        })
        .then((data) => {
          // Process HTML to fix image URLs
          setDocContent({
            ...data,
            content_html: processHtml(data.content_html),
          });
          setLoading(false);
        })
        .catch(() => {
          setError("Failed to load document");
          setLoading(false);
        });
    }
  }, [selectedDoc]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-5xl bg-dark-900 shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-dark-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-primary-400"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
                    />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-bold text-dark-100">
                    Documentation
                  </h2>
                  <p className="text-sm text-dark-400">Duckling Reference</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-dark-800 rounded-lg transition-colors"
              >
                <svg
                  className="w-5 h-5 text-dark-400"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 flex overflow-hidden">
              {/* Sidebar */}
              <div className="w-56 border-r border-dark-700 p-4 overflow-y-auto">
                <h3 className="text-xs font-semibold text-dark-500 uppercase tracking-wider mb-3">
                  Documents
                </h3>
                <nav className="space-y-1">
                  {docs.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => setSelectedDoc(doc.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                        selectedDoc === doc.id
                          ? "bg-primary-500/20 text-primary-400"
                          : "text-dark-300 hover:bg-dark-800 hover:text-dark-100"
                      }`}
                    >
                      {doc.name}
                    </button>
                  ))}
                </nav>
                {docs.length === 0 && !error && (
                  <p className="text-sm text-dark-500 text-center py-4">
                    Loading...
                  </p>
                )}
              </div>

              {/* Main content */}
              <div className="flex-1 overflow-y-auto p-6">
                {loading && (
                  <div className="flex items-center justify-center h-full">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}

                {error && (
                  <div className="text-center py-12">
                    <p className="text-dark-400">{error}</p>
                  </div>
                )}

                {!loading && !error && docContent && (
                  <div
                    className="docs-content"
                    dangerouslySetInnerHTML={{
                      __html: docContent.content_html,
                    }}
                  />
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-dark-700 p-4 flex items-center justify-between">
              <p className="text-sm text-dark-500">
                Also available in{" "}
                <code className="text-primary-400 bg-dark-800 px-1.5 py-0.5 rounded text-xs">
                  /docs
                </code>
              </p>
              {docContent && (
                <a
                  href={`/api/docs/${selectedDoc}/raw`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
                >
                  <svg
                    className="w-4 h-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                  Download
                </a>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
