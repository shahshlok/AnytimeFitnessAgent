import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function App() {
  const spline = useRef();

  function onLoad(splineApp) {
    // save the app in a ref for later use
    spline.current = splineApp;
  }

  function triggerAnimation() {
    spline.current.emitEvent('start', '6e2bae06-e4ca-49a8-b06f-1b1694d267f4 ');
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/DR8QDbJ20prhjdir/scene.splinecode"
        onLoad={onLoad}
      />
      
      <button type="button" onClick={triggerAnimation}>
        Trigger Spline Animation
      </button>
    </div>
  );
}