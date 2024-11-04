import React from 'react';
import ReactDOM from 'react-dom';
import Popup from '../Popup/Popup';

function injectSidebar() {
  const canvasApp = document.getElementById('application');
  if (canvasApp && canvasApp.classList.contains('ic-app')) {
    console.log('Canvas app found. Injecting sidebar...');

    const sidebarContainer = document.createElement('div');
    sidebarContainer.id = 'custom-sidebar-container';
    sidebarContainer.style.display = 'block';
    sidebarContainer.style.backgroundColor = 'transparent'; // Add this line

    const root = ReactDOM.createRoot(sidebarContainer);
    root.render(<Popup />);

    document.body.appendChild(sidebarContainer);

    console.log('Sidebar injected successfully');
  } else {
    console.log('Canvas app not found or not loaded yet.');
  }
}

const isCanvas = document
  .getElementById('application')
  ?.classList.contains('ic-app');

if (isCanvas) {
  injectSidebar();
} else {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        const canvasApp = document.getElementById('application');
        if (canvasApp && canvasApp.classList.contains('ic-app')) {
          injectSidebar();
          observer.disconnect();
        }
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}
