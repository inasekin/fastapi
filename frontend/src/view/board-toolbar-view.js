import AbstractView from './abstract-view.js';

const createTemplate = () => `
  <div class="board-toolbar glass-panel board-toolbar--compact" role="region" aria-label="Фильтры и сортировка задач">
    <div class="bt-compact">
      <div class="bt-compact__group">
        <label class="bt-compact__item">
          <span class="bt-compact__lbl">Сортировка</span>
          <select class="bt-compact__ctrl" name="sort_by" aria-label="Поле сортировки">
            <option value="created_at">Дата</option>
            <option value="title">Заголовок</option>
            <option value="status">Статус</option>
          </select>
        </label>
        <label class="bt-compact__item">
          <span class="bt-compact__lbl">Порядок</span>
          <select class="bt-compact__ctrl" name="order" aria-label="Порядок">
            <option value="desc">↓ Убыв.</option>
            <option value="asc">↑ Возр.</option>
          </select>
        </label>
        <button class="ui-btn ui-btn--sm ui-btn--solid" type="button" data-action="apply-sort">Применить</button>
        <button class="ui-btn ui-btn--sm ui-btn--outline" type="button" data-action="reset-list">Все</button>
      </div>
      <div class="bt-compact__group bt-compact__group--search">
        <input
          class="bt-compact__ctrl bt-compact__ctrl--search"
          type="search"
          name="search"
          placeholder="Поиск в заголовке и описании…"
          aria-label="Поиск"
          autocomplete="off"
        />
        <button class="ui-btn ui-btn--sm ui-btn--solid" type="button" data-action="search">Найти</button>
      </div>
      <div class="bt-compact__group">
        <label class="bt-compact__item bt-compact__item--n">
          <span class="bt-compact__lbl">Топ N</span>
          <input
            class="bt-compact__ctrl bt-compact__ctrl--num"
            type="number"
            name="top_n"
            min="1"
            max="100"
            value="5"
            aria-label="Количество для топа по приоритету"
          />
        </label>
        <button class="ui-btn ui-btn--sm ui-btn--solid" type="button" data-action="top">Топ</button>
      </div>
    </div>
  </div>
`;

export default class BoardToolbarView extends AbstractView {
  get template() {
    return createTemplate();
  }

  setHandlers = (handlers) => {
    this._handlers = handlers;
    this.element.querySelector('[data-action="apply-sort"]').addEventListener('click', () => {
      const sortBy = this.element.querySelector('[name="sort_by"]').value;
      const order = this.element.querySelector('[name="order"]').value;
      this._handlers.onApplySort(sortBy, order);
    });
    this.element.querySelector('[data-action="reset-list"]').addEventListener('click', () => {
      const sortBy = this.element.querySelector('[name="sort_by"]').value;
      const order = this.element.querySelector('[name="order"]').value;
      this._handlers.onResetList(sortBy, order);
    });
    this.element.querySelector('[data-action="search"]').addEventListener('click', () => {
      const q = this.element.querySelector('[name="search"]').value;
      this._handlers.onSearch(q);
    });
    this.element.querySelector('[data-action="top"]').addEventListener('click', () => {
      const n = Number(this.element.querySelector('[name="top_n"]').value) || 5;
      this._handlers.onTop(n);
    });
  };

  syncSortUi = (sortBy, order) => {
    this.element.querySelector('[name="sort_by"]').value = sortBy;
    this.element.querySelector('[name="order"]').value = order;
  };
}
