"""
Structured logging for video analysis results.

This module writes analysis results to JSON files and generates
human-readable summaries.
"""

import json
import os
from typing import Dict, Any, Tuple
from datetime import datetime
from core.types_analysis import VideoAnalysisResult, FeatureReason


class AnalysisLogger:
    """Logger for video analysis results."""
    
    def __init__(self, log_dir: str = "logs/analysis"):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_analysis(self, result: VideoAnalysisResult) -> str:
        """
        Log analysis result to JSON file.
        
        Args:
            result: VideoAnalysisResult to log
            
        Returns:
            Path to the log file
        """
        # Generate log filename
        log_filename = f"{result.video_id}.json"
        log_path = os.path.join(self.log_dir, log_filename)
        
        # Convert to dictionary
        log_data = result.to_dict()
        
        # Write to file
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        return log_path
    
    def generate_summary(self, result: VideoAnalysisResult) -> str:
        """
        Generate human-readable summary string.
        
        Args:
            result: VideoAnalysisResult to summarize
            
        Returns:
            Human-readable summary string
        """
        score = result.deepfake_score
        label = result.label
        
        # Determine severity level
        if score >= 0.8:
            severity = "Very High"
        elif score >= 0.6:
            severity = "High"
        elif score >= 0.4:
            severity = "Moderate"
        elif score >= 0.2:
            severity = "Low"
        else:
            severity = "Very Low"
        
        # Get top contributing features
        top_reasons = sorted(
            result.reasons,
            key=lambda r: abs(r.contribution),
            reverse=True
        )[:3]
        
        # Build summary
        summary_parts = [
            f"Deepfake probability {score:.2f} ({severity})"
        ]
        
        if top_reasons:
            reason_descriptions = []
            for reason in top_reasons:
                direction = "increased" if reason.contribution > 0 else "decreased"
                reason_descriptions.append(
                    f"{reason.name.replace('_', ' ')} {direction} probability"
                )
            summary_parts.append("– " + ", ".join(reason_descriptions))
        
        summary = ". ".join(summary_parts) + "."
        
        return summary
    
    def log_and_summarize(self, result: VideoAnalysisResult) -> tuple[str, str]:
        """
        Log analysis and generate summary.
        
        Args:
            result: VideoAnalysisResult to log
            
        Returns:
            Tuple of (log_path, summary_string)
        """
        # Generate summary
        summary = self.generate_summary(result)
        result.summary = summary
        
        # Log to file
        log_path = self.log_analysis(result)
        
        # Print to terminal
        self.print_analysis(result, log_path)
        
        return log_path, summary
    
    def print_analysis(self, result: VideoAnalysisResult, log_path: str):
        """
        Print analysis results to terminal in a structured format.
        
        Args:
            result: VideoAnalysisResult to print
            log_path: Path to log file
        """
        print("\n" + "=" * 80)
        print("DEEPFAKE DETECTION ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Video: {os.path.basename(result.video_path)}")
        print(f"Video ID: {result.video_id}")
        print(f"Analysis Time: {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("FEATURE SCORES:")
        print("-" * 80)
        for feature_name, value in result.features.items():
            normalized = result.normalized_features.get(feature_name, 0.0)
            print(f"  {feature_name:35s}: {value:6.3f} (normalized: {normalized:6.3f})")
        print()
        
        print("TOP CONTRIBUTING FEATURES:")
        print("-" * 80)
        for i, reason in enumerate(result.reasons[:5], 1):
            direction = "↑" if reason.contribution > 0 else "↓"
            print(f"  {i}. {reason.name:35s}: {direction} {abs(reason.contribution):6.3f} "
                  f"(weight: {reason.weight:.2f}, z-score: {reason.normalized_value:6.3f})")
        print()
        
        print("FINAL DECISION:")
        print("-" * 80)
        print(f"  Deepfake Score: {result.deepfake_score:.4f}")
        print(f"  Label: {result.label.upper()}")
        print(f"  Decision Threshold: {result.parameters.get('decision_threshold', 0.6):.2f}")
        print()
        
        print("SUMMARY:")
        print("-" * 80)
        print(f"  {result.summary}")
        print()
        
        print("DEBUG INFO:")
        print("-" * 80)
        print(f"  Frames Analyzed: {len(result.frame_records)}")
        print(f"  Frames with Face: {sum(1 for fr in result.frame_records if fr.face_detected)}")
        print(f"  Log File: {log_path}")
        print("=" * 80 + "\n")

