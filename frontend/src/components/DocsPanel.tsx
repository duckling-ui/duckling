import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./DocsPanel.css";

interface DocFile {
  id: string;
  name: string;
  path: string;
}


interface DocsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

// Chevron icon component
const ChevronIcon = ({ isExpanded }: { isExpanded: boolean }) => (
  <svg
    className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? "rotate-90" : ""}`}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
  </svg>
);

export default function DocsPanel({ isOpen, onClose }: DocsPanelProps) {
  const [docs, setDocs] = useState<DocFile[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [siteBuilt, setSiteBuilt] = useState(true);
  const [building, setBuilding] = useState(false);
  const [buildError, setBuildError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["Home"]));

  // Group docs by category
  const groupedDocs = useMemo(() => {
    const groups: Record<string, DocFile[]> = {};

    docs.forEach((doc) => {
      // Extract category from name (e.g., "Api: Conversion" -> "Api")
      const colonIndex = doc.name.indexOf(":");
      let category: string;
      let itemName: string;

      if (colonIndex > -1) {
        category = doc.name.substring(0, colonIndex).trim();
        itemName = doc.name.substring(colonIndex + 1).trim();
      } else {
        category = "Home";
        itemName = doc.name;
      }

      if (!groups[category]) {
        groups[category] = [];
      }

      groups[category].push({
        ...doc,
        name: itemName,
      });
    });

    // Sort categories and items
    const sortedCategories = Object.keys(groups).sort((a, b) => {
      // Home always first
      if (a === "Home") return -1;
      if (b === "Home") return 1;
      return a.localeCompare(b);
    });

    return sortedCategories.map((category) => ({
      name: category,
      items: groups[category].sort((a, b) => a.name.localeCompare(b.name)),
      isExpanded: expandedSections.has(category),
    }));
  }, [docs, expandedSections]);

  const fetchDocs = () => {
    setLoading(true);
    setError(null);
    fetch("/api/docs")
      .then((res) => res.json())
      .then((data) => {
        setDocs(data.docs || []);
        setSiteBuilt(data.site_built !== false);
        if (data.docs?.length > 0) {
          // Find and select "Home" or first doc
          const homeDoc = data.docs.find((d: DocFile) => d.id === "index");
          const firstDoc = homeDoc || data.docs[0];
          setSelectedDoc(firstDoc.id);
          setSelectedPath(firstDoc.path || "");
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load documentation");
        setLoading(false);
      });
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocs();
    }
  }, [isOpen]);

  const handleDocSelect = (doc: DocFile) => {
    setSelectedDoc(doc.id);
    setSelectedPath(doc.path || "");
  };

  const toggleSection = (sectionName: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(sectionName)) {
        next.delete(sectionName);
      } else {
        next.add(sectionName);
      }
      return next;
    });
  };

  const handleBuildDocs = async () => {
    setBuilding(true);
    setBuildError(null);
    try {
      const response = await fetch("/api/docs/build", { method: "POST" });
      const data = await response.json();
      if (data.success) {
        // Refresh the docs list
        fetchDocs();
      } else {
        setBuildError(data.message || "Failed to build documentation");
      }
    } catch {
      setBuildError("Failed to build documentation. Check if MkDocs is installed.");
    } finally {
      setBuilding(false);
    }
  };

  // Build the iframe URL for the selected doc
  const getDocUrl = () => {
    if (!selectedPath && selectedDoc === "index") {
      return "/api/docs/site/";
    }
    return `/api/docs/site/${selectedPath}/`;
  };

  // Expand all sections
  const expandAll = () => {
    setExpandedSections(new Set(groupedDocs.map((g) => g.name)));
  };

  // Collapse all sections
  const collapseAll = () => {
    setExpandedSections(new Set(["Home"]));
  };

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
            className="fixed right-0 top-0 h-full w-full max-w-6xl bg-dark-900 shadow-2xl z-50 flex flex-col"
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
              <div className="flex items-center gap-2">
                <a
                  href="/api/docs/site/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 hover:bg-dark-800 rounded-lg transition-colors text-dark-400 hover:text-dark-100"
                  title="Open in new tab"
                >
                  <svg
                    className="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
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
            </div>

            {/* Content */}
            <div className="flex-1 flex overflow-hidden">
              {/* Sidebar */}
              <div className="w-64 border-r border-dark-700 flex flex-col flex-shrink-0">
                {/* Sidebar header with expand/collapse */}
                <div className="p-3 border-b border-dark-700 flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-dark-500 uppercase tracking-wider">
                    Navigation
                  </h3>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={expandAll}
                      className="p-1 hover:bg-dark-800 rounded text-dark-500 hover:text-dark-300 transition-colors"
                      title="Expand all"
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                      </svg>
                    </button>
                    <button
                      onClick={collapseAll}
                      className="p-1 hover:bg-dark-800 rounded text-dark-500 hover:text-dark-300 transition-colors"
                      title="Collapse all"
                    >
                      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Navigation items */}
                <nav className="flex-1 overflow-y-auto p-2">
                  {groupedDocs.map((section) => (
                    <div key={section.name} className="mb-1">
                      {/* Section header */}
                      <button
                        onClick={() => toggleSection(section.name)}
                        className="w-full flex items-center gap-2 px-2 py-1.5 text-sm font-medium text-dark-300 hover:text-dark-100 hover:bg-dark-800 rounded-lg transition-colors"
                      >
                        <ChevronIcon isExpanded={section.isExpanded} />
                        <span>{section.name}</span>
                        <span className="ml-auto text-xs text-dark-500 bg-dark-800 px-1.5 py-0.5 rounded">
                          {section.items.length}
                        </span>
                      </button>

                      {/* Section items */}
                      <AnimatePresence initial={false}>
                        {section.isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                          >
                            <div className="ml-4 mt-1 space-y-0.5 border-l border-dark-700 pl-2">
                              {section.items.map((doc) => (
                                <button
                                  key={doc.id}
                                  onClick={() => handleDocSelect(doc)}
                                  className={`w-full text-left px-2 py-1.5 rounded text-sm transition-colors ${
                                    selectedDoc === doc.id
                                      ? "bg-primary-500/20 text-primary-400"
                                      : "text-dark-400 hover:bg-dark-800 hover:text-dark-200"
                                  }`}
                                >
                                  {doc.name}
                                </button>
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  ))}

                  {docs.length === 0 && !error && loading && (
                    <p className="text-sm text-dark-500 text-center py-4">
                      Loading...
                    </p>
                  )}
                  {docs.length === 0 && !loading && !siteBuilt && (
                    <p className="text-sm text-dark-500 text-center py-4">
                      Documentation not built yet.
                    </p>
                  )}
                </nav>
              </div>

              {/* Main content - iframe */}
              <div className="flex-1 overflow-hidden bg-white">
                {loading && (
                  <div className="flex items-center justify-center h-full bg-dark-900">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}

                {error && (
                  <div className="flex items-center justify-center h-full bg-dark-900">
                    <div className="text-center py-12">
                      <p className="text-dark-400">{error}</p>
                      <p className="text-sm text-dark-500 mt-2">
                        Make sure to run <code className="text-primary-400">mkdocs build</code> first.
                      </p>
                    </div>
                  </div>
                )}

                {!loading && !error && !siteBuilt && (
                  <div className="flex items-center justify-center h-full bg-dark-900">
                    <div className="text-center py-12 max-w-md">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-800 flex items-center justify-center">
                        <svg
                          className="w-8 h-8 text-dark-500"
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
                      <h3 className="text-lg font-semibold text-dark-200 mb-2">
                        Documentation Not Built
                      </h3>
                      <p className="text-dark-400 mb-4">
                        The documentation site needs to be built before it can be viewed.
                      </p>
                      <button
                        onClick={handleBuildDocs}
                        disabled={building}
                        className="px-4 py-2 bg-primary-500 hover:bg-primary-600 disabled:bg-primary-500/50 text-white rounded-lg transition-colors flex items-center gap-2 mx-auto"
                      >
                        {building ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            Building...
                          </>
                        ) : (
                          <>
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
                                d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3"
                              />
                            </svg>
                            Build Documentation
                          </>
                        )}
                      </button>
                      {buildError && (
                        <p className="text-red-400 text-sm mt-3">{buildError}</p>
                      )}
                      <p className="text-sm text-dark-500 mt-4">
                        Or run manually: <code className="text-primary-400 bg-dark-800 px-1.5 py-0.5 rounded">mkdocs build</code>
                      </p>
                    </div>
                  </div>
                )}

                {!loading && !error && siteBuilt && selectedDoc && (
                  <iframe
                    src={getDocUrl()}
                    className="w-full h-full border-0"
                    title="Documentation"
                  />
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-dark-700 p-4 flex items-center justify-between">
              <p className="text-sm text-dark-500">
                Full documentation at{" "}
                <a
                  href="/api/docs/site/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-400 hover:text-primary-300"
                >
                  /api/docs/site/
                </a>
              </p>
              {siteBuilt && (
                <button
                  onClick={handleBuildDocs}
                  disabled={building}
                  className="text-sm text-dark-400 hover:text-dark-200 flex items-center gap-1 disabled:opacity-50"
                  title="Rebuild documentation"
                >
                  {building ? (
                    <div className="w-3 h-3 border border-dark-400 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <svg
                      className="w-3 h-3"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
                      />
                    </svg>
                  )}
                  Rebuild
                </button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
