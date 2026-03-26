import AbstractView from './abstract-view.js';

const createBoardTemplate = () => `<section class="board container">
  <div class="task-modal task-modal--hidden" aria-hidden="true">
    <div class="task-modal__backdrop" role="presentation"></div>
    <div class="task-modal__dialog glass-panel" role="dialog" aria-labelledby="task-modal-title">
      <header class="task-modal__header">
        <h2 class="task-modal__title" id="task-modal-title">Новая задача</h2>
        <button type="button" class="task-modal__close" aria-label="Закрыть">&times;</button>
      </header>
      <div class="task-modal__body"></div>
    </div>
  </div>
</section>`;

export default class BoardView extends AbstractView {
  get template() {
    return createBoardTemplate();
  }
}
