"""
Patch temporal features into existing features.csv without re-extracting everything.

This is MUCH faster than full re-extraction (30-60 min vs 4-5 days).
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.temporal import optical_flow_oddity, rppg_coherence

def patch_temporal_features(csv_path: str = "data/training/features.csv"):
    """Patch temporal features into existing CSV."""
    
    print(f"Loading existing features from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")
    
    # Check if temporal columns exist and are all NaN
    if 'temp.flow_oddity' not in df.columns or 'temp.rppg' not in df.columns:
        print("ERROR: Temporal columns not found in CSV")
        return
    
    nan_count_flow = df['temp.flow_oddity'].isna().sum()
    nan_count_rppg = df['temp.rppg'].isna().sum()
    
    print(f"Current NaN counts: flow_oddity={nan_count_flow}, rppg={nan_count_rppg}")
    
    if nan_count_flow == 0 and nan_count_rppg == 0:
        print("All temporal features already populated! Nothing to do.")
        return
    
    # Process each row
    print("\nPatching temporal features...")
    total_rows = len(df)
    
    for idx in range(total_rows):
        row = df.iloc[idx]
        
        # Skip if already has values
        flow_val = row['temp.flow_oddity']
        rppg_val = row['temp.rppg']
        if pd.notna(flow_val) and pd.notna(rppg_val):
            continue
        
        video_path_raw = row['path']
        video_id = row['id']
        
        # Ensure video_path is a string
        video_path = str(video_path_raw)
        
        # Convert relative path to absolute
        if not os.path.isabs(video_path):
            video_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), video_path)
        
        if not os.path.exists(video_path):
            print(f"[{idx+1}/{total_rows}] SKIP: File not found: {video_id}")
            continue
        
        print(f"[{idx+1}/{total_rows}] Processing: {video_id}")
        
        try:
            # Extract temporal features
            flow_result = optical_flow_oddity(video_path)
            rppg_result = rppg_coherence(video_path)
            
            # Update DataFrame
            df.at[idx, 'temp.flow_oddity'] = flow_result.get('oddity_score')
            df.at[idx, 'temp.rppg'] = rppg_result.get('rppg_score')
            
            # Save every 10 rows (in case of interruption)
            if (idx + 1) % 10 == 0:
                df.to_csv(csv_path, index=False)
                print(f"  → Saved checkpoint at row {idx+1}")
        
        except Exception as e:
            print(f"  → ERROR: {e}")
            # Leave as NaN, continue
            continue
    
    # Final save
    print("\nSaving final results...")
    df.to_csv(csv_path, index=False)
    
    # Report
    final_nan_flow = df['temp.flow_oddity'].isna().sum()
    final_nan_rppg = df['temp.rppg'].isna().sum()
    
    print(f"\n✓ Complete!")
    print(f"Final NaN counts: flow_oddity={final_nan_flow}, rppg={final_nan_rppg}")
    print(f"Successfully patched: flow_oddity={nan_count_flow - final_nan_flow}, rppg={nan_count_rppg - final_nan_rppg}")
    
    if final_nan_flow > len(df) * 0.5 or final_nan_rppg > len(df) * 0.5:
        print("\n⚠ WARNING: >50% temporal features still NaN. Training may fail.")
        print("Consider checking video files or re-running full extraction.")
    else:
        print("\n✓ Ready to train! Run: python -m scripts.train_fusion")


if __name__ == "__main__":
    patch_temporal_features()

