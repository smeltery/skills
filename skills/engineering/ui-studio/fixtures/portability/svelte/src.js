import { mount } from 'svelte';
import App from './App.svelte';
import '@ui-studio/portability-kit';
import '@ui-studio/portability-kit/styles.css';

mount(App, { target: document.getElementById('app') });
