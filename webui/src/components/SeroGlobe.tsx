import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface SeroGlobeProps {
  className?: string
}

// Generate Earth dot positions (continents only)
function generateEarthDots(count: number = 5000): Float32Array {
  const positions = new Float32Array(count * 3)
  const radius = 2
  
  // Land regions (lat/lon ranges)
  const landRegions = [
    // North America
    { lat: [25, 50], lon: [-125, -70], density: 0.85 },
    { lat: [50, 70], lon: [-170, -50], density: 0.7 },
    { lat: [15, 30], lon: [-115, -80], density: 0.75 },
    // South America
    { lat: [-55, -20], lon: [-75, -35], density: 0.8 },
    { lat: [-20, 12], lon: [-82, -34], density: 0.85 },
    // Europe
    { lat: [36, 60], lon: [-10, 30], density: 0.9 },
    { lat: [60, 71], lon: [5, 40], density: 0.75 },
    // Africa
    { lat: [-35, 0], lon: [10, 52], density: 0.85 },
    { lat: [0, 37], lon: [-18, 52], density: 0.85 },
    // Asia
    { lat: [5, 45], lon: [60, 100], density: 0.88 },
    { lat: [45, 75], lon: [40, 150], density: 0.82 },
    { lat: [-10, 25], lon: [95, 150], density: 0.85 },
    // Australia
    { lat: [-45, -10], lon: [110, 155], density: 0.75 },
    // Japan/Philippines
    { lat: [25, 45], lon: [125, 145], density: 0.7 },
  ]
  
  let index = 0
  const latStep = 1.5
  const lonStep = 1.5
  
  for (let lat = -90; lat <= 90 && index < count * 3; lat += latStep) {
    for (let lon = -180; lon <= 180 && index < count * 3; lon += lonStep) {
      const inLand = landRegions.some(region =>
        lat >= region.lat[0] && lat <= region.lat[1] &&
        lon >= region.lon[0] && lon <= region.lon[1] &&
        Math.random() < region.density
      )
      
      if (inLand) {
        const jitterLat = lat + (Math.random() - 0.5) * latStep * 0.8
        const jitterLon = lon + (Math.random() - 0.5) * lonStep * 0.8
        
        const phi = (90 - jitterLat) * (Math.PI / 180)
        const theta = (jitterLon + 180) * (Math.PI / 180)
        
        positions[index++] = radius * Math.sin(phi) * Math.cos(theta)
        positions[index++] = radius * Math.cos(phi)
        positions[index++] = radius * Math.sin(phi) * Math.sin(theta)
      }
    }
  }
  
  return positions.slice(0, index)
}

// Globe dots component
function GlobeDots() {
  const pointsRef = useRef<THREE.Points>(null)
  const positions = useMemo(() => generateEarthDots(5000), [])
  
  useFrame(() => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += 0.001
    }
  })
  
  const geometry = useMemo(() => {
    const geom = new THREE.BufferGeometry()
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    return geom
  }, [positions])
  
  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.015}
        color="#3b82f6"
        sizeAttenuation
        transparent
        opacity={0.8}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

// Generate orbit arc points
function generateOrbitArc(start: THREE.Vector3, end: THREE.Vector3, height: number = 0.8): THREE.Vector3[] {
  const mid = new THREE.Vector3()
    .addVectors(start, end)
    .normalize()
    .multiplyScalar(2 + height)
  
  const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
  return curve.getPoints(50)
}

// Orbit arc component
function OrbitArc({ start, end, color, progress }: { 
  start: THREE.Vector3
  end: THREE.Vector3
  color: string
  progress: number
}) {
  const points = useMemo(() => generateOrbitArc(start, end), [start, end])
  const geometry = useMemo(() => {
    const geom = new THREE.BufferGeometry().setFromPoints(points)
    return geom
  }, [points])
  
  const material = useMemo(() => new THREE.LineBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.3,
    linewidth: 2,
    blending: THREE.AdditiveBlending
  }), [color])
  
  useFrame(() => {
    if (material) {
      // Subtle pulse animation
      material.opacity = 0.3 + Math.sin(Date.now() * 0.001 + progress) * 0.1
    }
  })
  
  // Calculate pulse position along curve
  const pulseIndex = Math.floor((progress % 1) * points.length)
  const pulsePos = points[pulseIndex] || points[0]
  
  const lineObject = useMemo(() => {
    return new THREE.Line(geometry, material)
  }, [geometry, material])
  
  return (
    <group>
      {/* Arc line - use primitive for THREE.Line */}
      <primitive object={lineObject} />
      
      {/* Moving pulse */}
      <mesh position={pulsePos}>
        <sphereGeometry args={[0.04, 8, 8]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.9}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* Endpoint nodes */}
      <mesh position={start}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.7}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      <mesh position={end}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.7}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  )
}

// Orbit arcs group
function OrbitArcs() {
  const radius = 2
  const arcConfigs = useMemo(() => {
    // Generate 4-5 arcs connecting different regions
    return [
      // North America to Europe
      {
        start: new THREE.Vector3(
          radius * Math.sin(0.6) * Math.cos(-1.5),
          radius * Math.cos(0.6),
          radius * Math.sin(0.6) * Math.sin(-1.5)
        ),
        end: new THREE.Vector3(
          radius * Math.sin(0.8) * Math.cos(0.3),
          radius * Math.cos(0.8),
          radius * Math.sin(0.8) * Math.sin(0.3)
        ),
        color: '#06b6d4', // cyan
        initialProgress: 0
      },
      // Asia to North America
      {
        start: new THREE.Vector3(
          radius * Math.sin(0.7) * Math.cos(2.0),
          radius * Math.cos(0.7),
          radius * Math.sin(0.7) * Math.sin(2.0)
        ),
        end: new THREE.Vector3(
          radius * Math.sin(0.6) * Math.cos(-1.5),
          radius * Math.cos(0.6),
          radius * Math.sin(0.6) * Math.sin(-1.5)
        ),
        color: '#ec4899', // pink
        initialProgress: 0.25
      },
      // Europe to Asia
      {
        start: new THREE.Vector3(
          radius * Math.sin(0.8) * Math.cos(0.3),
          radius * Math.cos(0.8),
          radius * Math.sin(0.8) * Math.sin(0.3)
        ),
        end: new THREE.Vector3(
          radius * Math.sin(0.7) * Math.cos(2.0),
          radius * Math.cos(0.7),
          radius * Math.sin(0.7) * Math.sin(2.0)
        ),
        color: '#a855f7', // purple
        initialProgress: 0.5
      },
      // South America to Europe
      {
        start: new THREE.Vector3(
          radius * Math.sin(1.2) * Math.cos(-1.0),
          radius * Math.cos(1.2),
          radius * Math.sin(1.2) * Math.sin(-1.0)
        ),
        end: new THREE.Vector3(
          radius * Math.sin(0.8) * Math.cos(0.3),
          radius * Math.cos(0.8),
          radius * Math.sin(0.8) * Math.sin(0.3)
        ),
        color: '#06b6d4', // cyan
        initialProgress: 0.75
      },
      // Asia to Australia
      {
        start: new THREE.Vector3(
          radius * Math.sin(0.7) * Math.cos(2.0),
          radius * Math.cos(0.7),
          radius * Math.sin(0.7) * Math.sin(2.0)
        ),
        end: new THREE.Vector3(
          radius * Math.sin(1.4) * Math.cos(2.5),
          radius * Math.cos(1.4),
          radius * Math.sin(1.4) * Math.sin(2.5)
        ),
        color: '#ec4899', // pink
        initialProgress: 0.9
      }
    ]
  }, [])
  
  return (
    <group>
      {arcConfigs.map((config, i) => (
        <AnimatedOrbitArc
          key={i}
          start={config.start}
          end={config.end}
          color={config.color}
          initialProgress={config.initialProgress}
        />
      ))}
    </group>
  )
}

// Animated orbit arc with progress tracking
function AnimatedOrbitArc({ 
  start, 
  end, 
  color, 
  initialProgress 
}: { 
  start: THREE.Vector3
  end: THREE.Vector3
  color: string
  initialProgress: number
}) {
  const progressRef = useRef(initialProgress)
  
  useFrame(() => {
    progressRef.current = (progressRef.current + 0.003) % 1
  })
  
  return (
    <OrbitArc
      start={start}
      end={end}
      color={color}
      progress={progressRef.current}
    />
  )
}

// Main scene component
function GlobeScene() {
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[5, 5, 5]}
        intensity={0.8}
        castShadow={false}
      />
      
      {/* Globe dots */}
      <GlobeDots />
      
      {/* Orbit arcs */}
      <OrbitArcs />
    </>
  )
}

// Main exported component
export function SeroGlobe({ className = '' }: SeroGlobeProps) {
  const [hasError, setHasError] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)
  
  React.useEffect(() => {
    // Timeout after 3 seconds - if canvas hasn't initialized, show fallback
    const timeout = setTimeout(() => {
      if (isLoading) {
        console.warn('Globe canvas initialization timeout')
        setHasError(true)
        setIsLoading(false)
      }
    }, 3000)
    
    return () => clearTimeout(timeout)
  }, [isLoading])
  
  // Fallback if Three.js fails to load
  if (hasError) {
    return (
      <div 
        className={`relative w-full ${className} flex items-center justify-center`} 
        style={{ background: '#050B18', minHeight: '400px' }}
      >
        <div className="text-center">
          <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-400/30 to-purple-400/30 animate-pulse" />
          </div>
          <p className="text-white/60 text-sm">3D Globe Visualization</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className={`relative w-full ${className}`} style={{ background: '#050B18' }}>
      <ErrorBoundary onError={() => {
        setHasError(true)
        setIsLoading(false)
      }}>
        <Canvas
          camera={{ position: [0, 0, 6], fov: 45 }}
          gl={{ 
            antialias: true, 
            alpha: true,
            powerPreference: 'high-performance'
          }}
          style={{ background: 'transparent' }}
          dpr={[1, 2]}
          onCreated={() => {
            // Canvas successfully created
            setIsLoading(false)
          }}
        >
          <GlobeScene />
        </Canvas>
      </ErrorBoundary>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#050B18]">
          <div className="text-white/50 text-sm">Loading globe...</div>
        </div>
      )}
    </div>
  )
}

// Simple error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onError: () => void },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; onError: () => void }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    console.error('Globe error:', error)
    this.props.onError()
  }

  render() {
    if (this.state.hasError) {
      return null // Let parent handle the fallback
    }
    return this.props.children
  }
}
