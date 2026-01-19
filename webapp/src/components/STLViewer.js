import React, { Suspense, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment } from '@react-three/drei';
import STLModel from './STLModel';
import './STLViewer.css';

function STLViewer({ stlUrls, boxColor, lidColor, loading }) {
  const [models, setModels] = useState({ box: null, lid: null });

  useEffect(() => {
    if (stlUrls) {
      setModels({
        box: stlUrls.box,
        lid: stlUrls.lid
      });
    }
  }, [stlUrls]);

  return (
    <div className="stl-viewer">
      {loading && (
        <div className="viewer-overlay">
          <div className="spinner"></div>
          <p>Generating your custom container...</p>
        </div>
      )}

      {!models.box && !loading && (
        <div className="viewer-placeholder">
          <div className="placeholder-content">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <h3>No Preview Yet</h3>
            <p>Adjust parameters and click "Create" to generate your container</p>
          </div>
        </div>
      )}

      {models.box && !loading && (
        <Canvas shadows>
          <PerspectiveCamera makeDefault position={[300, 200, 300]} fov={50} />
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
          <pointLight position={[-10, -10, -5]} intensity={0.5} />

          <Suspense fallback={null}>
            <STLModel url={models.box} color={boxColor} position={[0, 0, 0]} />
            <STLModel url={models.lid} color={lidColor} position={[0, 160, 0]} />

            <Environment preset="studio" />

            {/* Ground plane */}
            <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -5, 0]}>
              <planeGeometry args={[1000, 1000]} />
              <shadowMaterial opacity={0.3} />
            </mesh>
          </Suspense>

          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={100}
            maxDistance={800}
            maxPolarAngle={Math.PI / 2}
          />

          <gridHelper args={[500, 20, '#999', '#ddd']} position={[0, -5, 0]} />
        </Canvas>
      )}

      <div className="viewer-controls">
        <small>Click and drag to rotate • Scroll to zoom • Right-click to pan</small>
      </div>
    </div>
  );
}

export default STLViewer;
