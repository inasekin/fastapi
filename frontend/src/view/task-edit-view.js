import he from 'he';
import SmartView from './smart-view.js';

const STATUS_OPTIONS = [
  { value: 'pending', label: 'в ожидании' },
  { value: 'in_progress', label: 'в работе' },
  { value: 'completed', label: 'завершено' },
];

const BLANK_TASK = {
  title: '',
  description: '',
  status: 'pending',
  priority: 0,
};

const createStatusOptions = (current) => STATUS_OPTIONS.map(
  (o) => `<option value="${o.value}" ${current === o.value ? 'selected' : ''}>${he.encode(o.label)}</option>`,
).join('');

const createTaskEditTemplate = (data) => {
  const {
    title, description, status, priority,
  } = data;

  return `<article class="card card--edit card--glass">
    <form class="card__form" method="get">
      <div class="card__inner">
        <div class="card__accent" aria-hidden="true"></div>

        <div class="card__field">
          <label class="card__field-label">Заголовок
            <input class="card__input" type="text" name="title" value="${he.encode(title)}" required maxlength="500" />
          </label>
        </div>

        <div class="card__textarea-wrap">
          <label class="card__field-label">Описание
            <textarea
              class="card__text"
              placeholder="Текст задачи..."
              name="description"
              rows="4"
            >${he.encode(description)}</textarea>
          </label>
        </div>

        <div class="card__settings">
          <div class="card__field card__field--inline">
            <label class="card__field-label">Статус
              <select class="card__select" name="status" aria-label="Статус задачи">
                ${createStatusOptions(status)}
              </select>
            </label>
            <label class="card__field-label">Приоритет
              <input class="card__input card__input--num" type="number" name="priority" min="0" max="1000" value="${Number(priority)}" />
            </label>
          </div>
        </div>

        <div class="card__status-btns">
          <button class="card__save" type="submit">сохранить</button>
          <button class="card__delete" type="button">удалить</button>
        </div>
      </div>
    </form>
  </article>`;
};

export default class TaskEditView extends SmartView {
  constructor(task = BLANK_TASK) {
    super();
    this._data = TaskEditView.parseTaskToData(task);

    this.#setInnerHandlers();
  }

  get template() {
    return createTaskEditTemplate(this._data);
  }

  reset = (task) => {
    this.updateData(TaskEditView.parseTaskToData(task));
  };

  restoreHandlers = () => {
    this.#setInnerHandlers();
    this.setFormSubmitHandler(this._callback.formSubmit);
    this.setDeleteClickHandler(this._callback.deleteClick);
  };

  setFormSubmitHandler = (callback) => {
    this._callback.formSubmit = callback;
    this.element
      .querySelector('form')
      .addEventListener('submit', this.#formSubmitHandler);
  };

  setDeleteClickHandler = (callback) => {
    this._callback.deleteClick = callback;
    this.element
      .querySelector('.card__delete')
      .addEventListener('click', this.#formDeleteClickHandler);
  };

  #setInnerHandlers = () => {
    this.element.querySelector('[name="title"]').addEventListener('input', this.#titleInputHandler);
    this.element
      .querySelector('[name="description"]')
      .addEventListener('input', this.#descriptionInputHandler);
    this.element
      .querySelector('[name="status"]')
      .addEventListener('change', this.#statusChangeHandler);
    this.element
      .querySelector('[name="priority"]')
      .addEventListener('input', this.#priorityInputHandler);
  };

  #titleInputHandler = (evt) => {
    this.updateData({ title: evt.target.value }, true);
  };

  #descriptionInputHandler = (evt) => {
    this.updateData({ description: evt.target.value }, true);
  };

  #statusChangeHandler = (evt) => {
    this.updateData({ status: evt.target.value });
  };

  #priorityInputHandler = (evt) => {
    const value = Number(evt.target.value);
    this.updateData({ priority: Number.isFinite(value) ? value : 0 }, true);
  };

  #formSubmitHandler = async (evt) => {
    evt.preventDefault();
    await this._callback.formSubmit(TaskEditView.parseDataToTask(this._data));
  };

  #formDeleteClickHandler = (evt) => {
    evt.preventDefault();
    this._callback.deleteClick(TaskEditView.parseDataToTask(this._data));
  };

  static parseTaskToData = (task) => ({
    id: task.id,
    title: task.title ?? '',
    description: task.description ?? '',
    status: task.status ?? 'pending',
    priority: task.priority ?? 0,
  });

  static parseDataToTask = (data) => ({
    id: data.id,
    title: data.title,
    description: data.description,
    status: data.status,
    priority: data.priority,
  });
}
