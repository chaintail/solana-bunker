import './styles/base.css';
import './styles/explore.css';
import './styles/scenes.css';
import './styles/rig.css';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { bakeTextures } from './textures';

bakeTextures();
// ?lite: same layout without SVG filters or blend modes (fast headless screenshots)
if (new URLSearchParams(location.search).has('lite')) document.documentElement.classList.add('lite');
createRoot(document.getElementById('root')!).render(<App />);
