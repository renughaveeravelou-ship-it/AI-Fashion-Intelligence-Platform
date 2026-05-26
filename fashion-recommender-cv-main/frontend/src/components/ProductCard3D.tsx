import { Canvas } from "@react-three/fiber";
import { OrbitControls, Float, useTexture } from "@react-three/drei";
import { Suspense } from "react";
import { FashionItem } from "../lib/api";

function ProductMesh({ url }: { url: string }) {
  const texture = useTexture(url);
  return (
    <Float speed={2} rotationIntensity={0.4} floatIntensity={0.8}>
      <mesh>
        <boxGeometry args={[2.2, 2.8, 0.15]} />
        <meshStandardMaterial map={texture} roughness={0.4} metalness={0.1} />
      </mesh>
    </Float>
  );
}

export default function ProductCard3D({ item }: { item: FashionItem | null }) {
  if (!item) {
    return (
      <div className="glass rounded-3xl h-[420px] flex items-center justify-center text-zinc-500">
        Select a product from Discover
      </div>
    );
  }

  return (
    <div className="glass rounded-3xl h-[420px] overflow-hidden relative">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} />
        <pointLight position={[-3, 2, 2]} color="var(--color-accent)" intensity={0.6} />
        <Suspense fallback={null}>
          <ProductMesh url={item.url} />
        </Suspense>
        <OrbitControls enableZoom autoRotate autoRotateSpeed={1.2} />
      </Canvas>
      <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/80">
        <p className="font-semibold">{item.category}</p>
      </div>
    </div>
  );
}
