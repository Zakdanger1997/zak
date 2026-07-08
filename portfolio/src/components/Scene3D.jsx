import { Canvas } from '@react-three/fiber'
import { Float, MeshDistortMaterial, Sphere, Stars } from '@react-three/drei'
import { Suspense } from 'react'

function FloatingShape({ position, scale, color, speed, distort }) {
  return (
    <Float speed={speed} rotationIntensity={1.2} floatIntensity={1.6}>
      <Sphere args={[1, 64, 64]} position={position} scale={scale}>
        <MeshDistortMaterial
          color={color}
          roughness={0.35}
          metalness={0.2}
          emissive={color}
          emissiveIntensity={0.15}
          distort={distort}
          speed={1.8}
        />
      </Sphere>
    </Float>
  )
}

function SmallCrystal({ position, color, speed }) {
  return (
    <Float speed={speed} rotationIntensity={2} floatIntensity={2}>
      <mesh position={position}>
        <octahedronGeometry args={[0.45, 0]} />
        <meshStandardMaterial
          color={color}
          roughness={0.25}
          metalness={0.3}
          emissive={color}
          emissiveIntensity={0.5}
        />
      </mesh>
    </Float>
  )
}

export default function Scene3D() {
  return (
    <Canvas
      className="!absolute inset-0"
      camera={{ position: [0, 0, 6], fov: 45 }}
      dpr={[1, 1.8]}
      gl={{ antialias: true, alpha: true }}
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.7} />
        <directionalLight position={[5, 5, 5]} intensity={2} />
        <pointLight position={[-5, -2, 2]} intensity={2} color="#22d3ee" />
        <pointLight position={[5, 2, -2]} intensity={2} color="#7c5cff" />

        <FloatingShape
          position={[2.2, 0.3, 0]}
          scale={1.35}
          color="#7c5cff"
          speed={1.4}
          distort={0.4}
        />
        <SmallCrystal position={[-2.4, 1, 1]} color="#22d3ee" speed={2.5} />
        <SmallCrystal position={[-1.6, -1.4, 0.5]} color="#7c5cff" speed={3} />
        <SmallCrystal position={[3.3, -1.6, -1]} color="#a78bfa" speed={2.2} />

        <Stars
          radius={60}
          depth={40}
          count={2500}
          factor={4}
          saturation={0}
          fade
          speed={0.6}
        />
      </Suspense>
    </Canvas>
  )
}
