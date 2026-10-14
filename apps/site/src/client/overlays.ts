let current: HTMLDialogElement | null = null;
let returnFocus: HTMLElement | null = null;
let scrollPosition = 0;
const registered = new WeakSet<HTMLDialogElement>();

export function closeOverlay(dialog: HTMLDialogElement) {
  dialog.close();
  restorePage(dialog);
}

function restorePage(dialog: HTMLDialogElement) {
  if (current !== dialog || dialog.open) return;
  current = null;
  document.documentElement.classList.remove("overlay-open");
  document.body.style.top = "";
  window.scrollTo({ top: scrollPosition, behavior: "instant" });
  returnFocus?.focus({ preventScroll: true });
  returnFocus = null;
}

export function openOverlay(
  dialog: HTMLDialogElement,
  trigger: HTMLElement | null,
) {
  if (current === dialog) return;
  // When switching panels, return to the original page control, not a hidden panel.
  const focusTarget = current?.contains(trigger) ? returnFocus : trigger;
  if (current) closeOverlay(current);
  registerOverlay(dialog);
  returnFocus = focusTarget;
  scrollPosition = window.scrollY;
  current = dialog;
  document.body.style.top = `-${scrollPosition}px`;
  document.documentElement.classList.add("overlay-open");
  dialog.showModal();
}

export function registerOverlay(dialog: HTMLDialogElement) {
  if (registered.has(dialog)) return;
  registered.add(dialog);
  dialog
    .querySelectorAll<HTMLButtonElement>("[data-close-overlay]")
    .forEach((button) => {
      button.addEventListener("click", () => closeOverlay(dialog));
    });
  dialog.addEventListener("click", (event) => {
    const rect = dialog.getBoundingClientRect();
    if (
      event.target === dialog &&
      (event.clientX < rect.left ||
        event.clientX > rect.right ||
        event.clientY < rect.top ||
        event.clientY > rect.bottom)
    )
      closeOverlay(dialog);
  });
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeOverlay(dialog);
  });
  dialog.addEventListener("close", () => restorePage(dialog));
}
