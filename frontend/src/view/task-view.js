import he from 'he';
import dayjs from 'dayjs';
import AbstractView from './abstract-view.js';

const formatCreated = (iso) => {
  if (!iso) {
    return '';
  }
  return dayjs(iso).format('DD.MM.YYYY HH:mm');
};

const VALID_STATUS = new Set(['pending', 'in_progress', 'completed']);

const normalizeStatus = (status) =>
  VALID_STATUS.has(status) ? status : 'pending';

const createTaskTemplate = (task) => {
  const {
    title,
    description,
    status,
    status_label_ru: statusLabel,
    priority,
    created_at: createdAt,
  } = task;

  const statusKey = normalizeStatus(status);

  return `<article class="card card--glass" data-status="${he.encode(statusKey)}">
    <div class="card__form">
      <div class="card__inner">
        <div class="card__accent" aria-hidden="true"></div>
        <div class="card__control">
          <button type="button" class="card__btn card__btn--edit">
            изменить
          </button>
        </div>

        <div class="card__body">
          <h2 class="card__title">${he.encode(title || '')}</h2>
          <p class="card__desc">${he.encode(description || '')}</p>
        </div>

        <div class="card__settings">
          <div class="card__details card__meta">
            <p class="card__meta-line">
              <span class="card__meta-label">Статус</span>
              <span class="card__status-pill">${he.encode(statusLabel || '')}</span>
            </p>
            <p class="card__meta-line"><span class="card__meta-label">Приоритет:</span> ${Number(priority)}</p>
            <p class="card__meta-line"><span class="card__meta-label">Создано:</span> ${he.encode(formatCreated(createdAt))}</p>
          </div>
        </div>
      </div>
    </div>
  </article>`;
};

export default class TaskView extends AbstractView {
  #task = null;

  constructor(task) {
    super();
    this.#task = task;
  }

  get template() {
    return createTaskTemplate(this.#task);
  }

  setEditClickHandler = (callback) => {
    this._callback.editClick = callback;
    this.element
      .querySelector('.card__btn--edit')
      .addEventListener('click', this.#editClickHandler);
  };

  #editClickHandler = (evt) => {
    evt.preventDefault();
    this._callback.editClick();
  };
}
