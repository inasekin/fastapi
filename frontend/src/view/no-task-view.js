import AbstractView from './abstract-view.js';

const createNoTaskTemplate = () => {
  return `<p class="board__no-tasks">
      Нет новых задач.
    </p>`;
};

export default class NoTaskView extends AbstractView {
  constructor(data) {
    super();
    this._data = data;
  }

  get template() {
    return createNoTaskTemplate(this._data);
  }
}
