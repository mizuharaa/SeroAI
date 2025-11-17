import React from 'react';
import { AlertTriangle, CheckCircle2, Info, Download, Eye, Zap, Waves, Box, AudioWaveform, Grid3x3 } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';

interface DetectionResult {
  method: string;
  score: number;
  confidence: number;
  details: string[];
  icon: 'eye' | 'zap' | 'waves' | 'box' | 'audio' | 'grid';
}

interface ResultsDisplayProps {
  overallScore: number;
  results: DetectionResult[];
  fileName: string;
  processingTime: number;
  generatorHint?: string;
  feedbackId?: string;
}

const iconMap = { eye: Eye, zap: Zap, waves: Waves, box: Box, audio: AudioWaveform, grid: Grid3x3 };

export function ResultsDisplay({ overallScore, results, fileName, processingTime, generatorHint, feedbackId }: ResultsDisplayProps) {
  const [userChoice, setUserChoice] = React.useState<'AI' | 'REAL' | null>(null)
  const [notes, setNotes] = React.useState('')
  const [sent, setSent] = React.useState(false)
  const [sending, setSending] = React.useState(false)

  async function submitFeedback() {
    if (!feedbackId || !userChoice || sending) return
    setSending(true)
    try {
      await fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedbackId, userLabel: userChoice, notes })
      })
      setSent(true)
    } catch (e) {
      console.error(e)
    } finally {
      setSending(false)
    }
  }
  const getScoreColor = (score: number) => {
    if (score <= 20) return 'text-green-600';
    if (score <= 40) return 'text-lime-600';
    if (score <= 60) return 'text-yellow-600';
    if (score <= 80) return 'text-orange-600';
    return 'text-red-600';
  };
  const getScoreBgColor = (score: number) => {
    if (score <= 20) return 'from-green-500 to-emerald-600';
    if (score <= 40) return 'from-lime-500 to-green-600';
    if (score <= 60) return 'from-yellow-500 to-orange-500';
    if (score <= 80) return 'from-orange-500 to-red-500';
    return 'from-red-500 to-rose-600';
  };
  const getVerdict = (score: number) => {
    if (score <= 20) return { text: 'Highly Likely Authentic', icon: CheckCircle2, color: 'text-green-600' };
    if (score <= 40) return { text: 'Probably Authentic', icon: CheckCircle2, color: 'text-lime-600' };
    if (score <= 60) return { text: 'Uncertain - Manual Review Recommended', icon: Info, color: 'text-yellow-600' };
    if (score <= 80) return { text: 'Likely Deepfake', icon: AlertTriangle, color: 'text-orange-600' };
    return { text: 'Highly Likely Deepfake', icon: AlertTriangle, color: 'text-red-600' };
  };
  const verdict = getVerdict(overallScore);
  const VerdictIcon = verdict.icon;

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden">
        <div className={`bg-gradient-to-br ${getScoreBgColor(overallScore)} p-8 text-white`}>
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-white/80 text-sm mb-1">Deepfake Probability Score</p>
              <h2 className="text-6xl tracking-tight">{Math.round(overallScore)}%</h2>
            </div>
            <VerdictIcon className="w-12 h-12 text-white/90" />
          </div>
          <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-lg p-3">
            <VerdictIcon className="w-5 h-5" />
            <span className="text-sm">{verdict.text}</span>
          </div>
        </div>
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">File Name</p>
              <p className="text-sm text-gray-900 truncate">{fileName}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Processing Time</p>
              <p className="text-sm text-gray-900">{processingTime.toFixed(1)}s</p>
            </div>
          </div>
          {generatorHint && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-sm text-purple-900">
                <strong>Possible AI Generator:</strong> {generatorHint}
              </p>
              <p className="text-xs text-purple-700 mt-1">Based on detected fingerprints and patterns</p>
            </div>
          )}
          <div className="flex gap-2">
            <Button className="flex-1">
              <Download className="w-4 h-4 mr-2" />
              Download Report
            </Button>
            <Button variant="outline">View Details</Button>
          </div>
        </div>
      </Card>

      <Card className="p-6 space-y-6">
        <div>
          <h3 className="text-gray-900 mb-4">Detection Methods Breakdown</h3>
          <div className="grid gap-3">
            {results.map((result, idx) => {
              const Icon = iconMap[result.icon];
              return (
                <div key={idx} className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                  <div className="bg-blue-100 rounded-lg p-3">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{result.method}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full bg-gradient-to-r ${getScoreBgColor(result.score)}`}
                          style={{ width: `${result.score}%` }}
                        />
                      </div>
                      <span className={`text-sm ${getScoreColor(result.score)}`}>{result.score}%</span>
                    </div>
                  </div>
                  <Badge variant={result.confidence > 80 ? 'default' : 'secondary'}>{result.confidence}% confidence</Badge>
                </div>
              );
            })}
          </div>
        </div>
        <Separator />
        <div className="space-y-6">
          {results.map((result, idx) => {
            const Icon = iconMap[result.icon];
            return (
              <div key={idx}>
                {idx > 0 && <Separator className="my-6" />}
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 rounded-lg p-2">
                      <Icon className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="text-sm text-gray-900">{result.method}</h4>
                      <p className="text-xs text-gray-600">
                        Score: {result.score}% • Confidence: {result.confidence}%
                      </p>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <p className="text-xs text-gray-700">Key Findings:</p>
                    <ul className="space-y-1.5">
                      {result.details.map((detail, detailIdx) => (
                        <li key={detailIdx} className="text-xs text-gray-600 flex items-start gap-2">
                          <span className="text-blue-600 mt-0.5">•</span>
                          <span>{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {feedbackId && (
        <Card className="p-6 space-y-4">
          <h3 className="text-gray-900">Was this result correct?</h3>
          <div className="flex flex-wrap gap-3">
            <Button
              variant={userChoice === 'REAL' ? 'default' : 'outline'}
              onClick={() => setUserChoice('REAL')}
              className={userChoice === 'REAL' ? '' : 'bg-white dark:bg-slate-900'}
            >
              <CheckCircle2 className="w-4 h-4 mr-2" />
              Real / Authentic
            </Button>
            <Button
              variant={userChoice === 'AI' ? 'default' : 'outline'}
              onClick={() => setUserChoice('AI')}
              className={userChoice === 'AI' ? '' : 'bg-white dark:bg-slate-900'}
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              AI / Deepfake
            </Button>
          </div>
          {userChoice && !sent && (
            <div className="relative">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Optional: Add a short note (weighs lightly and helps the model focus on real errors)"
                className="w-full h-24 p-3 rounded-lg border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm text-gray-900 dark:text-gray-100 outline-none focus:ring-2 focus:ring-orange-500"
                maxLength={300}
              />
              {/* playful caret animation */}
              <div
                aria-hidden
                className="pointer-events-none absolute top-3 left-3 h-4 w-0.5 bg-orange-500 opacity-60 animate-[caret-wiggle_1.8s_ease-in-out_infinite]"
              />
              <style>{`
                @keyframes caret-wiggle {
                  0% { transform: translateX(0); opacity: .3; }
                  20% { transform: translateX(8px); opacity: .6; }
                  40% { transform: translateX(2px); opacity: .4; }
                  60% { transform: translateX(12px); opacity: .7; }
                  80% { transform: translateX(4px); opacity: .5; }
                  100% { transform: translateX(0); opacity: .3; }
                }
              `}</style>
              <div className="mt-3 flex items-center gap-3">
                <Button onClick={submitFeedback} disabled={sending} className="px-5">
                  {sending ? 'Sending...' : 'Submit Feedback'}
                </Button>
                <p className="text-xs text-gray-500">
                  Feedback slightly re-weights signals over time. Obvious noise is ignored.
                </p>
              </div>
            </div>
          )}
          {sent && (
            <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-3">
              Thank you — your feedback has been recorded.
            </div>
          )}
        </Card>
      )}
    </div>
  );
}


