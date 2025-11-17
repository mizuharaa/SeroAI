import React, { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Line, PointMaterial, Points } from '@react-three/drei'
import * as THREE from 'three'

interface SimpleGlobeProps {
  className?: string
}

const RADIUS = 1
const DOT_COUNT = 5000
const PANEL_BACKGROUND =
  'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.06), rgba(6,9,18,0.95) 70%)'

type OrbitConfig = {
  tilt: [number, number, number]
  radius: number
  color: string
  speed: number
}

const ORBITS: OrbitConfig[] = [
  { tilt: [Math.PI / 2.3, 0, 0], radius: 1.25, color: '#7DE0FF', speed: 0.06 },
  { tilt: [Math.PI / 2.5, 0, Math.PI / 2], radius: 1.25, color: '#F472B6', speed: 0.055 },
  { tilt: [Math.PI / 2.4, Math.PI / 3.6, Math.PI / 3], radius: 1.18, color: '#A78BFA', speed: 0.045 },
  { tilt: [Math.PI / 1.9, -Math.PI / 4, Math.PI / 5], radius: 1.32, color: '#FBBF24', speed: 0.05 }
]

const createOrbitCurve = (tilt: [number, number, number], radius: number, segments = 200) => {
  const points: THREE.Vector3[] = []
  const euler = new THREE.Euler(tilt[0], tilt[1], tilt[2])
  const quat = new THREE.Quaternion().setFromEuler(euler)
  for (let i = 0; i <= segments; i++) {
    const angle = (i / segments) * Math.PI * 2
    const base = new THREE.Vector3(Math.cos(angle) * radius, Math.sin(angle) * radius, 0)
    base.applyQuaternion(quat)
    points.push(base)
  }
  return points
}

function OceanSphere() {
  return (
    <mesh>
      <sphereGeometry args={[RADIUS, 64, 64]} />
      <meshStandardMaterial
        color="#070E1F"
        transparent
        opacity={0.82}
        roughness={0.85}
        metalness={0.05}
      />
      <mesh>
        <sphereGeometry args={[RADIUS + 0.01, 64, 64]} />
        <meshBasicMaterial color="#111A2E" transparent opacity={0.45} />
      </mesh>
    </mesh>
  )
}

function DotSphere() {
  const positions = useMemo(() => {
    const pos = new Float32Array(DOT_COUNT * 3)
    const offset = 2 / DOT_COUNT
    const increment = Math.PI * (3 - Math.sqrt(5))

    for (let i = 0; i < DOT_COUNT; i++) {
      const y = i * offset - 1 + offset / 2
      const r = Math.sqrt(1 - y * y)
      const phi = i * increment
      const x = Math.cos(phi) * r
      const z = Math.sin(phi) * r
      pos[i * 3 + 0] = x * 1.02
      pos[i * 3 + 1] = y * 1.02
      pos[i * 3 + 2] = z * 1.02
    }
    return pos
  }, [])

  const materialRef = useRef<THREE.PointsMaterial>(null)

  useFrame(({ clock }) => {
    if (materialRef.current) {
      const wave = 0.6 + Math.sin(clock.elapsedTime * 0.8) * 0.1
      materialRef.current.opacity = wave
      materialRef.current.size = 0.014 + Math.sin(clock.elapsedTime * 0.6) * 0.002
    }
  })

  return (
    <Points positions={positions}>
      <PointMaterial
        ref={materialRef}
        color="#FFC7A2"
        size={0.015}
        sizeAttenuation
        depthWrite={false}
        transparent
        opacity={0.7}
      />
    </Points>
  )
}

function OrbitTrack({ orbit }: { orbit: OrbitConfig }) {
  const curve = useMemo(() => {
    const pts = createOrbitCurve(orbit.tilt, orbit.radius)
    return new THREE.CatmullRomCurve3(pts, true, 'catmullrom', 0.5)
  }, [orbit])

  const points = useMemo(() => curve.getPoints(200), [curve])
  const nodeRef = useRef<THREE.Mesh>(null)
  const tRef = useRef(Math.random())

  useFrame((_, delta) => {
    if (!nodeRef.current) return
    tRef.current = (tRef.current + delta * orbit.speed) % 1
    const pos = curve.getPointAt(tRef.current)
    nodeRef.current.position.copy(pos)

    const front = pos.z >= 0
    nodeRef.current.visible = front
    const mat = nodeRef.current.material as THREE.MeshBasicMaterial
    mat.opacity = front ? 1 : 0

    const pulse = 0.9 + Math.sin(tRef.current * Math.PI * 2) * 0.08
    nodeRef.current.scale.setScalar(pulse)
  })

  return (
    <>
      <Line points={points} color={orbit.color} lineWidth={1} transparent opacity={0.45} />
      <mesh ref={nodeRef}>
        <sphereGeometry args={[0.022, 16, 16]} />
        <meshBasicMaterial color={orbit.color} transparent opacity={1} />
      </mesh>
    </>
  )
}

function OrbitLayer() {
  return (
    <>
      {ORBITS.map((orbit, idx) => (
        <OrbitTrack key={idx} orbit={orbit} />
      ))}
    </>
  )
}

function GlobeRoot() {
  const groupRef = useRef<THREE.Group>(null)

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.1
    }
  })

  return (
    <group ref={groupRef}>
      <OceanSphere />
      <DotSphere />
      <OrbitLayer />
    </group>
  )
}

export function SimpleGlobe({ className = '' }: SimpleGlobeProps) {
  const [isClient, setIsClient] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient || hasError) {
    return (
      <div className={`relative ${className}`} style={{ background: PANEL_BACKGROUND }}>
        <FallbackVisual />
      </div>
    )
  }

  return (
    <div className={`relative ${className}`} style={{ background: PANEL_BACKGROUND }}>
      <ErrorBoundary onError={() => setHasError(true)}>
        <Suspense fallback={<FallbackVisual />}>
          <Canvas gl={{ antialias: false, alpha: true }} camera={{ position: [0, 0, 3.2], fov: 45 }} dpr={[1, 2]}>
            <ambientLight intensity={0.4} />
            <directionalLight position={[3, 3, 3]} intensity={0.8} />
            <GlobeRoot />
          </Canvas>
        </Suspense>
      </ErrorBoundary>
    </div>
  )
}

function FallbackVisual() {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400/30 to-purple-400/30 animate-pulse" />
        </div>
        <p className="text-white/60 text-xs">Initializing globeâ€¦</p>
      </div>
    </div>
  )
}

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
      return <FallbackVisual />
    }
    return this.props.children
  }
}
