import React, { useState, useEffect, useRef } from 'react';
import { 
  X, UploadCloud, FileSpreadsheet, Download, CheckCircle2, 
  AlertCircle, Play, Database, ShieldCheck, FolderOpen, RefreshCw
} from 'lucide-react';
import { uploadDataset, getTemplateDownloadUrl } from '../api';

export default function UploadDatasetModal({ onClose, onDatasetImported, onRunAgentAfterImport }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [clearCache, setClearCache] = useState(true);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleFileSelection = (fileObj) => {
    if (!fileObj) return;
    if (!fileObj.name.toLowerCase().endsWith('.csv') && !fileObj.name.toLowerCase().endsWith('.txt')) {
      setError('Please select a valid CSV or TXT file (.csv, .txt).');
      return;
    }
    setError('');
    setSelectedFile(fileObj);
  };

  const handleFileInputChange = (e) => {
    const fileObj = e.target.files?.[0];
    if (fileObj) {
      handleFileSelection(fileObj);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) {
      handleFileSelection(dropped);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleTriggerBrowse = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      setError('Please choose a CSV file first before uploading.');
      return;
    }

    setError('');
    setUploading(true);

    try {
      const res = await uploadDataset(selectedFile, clearCache);
      setUploadResult(res);
      if (onDatasetImported) {
        onDatasetImported(res);
      }
    } catch (err) {
      setError(err.message || 'Failed to upload dataset.');
    } finally {
      setUploading(false);
    }
  };

  const handleResetFile = (e) => {
    if (e) e.stopPropagation();
    setSelectedFile(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes && bytes !== 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const handleConfirmAndExplore = () => {
    onClose();
  };

  const handleConfirmAndRun = async () => {
    onClose();
    if (onRunAgentAfterImport) {
      onRunAgentAfterImport();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div 
        className="modal-content" 
        style={{ maxWidth: '720px' }} 
        onClick={(e) => e.stopPropagation()}
      >
        {/* Native File Input */}
        <input
          id="csv-file-upload-input"
          ref={fileInputRef}
          type="file"
          accept=".csv,.txt"
          style={{ position: 'absolute', width: '1px', height: '1px', opacity: 0, pointerEvents: 'none' }}
          onChange={handleFileInputChange}
        />

        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ padding: '6px', background: 'var(--mobitel-green-tint)', borderRadius: 'var(--radius-sm)', color: 'var(--mobitel-green)' }}>
              <Database size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Import Customer Dataset</h3>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                Upload an external CSV file with customer telephone, email, and suspension remarks.
              </div>
            </div>
          </div>
          <button 
            type="button"
            onClick={onClose} 
            style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Template Download Banner */}
          <div 
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--bg-elevated)',
              border: '1px dashed var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 14px',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <FileSpreadsheet size={15} color="var(--slt-cyan)" />
              <span>Need standard SLT column headers and formatting?</span>
            </div>
            <a
              href={getTemplateDownloadUrl()}
              download="slt_customer_dataset_template.csv"
              className="btn-secondary"
              style={{ fontSize: '0.76rem', padding: '4px 10px', textDecoration: 'none' }}
            >
              <Download size={12} />
              <span>Sample CSV</span>
            </a>
          </div>

          {/* Error message */}
          {error && (
            <div
              style={{
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--danger-red-tint)',
                color: 'var(--danger-red)',
                border: '1px solid var(--danger-red-border)',
                marginBottom: '16px',
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {!uploadResult ? (
            <div>
              {!selectedFile ? (
                /* Dropzone with Native Label and Browse Click */
                <label
                  htmlFor="csv-file-upload-input"
                  className={`upload-dropzone ${isDragOver ? 'dragover' : ''}`}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  style={{
                    padding: '36px 20px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '12px',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius-lg)',
                    border: isDragOver ? '2px dashed var(--slt-cyan)' : '2px dashed var(--border-color)',
                    background: isDragOver ? 'var(--bg-card-hover)' : 'var(--bg-elevated)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div 
                    style={{ 
                      padding: '14px', 
                      borderRadius: '50%', 
                      background: 'rgba(0, 91, 172, 0.1)', 
                      color: 'var(--slt-cyan)' 
                    }}
                  >
                    <UploadCloud size={30} />
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Drag and drop your CSV file here
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Or click anywhere in this box to browse files
                    </div>
                  </div>

                  <button
                    type="button"
                    className="btn-primary"
                    onClick={handleTriggerBrowse}
                    style={{ marginTop: '6px' }}
                  >
                    <FolderOpen size={14} />
                    <span>Browse CSV File</span>
                  </button>
                </label>
              ) : (
                /* Selected File Card */
                <div
                  style={{
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '20px',
                    marginBottom: '10px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div
                        style={{
                          width: '42px',
                          height: '42px',
                          borderRadius: '8px',
                          background: 'var(--mobitel-green-tint)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'var(--mobitel-green)',
                          border: '1px solid var(--mobitel-green-border)',
                        }}
                      >
                        <FileSpreadsheet size={22} />
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                          {selectedFile.name}
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                          {formatFileSize(selectedFile.size)} • Ready for import
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        type="button"
                        className="btn-secondary"
                        onClick={handleTriggerBrowse}
                        disabled={uploading}
                        style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        Change File
                      </button>
                      <button
                        type="button"
                        className="btn-ghost"
                        onClick={handleResetFile}
                        disabled={uploading}
                        style={{ fontSize: '0.8rem', padding: '6px 10px', color: 'var(--danger-red)' }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  <div style={{ marginTop: '16px', padding: '10px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(0, 91, 172, 0.08)', border: '1px solid rgba(0, 91, 172, 0.2)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    File staged. Click <strong>"Upload Dataset"</strong> below to parse accounts, validate columns, and update the repository.
                  </div>

                  <div style={{ marginTop: '12px', padding: '10px 14px', borderRadius: 'var(--radius-md)', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <input
                      type="checkbox"
                      id="upload-clear-cache-checkbox"
                      checked={clearCache}
                      onChange={(e) => setClearCache(e.target.checked)}
                      style={{ cursor: 'pointer', accentColor: 'var(--slt-cyan)', width: '16px', height: '16px' }}
                    />
                    <label htmlFor="upload-clear-cache-checkbox" style={{ cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                      <strong>Clear duplicate prevention cache</strong> (Recommended: ensures all accounts in this new CSV receive notifications without being skipped)
                    </label>
                  </div>
                </div>
              )}

              <div style={{ marginTop: '12px', fontSize: '0.76rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                Supports standard comma, semicolon, or tab-delimited files. Auto-detects columns: landline, name, email, status, remark.
              </div>
            </div>
          ) : (
            /* Upload Result Preview & Analytics */
            <div>
              {/* Success notification */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  background: 'var(--mobitel-green-tint)',
                  border: '1px solid var(--mobitel-green-border)',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '16px',
                }}
              >
                <CheckCircle2 size={18} color="var(--mobitel-green)" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--mobitel-green)' }}>
                    Dataset Successfully Imported!
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {uploadResult.message}
                  </div>
                  {uploadResult.cache_cleared && (
                    <div style={{ fontSize: '0.74rem', color: 'var(--mobitel-green)', marginTop: '4px', fontWeight: 500 }}>
                      ✓ Duplicate prevention cache deleted ({uploadResult.lifecycle_records_cleared ?? 0} previous records cleared). Newly uploaded accounts will be evaluated freshly.
                    </div>
                  )}
                </div>
              </div>

              {/* Quick Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '16px' }}>
                <div style={{ background: 'var(--bg-elevated)', padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>TOTAL RECORDS</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>{uploadResult.total_records}</div>
                </div>
                <div style={{ background: 'var(--danger-red-tint)', padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid var(--danger-red-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--danger-red)' }}>SUSPENDED</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--danger-red)', marginTop: '2px' }}>{uploadResult.suspended_records}</div>
                </div>
                <div style={{ background: 'var(--mobitel-green-tint)', padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid var(--mobitel-green-border)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--mobitel-green)' }}>READY FOR EMAIL</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--mobitel-green)', marginTop: '2px' }}>{uploadResult.suspended_with_email}</div>
                </div>
                <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(245, 158, 11, 0.25)', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.7rem', color: '#F59E0B' }}>MISSING EMAIL</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F59E0B', marginTop: '2px' }}>{uploadResult.missing_email_records}</div>
                </div>
              </div>

              {/* Smart Column Mapping Card */}
              {uploadResult.mapped_columns && (
                <div style={{ background: 'var(--bg-elevated)', padding: '10px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px' }}>
                  <div style={{ fontSize: '0.76rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ShieldCheck size={13} color="var(--slt-cyan)" />
                    <span>Auto-Detected Column Mappings:</span>
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {Object.entries(uploadResult.mapped_columns).map(([field, rawCol]) => (
                      <span 
                        key={field} 
                        style={{ 
                          fontSize: '0.72rem', 
                          padding: '2px 7px', 
                          borderRadius: '4px', 
                          background: 'rgba(0, 91, 172, 0.1)', 
                          border: '1px solid rgba(0, 91, 172, 0.25)', 
                          color: 'var(--slt-cyan)'
                        }}
                      >
                        <strong>{rawCol}</strong> &rarr; {field}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Preview */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Preview (First {uploadResult.preview?.length || 0} rows):
                </div>
                <div className="table-responsive" style={{ maxHeight: '160px' }}>
                  <table className="data-table" style={{ fontSize: '0.78rem' }}>
                    <thead>
                      <tr>
                        <th style={{ padding: '6px 10px' }}>Landline</th>
                        <th style={{ padding: '6px 10px' }}>Customer Name</th>
                        <th style={{ padding: '6px 10px' }}>Email</th>
                        <th style={{ padding: '6px 10px' }}>WhatsApp</th>
                        <th style={{ padding: '6px 10px' }}>Status</th>
                        <th style={{ padding: '6px 10px' }}>Remark</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uploadResult.preview?.map((r, i) => (
                        <tr key={i}>
                          <td style={{ padding: '6px 10px', fontFamily: 'var(--font-mono)' }}>{r.land_number}</td>
                          <td style={{ padding: '6px 10px' }}>{r.customer_name}</td>
                          <td style={{ padding: '6px 10px', color: r.email ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                            {r.email || '(Missing)'}
                          </td>
                          <td style={{ padding: '6px 10px', color: r.whatsapp_number ? 'var(--text-primary)' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {r.whatsapp_number || '—'}
                          </td>
                          <td style={{ padding: '6px 10px' }}>
                            <span className={`status-badge ${r.status === 'Active' ? 'badge-active' : 'badge-suspended'}`}>
                              {r.status}
                            </span>
                          </td>
                          <td style={{ padding: '6px 10px' }}>{r.remark}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div style={{ 
                marginTop: '12px', 
                padding: '10px 14px', 
                borderRadius: 'var(--radius-md)', 
                background: 'rgba(0, 144, 208, 0.08)', 
                border: '1px solid rgba(0, 144, 208, 0.2)',
                fontSize: '0.8rem',
                color: 'var(--text-secondary)'
              }}>
                Dataset loaded successfully. You can trigger evaluation whenever you are ready using the <strong>RUN AGENT</strong> button in the top navigation bar.
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          {!uploadResult ? (
            <>
              <button type="button" className="btn-secondary" onClick={onClose} disabled={uploading}>
                Cancel
              </button>
              <button 
                type="button" 
                className="btn-primary" 
                onClick={handleUploadSubmit}
                disabled={!selectedFile || uploading}
                id="modal-upload-dataset-btn"
              >
                {uploading ? (
                  <>
                    <RefreshCw size={14} className="spin-anim" />
                    <span>Uploading Dataset...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud size={14} />
                    <span>Upload Dataset</span>
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              <button 
                type="button" 
                className="btn-secondary" 
                onClick={() => {
                  setUploadResult(null);
                  setSelectedFile(null);
                  setError('');
                }}
                style={{ marginRight: 'auto' }}
              >
                Upload Different File
              </button>
              <button 
                type="button" 
                className="btn-primary" 
                onClick={handleConfirmAndExplore}
              >
                <span>View Customer Directory</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
