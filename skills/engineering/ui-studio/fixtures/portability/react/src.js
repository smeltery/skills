import React from 'react';
import { createRoot } from 'react-dom/client';
import { kitName } from '@ui-studio/portability-kit';
import '@ui-studio/portability-kit/styles.css';

const app = React.createElement('section', { className: 'portability-consumer' },
  React.createElement('h1', null, `React consumes ${kitName}`),
  React.createElement('ui-studio-button', { label: 'Continue with React' })
);
createRoot(document.getElementById('app')).render(app);
