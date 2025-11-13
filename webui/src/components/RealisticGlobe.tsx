import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

export function RealisticGlobe() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = 500
    const height = 500
    canvas.width = width
    canvas.height = height

    const centerX = width / 2
    const centerY = height / 2
    const radius = 200

    const points: { x: number; y: number; z: number; origY: number; origZ: number }[] = []
    const nodeCount = 80
    for (let i = 0; i < nodeCount; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const x = radius * Math.sin(phi) * Math.cos(theta)
      const y = radius * Math.sin(phi) * Math.sin(theta)
      const z = radius * Math.cos(phi)
      points.push({ x, y: y, z: z, origY: y, origZ: z })
    }

    let rotation = 0
    function animate() {
      if (!ctx || !canvas) return
      ctx.clearRect(0, 0, width, height)
      rotation += 0.005

      points.forEach((point) => {
        const cosR = Math.cos(rotation)
        const sinR = Math.sin(rotation)
        const rotatedY = point.origY * cosR - point.origZ * sinR
        const rotatedZ = point.origY * sinR + point.origZ * cosR
        point.y = rotatedY
        point.z = rotatedZ
      })

      const sortedPoints = [...points].sort((a, b) => a.z - b.z)

      ctx.strokeStyle = 'rgba(251, 146, 60, 0.15)'
      ctx.lineWidth = 1
      sortedPoints.forEach((point, i) => {
        sortedPoints.slice(i + 1, i + 4).forEach((otherPoint) => {
          const distance = Math.sqrt(
            Math.pow(point.x - otherPoint.x, 2) +
              Math.pow(point.y - otherPoint.y, 2) +
              Math.pow(point.z - otherPoint.z, 2)
          )
          if (distance < radius * 0.8) {
            const opacity = point.z > 0 && otherPoint.z > 0 ? 0.2 : 0.05
            ctx.strokeStyle = `rgba(251, 146, 60, ${opacity})`
            ctx.beginPath()
            ctx.moveTo(centerX + point.x, centerY + point.y)
            ctx.lineTo(centerX + otherPoint.x, centerY + otherPoint.y)
            ctx.stroke()
          }
        })
      })

      sortedPoints.forEach((point) => {
        const scale = (point.z + radius) / (radius * 2)
        const size = 2 + scale * 3
        const opacity = point.z > 0 ? 0.8 : 0.3

        if (point.z > 0) {
          const gradient = ctx.createRadialGradient(
            centerX + point.x,
            centerY + point.y,
            0,
            centerX + point.x,
            centerY + point.y,
            size * 2
          )
          gradient.addColorStop(0, `rgba(251, 146, 60, ${opacity * 0.8})`)
          gradient.addColorStop(1, 'rgba(251, 146, 60, 0)')
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(centerX + point.x, centerY + point.y, size * 2, 0, Math.PI * 2)
          ctx.fill()
        }

        ctx.fillStyle = `rgba(251, 146, 60, ${opacity})`
        ctx.beginPath()
        ctx.arc(centerX + point.x, centerY + point.y, size, 0, Math.PI * 2)
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
      className="relative"
    >
      <canvas ref={canvasRef} className="w-full h-full" />
      <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-pink-500/10 rounded-full blur-3xl -z-10" />
    </motion.div>
  )
}


