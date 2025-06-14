import { useRef, useEffect } from 'react';
import Spline from '@splinetool/react-spline';

export default function AIBubble({ mode }) {
  const splineRef = useRef();

  useEffect(() => {
    const spline = splineRef.current;
    if (!spline) return;

    const modes = ['IdleOrb', 'ListenOrb', 'ThinkOrb', 'SpeakOrb'];

    modes.forEach((name) => {
      const obj = spline.findObjectByName(name);
      if (obj) {
        obj.visible = name.toLowerCase().includes(mode.toLowerCase());
      }
    });
  }, [mode]);

  return (
    <Spline
      scene="https://prod.spline.design/DR8QDbJ20prhjdir/scene.splinecode"
      ref={splineRef}
    />
  );
}
