import React, { useEffect, useState } from 'react';
import { useLoader } from '@react-three/fiber';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import * as THREE from 'three';

function STLModel({ url, color, position }) {
  const [geometry, setGeometry] = useState(null);

  useEffect(() => {
    if (!url) return;

    const loader = new STLLoader();
    loader.load(
      url,
      (loadedGeometry) => {
        // Center the geometry
        loadedGeometry.center();
        // Compute normals for proper lighting
        loadedGeometry.computeVertexNormals();
        setGeometry(loadedGeometry);
      },
      undefined,
      (error) => {
        console.error('Error loading STL:', error);
      }
    );
  }, [url]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry} position={position} castShadow receiveShadow>
      <meshStandardMaterial
        color={color}
        roughness={0.3}
        metalness={0.1}
      />
    </mesh>
  );
}

export default STLModel;
