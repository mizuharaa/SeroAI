import React, { useCallback } from 'react';
import { Upload, FileVideo, Image as ImageIcon } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isAnalyzing: boolean;
}

export function UploadZone({ onFileSelect, isAnalyzing }: UploadZoneProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (isAnalyzing) return;
      const file = e.dataTransfer.files[0];
      if (file && (file.type.startsWith('video/') || file.type.startsWith('image/'))) {
        onFileSelect(file);
      }
    },
    [onFileSelect, isAnalyzing]
  );
  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      className={`relative border-2 border-dashed rounded-xl p-12 transition-all ${
        isAnalyzing ? 'border-gray-300 bg-gray-50 cursor-not-allowed opacity-50' : 'border-blue-300 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-400 cursor-pointer'
      }`}
    >
      <input
        type="file"
        accept="video/*,image/*"
        onChange={handleFileInput}
        disabled={isAnalyzing}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        id="file-upload"
      />
      <div className="flex flex-col items-center gap-4 pointer-events-none">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl" />
          <div className="relative bg-white rounded-full p-6 shadow-lg">
            <Upload className="w-12 h-12 text-blue-600" />
          </div>
        </div>
        <div className="text-center">
          <h3 className="text-gray-900 mb-2">Drop your file here or click to browse</h3>
          <p className="text-gray-500 text-sm">Supports MP4, AVI, MOV, WebM, JPG, PNG • Max 500MB • Up to 5 minutes</p>
        </div>
        <div className="flex gap-4 mt-2">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <FileVideo className="w-4 h-4" />
            <span>Videos</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <ImageIcon className="w-4 h-4" />
            <span>Images</span>
          </div>
        </div>
      </div>
    </div>
  );
}


