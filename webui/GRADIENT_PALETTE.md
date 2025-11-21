# Scroll-Based Gradient Color Palette

## Overview

The landing page now features a dynamic gradient background that shifts colors as you scroll, transitioning from warm, subtle tones to vibrant, colorful hues.

## Color Palette Stages

The gradient transitions through 6 stages as you scroll:

### Stage 0: Start (Scroll Progress: 0.0)
- **From**: `rgb(255, 247, 237)` - Soft orange-50
- **Via**: `rgb(255, 241, 242)` - Soft rose-50
- **To**: `rgb(255, 251, 235)` - Soft amber-50
- **Mood**: Warm, subtle, welcoming

### Stage 1: Early Scroll (Scroll Progress: 0.2)
- **From**: `rgb(254, 243, 199)` - Orange-100
- **Via**: `rgb(255, 228, 230)` - Rose-100
- **To**: `rgb(254, 240, 138)` - Amber-100
- **Mood**: Slightly more vibrant

### Stage 2: Mid Scroll (Scroll Progress: 0.4)
- **From**: `rgb(253, 230, 138)` - Orange-200
- **Via**: `rgb(254, 205, 211)` - Rose-200
- **To**: `rgb(253, 224, 71)` - Amber-200
- **Mood**: More colorful, energetic

### Stage 3: Further Scroll (Scroll Progress: 0.6)
- **From**: `rgb(251, 191, 36)` - Orange-300
- **Via**: `rgb(251, 182, 206)` - Rose-300
- **To**: `rgb(252, 211, 77)` - Amber-300
- **Mood**: Vibrant, dynamic

### Stage 4: Deep Scroll (Scroll Progress: 0.8)
- **From**: `rgb(249, 115, 22)` - Orange-500
- **Via**: `rgb(244, 63, 94)` - Rose-500
- **To**: `rgb(245, 158, 11)` - Amber-500
- **Mood**: Very vibrant, intense

### Stage 5: Maximum Scroll (Scroll Progress: 1.0)
- **From**: `rgb(251, 146, 60)` - Orange-500
- **Via**: `rgb(236, 72, 153)` - Pink-500
- **To**: `rgb(168, 85, 247)` - Purple-500
- **Mood**: Most colorful, full spectrum

## Implementation

### Files
- **`utils/gradientPalette.ts`**: Color palette definitions and interpolation logic
- **`components/HeroSection.tsx`**: Scroll-based gradient application
- **`styles/performance.css`**: Performance optimizations

### How It Works

1. **Scroll Progress Tracking**: Uses `useScroll` from Framer Motion to track scroll position
2. **Color Interpolation**: `getGradientForScroll()` function interpolates between palette stages
3. **Smooth Transitions**: Colors smoothly blend between stages as you scroll
4. **GPU Acceleration**: Uses `will-change` and `transform: translateZ(0)` for hardware acceleration

## Performance Optimizations

### Applied Optimizations

1. **Reduced Keyframes**: Simplified `useTransform` calls (removed intermediate keyframes)
2. **GPU Acceleration**: Added `will-change` and `transform: translateZ(0)` to animated elements
3. **Reduced Blur Elements**: Removed one blur element (from 3 to 2) to reduce GPU load
4. **CSS Containment**: Added `contain: layout style paint` to isolate rendering
5. **Optimized Transforms**: All animations use `transform` instead of `position` changes
6. **Memoized Transforms**: Gradient calculations are memoized in `useTransform`

### Performance Tips

- **Blur Effects**: `blur-3xl` is GPU-intensive; reduced from 3 to 2 elements
- **Will-Change**: Applied strategically to elements that animate during scroll
- **Transform**: All animations use `transform` (GPU-accelerated) instead of `top/left`
- **Isolation**: CSS `isolation: isolate` prevents unnecessary repaints

## Customization

To adjust the color palette, edit `utils/gradientPalette.ts`:

```typescript
export const GRADIENT_PALETTE: GradientColor[] = [
  // Add or modify stages here
  {
    from: 'rgb(...)',
    via: 'rgb(...)',
    to: 'rgb(...)',
  },
  // ...
];
```

## Browser Compatibility

- Uses CSS `will-change` for modern browsers
- Falls back gracefully on older browsers
- Respects `prefers-reduced-motion` for accessibility

