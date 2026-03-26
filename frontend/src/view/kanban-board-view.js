import AbstractView from './abstract-view.js';

const COLUMNS = [
  { status: 'pending', title: 'В ожидании' },
  { status: 'in_progress', title: 'В работе' },
  { status: 'completed', title: 'Завершено' },
];

const columnHtml = ({ status, title }) => `
  <div class="col col-12 col-md-6 col-lg-4 kanban__col" data-status="${status}">
    <div class="kanban__column glass-panel">
      <div class="kanban__column-head">
        <span class="kanban__column-title">${title}</span>
      </div>
      <div class="kanban__list"></div>
    </div>
  </div>
`;

const createTemplate = () => `
  <div class="kanban">
    <div class="row kanban__row">
      ${COLUMNS.map(columnHtml).join('')}
    </div>
  </div>
`;

export default class KanbanBoardView extends AbstractView {
  get template() {
    return createTemplate();
  }

  getListElForStatus(status) {
    const allowed = COLUMNS.map((c) => c.status);
    const key = allowed.includes(status) ? status : 'pending';
    return this.element.querySelector(`[data-status="${key}"] .kanban__list`);
  }
}
