import AbstractView from './abstract-view.js';
import { MenuItem } from '../utils/constants.js';

const createSiteMenuTemplate = () => `<div class="control__btn-wrap">
    <input
      type="radio"
      name="control"
      id="control__new-task"
      class="control__input visually-hidden"
      value="${MenuItem.ADD_NEW_TASK}"
    />
    <label for="control__new-task" class="control__button">Новая задача</label>
        <input
      type="radio"
      name="control"
      id="control__task"
      class="control__input visually-hidden"
      value="${MenuItem.TASKS}"
      checked
    />
    <label for="control__task" class="control__label" style="display: none;">ЗАДАЧКИ</label>
  </div>`;

export default class SiteMenuView extends AbstractView {
  get template() {
    return createSiteMenuTemplate();
  }

  setMenuClickHandler = (callback) => {
    this._callback.menuClick = callback;
    this.element.addEventListener('change', this.#menuClickHandler);
  };

  setMenuItem = (menuItem) => {
    const item = this.element.querySelector(`[value=${menuItem}]`);

    if (item !== null) {
      item.checked = true;
    }
  };

  #menuClickHandler = (evt) => {
    evt.preventDefault();
    this._callback.menuClick(evt.target.value);
  };
}
