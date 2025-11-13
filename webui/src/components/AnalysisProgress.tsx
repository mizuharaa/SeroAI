import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import { Progress } from './ui/progress';

interface AnalysisMethod {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'analyzing' | 'complete';
  score?: number;
}

interface AnalysisProgressProps {
  methods: AnalysisMethod[];
  overallProgress: number;
}

export function AnalysisProgress({ methods, overallProgress }: AnalysisProgressProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-gray-900">Overall Progress</h3>
          <span className="text-sm text-gray-600">{Math.round(overallProgress)}%</span>
        </div>
        <Progress value={overallProgress} className="h-2" />
      </div>

      <div className="space-y-3">
        <h4 className="text-sm text-gray-700">Detection Methods</h4>
        <div className="space-y-2">
          {methods.map(method => (
            <div
              key={method.id}
              className={`flex items-start gap-3 p-4 rounded-lg border transition-all ${
                method.status === 'complete'
                  ? 'bg-green-50 border-green-200'
                  : method.status === 'analyzing'
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="mt-0.5">
                {method.status === 'complete' ? (
                  <div className="bg-green-500 rounded-full p-1">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                ) : method.status === 'analyzing' ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : (
                  <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm text-gray-900">{method.name}</p>
                  {method.score !== undefined && (
                    <span className="text-xs text-gray-600 whitespace-nowrap">{method.score}%</span>
                  )}
                </div>
                <p className="text-xs text-gray-600 mt-0.5">{method.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


