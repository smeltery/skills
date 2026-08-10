export const kitName = 'UI Studio Portability Kit';

export class UiStudioButton extends HTMLElement {
  connectedCallback() {
    if (this.shadowRoot) return;
    const root = this.attachShadow({ mode: 'open' });
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = this.getAttribute('label') || 'Continue';
    button.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('kit-activate', { bubbles: true }));
    });
    root.append(button);
  }
}

if (typeof window !== 'undefined' && !customElements.get('ui-studio-button')) {
  customElements.define('ui-studio-button', UiStudioButton);
}
