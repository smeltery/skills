import { createApp, h } from 'vue';
import { kitName } from '@ui-studio/portability-kit';
import '@ui-studio/portability-kit/styles.css';

createApp({
  render() {
    return h('section', { class: 'portability-consumer' }, [
      h('h1', `Vue consumes ${kitName}`),
      h('ui-studio-button', { label: 'Continue with Vue' })
    ]);
  }
}).mount('#app');
