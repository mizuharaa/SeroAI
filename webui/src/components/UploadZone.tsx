import React, { useCallback, useState } from 'react';
import { Upload, FileVideo, Image as ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isAnalyzing: boolean;
}

export function UploadZone({ onFileSelect, isAnalyzing }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (isAnalyzing) return;
      const file = e.dataTransfer.files[0];
      if (file && (file.type.startsWith('video/') || file.type.startsWith('image/'))) {
        onFileSelect(file);
      }
    },
    [onFileSelect, isAnalyzing]
  );
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!isAnalyzing) setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <motion.div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      animate={isDragging ? { scale: 1.02 } : { scale: 1 }}
      className={`relative border-2 border-dashed rounded-2xl p-8 md:p-12 transition-all ${
        isAnalyzing
          ? 'border-gray-300 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/50 cursor-not-allowed opacity-50'
          : isDragging
          ? 'border-orange-400 bg-gradient-to-br from-orange-50/80 to-pink-50/80 dark:from-orange-950/30 dark:to-pink-950/30 cursor-pointer shadow-2xl'
          : 'border-orange-300 dark:border-orange-700 bg-gradient-to-br from-orange-50/50 to-pink-50/50 dark:from-orange-950/20 dark:to-pink-950/20 hover:bg-gradient-to-br hover:from-orange-50 hover:to-pink-50 dark:hover:from-orange-950/30 dark:hover:to-pink-950/30 hover:border-orange-400 dark:hover:border-orange-600 cursor-pointer shadow-lg hover:shadow-2xl'
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
      <div className="flex flex-col items-center gap-6 pointer-events-none">
        <motion.div
          className="relative"
          animate={isDragging ? { scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] } : {}}
          transition={{ duration: 2, repeat: isDragging ? Infinity : 0 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-orange-400/30 via-pink-400/20 to-purple-400/30 rounded-full blur-2xl" />
          <motion.div
            className="relative bg-gradient-to-br from-orange-500 to-pink-500 rounded-full p-6 shadow-2xl"
            whileHover={{ scale: 1.1 }}
          >
            <Upload className="w-10 h-10 md:w-12 md:h-12 text-white" strokeWidth={2.5} />
          </motion.div>
        </motion.div>
        <div className="text-center space-y-2">
          <h3 className="text-lg md:text-xl font-bold text-gray-900 dark:text-white">
            {isDragging ? 'Drop your file here' : 'Drop your file here or click to browse'}
          </h3>
          <p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
            Supports MP4, AVI, MOV, WebM, JPG, PNG • Max 500MB • Up to 5 minutes
          </p>
        </div>
        <div className="flex gap-6 mt-2">
          <motion.div
            className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
            whileHover={{ scale: 1.1 }}
          >
            <div className="p-2 rounded-lg bg-blue-500/10 dark:bg-blue-500/20">
              <FileVideo className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <span>Videos</span>
          </motion.div>
          <motion.div
            className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300"
            whileHover={{ scale: 1.1 }}
          >
            <div className="p-2 rounded-lg bg-purple-500/10 dark:bg-purple-500/20">
              <ImageIcon className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            </div>
            <span>Images</span>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}


