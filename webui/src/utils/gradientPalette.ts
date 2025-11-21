/**
 * Color palette for scroll-based gradient transitions.
 * Colors shift from warm (orange/rose) to more vibrant (purple/pink) as you scroll.
 */

export interface GradientColor {
  from: string;
  via: string;
  to: string;
}

/**
 * Color palette that transitions through the spectrum as scroll progresses.
 * Each palette represents a stage in the scroll journey.
 * Enhanced with more dramatic color differences for stronger visual impact.
 */
export const GRADIENT_PALETTE: GradientColor[] = [
  // Stage 0: Start - Warm, subtle (orange/rose/amber) - VERY LIGHT
  {
    from: 'rgb(255, 247, 237)', // orange-50
    via: 'rgb(255, 241, 242)', // rose-50
    to: 'rgb(255, 251, 235)',  // amber-50
  },
  // Stage 1: Early scroll - Noticeable shift to warmer tones
  {
    from: 'rgb(253, 186, 116)', // orange-300 (much stronger)
    via: 'rgb(253, 164, 175)', // rose-300
    to: 'rgb(253, 224, 71)',   // amber-300
  },
  // Stage 2: Mid scroll - Vibrant orange/rose
  {
    from: 'rgb(251, 146, 60)', // orange-500
    via: 'rgb(251, 113, 133)', // rose-400
    to: 'rgb(252, 211, 77)',   // amber-400
  },
  // Stage 3: Further scroll - Intense colors
  {
    from: 'rgb(249, 115, 22)', // orange-600
    via: 'rgb(244, 63, 94)',   // rose-500
    to: 'rgb(245, 158, 11)',   // amber-500
  },
  // Stage 4: Deep scroll - Very vibrant pink/purple
  {
    from: 'rgb(251, 146, 60)', // orange-500
    via: 'rgb(236, 72, 153)',  // pink-500
    to: 'rgb(192, 132, 252)',  // purple-400
  },
  // Stage 5: Maximum scroll - Most colorful (vibrant purple/pink/blue)
  {
    from: 'rgb(251, 113, 133)', // rose-400
    via: 'rgb(236, 72, 153)',  // pink-500
    to: 'rgb(168, 85, 247)',   // purple-500
  },
];

/**
 * Interpolate between two gradient colors based on progress.
 */
export function interpolateGradient(
  color1: GradientColor,
  color2: GradientColor,
  progress: number
): GradientColor {
  const lerp = (a: string, b: string, t: number): string => {
    // Parse RGB values
    const rgb1 = a.match(/\d+/g)!.map(Number);
    const rgb2 = b.match(/\d+/g)!.map(Number);
    const result = rgb1.map((val, i) => Math.round(val + (rgb2[i] - val) * t));
    return `rgb(${result.join(', ')})`;
  };

  return {
    from: lerp(color1.from, color2.from, progress),
    via: lerp(color1.via, color2.via, progress),
    to: lerp(color1.to, color2.to, progress),
  };
}

/**
 * Get gradient color for a given scroll progress (0 to 1).
 * Enhanced with easing for smoother, more noticeable transitions.
 */
export function getGradientForScroll(progress: number): GradientColor {
  const clampedProgress = Math.max(0, Math.min(1, progress));
  
  // Apply easing function for more dramatic transitions
  // Ease-in-out cubic for smoother color shifts
  const easedProgress = clampedProgress < 0.5
    ? 4 * clampedProgress * clampedProgress * clampedProgress
    : 1 - Math.pow(-2 * clampedProgress + 2, 3) / 2;
  
  const stageCount = GRADIENT_PALETTE.length - 1;
  const stageIndex = easedProgress * stageCount;
  const stage = Math.floor(stageIndex);
  const stageProgress = stageIndex - stage;

  if (stage >= stageCount) {
    return GRADIENT_PALETTE[GRADIENT_PALETTE.length - 1];
  }

  return interpolateGradient(
    GRADIENT_PALETTE[stage],
    GRADIENT_PALETTE[stage + 1],
    stageProgress
  );
}

