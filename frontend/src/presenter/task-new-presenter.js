import TaskEditView from '../view/task-edit-view.js';
import { remove, render, RenderPosition } from '../utils/render.js';
import { UserAction, UpdateType } from '../utils/constants.js';

export default class TaskNewPresenter {
  #changeData;

  #taskEditComponent = null;

  #destroyCallback = null;

  #modal = null;

  #modalBody = null;

  #backdrop = null;

  #closeBtn = null;

  #dialog = null;

  #boundBackdrop = null;

  #boundClose = null;

  constructor(changeData) {
    this.#changeData = changeData;
  }

  setBoardView = (boardView) => {
    const root = boardView.element.querySelector('.task-modal');
    if (!root) {
      return;
    }
    this.#modal = root;
    this.#modalBody = root.querySelector('.task-modal__body');
    this.#backdrop = root.querySelector('.task-modal__backdrop');
    this.#closeBtn = root.querySelector('.task-modal__close');
    this.#dialog = root.querySelector('.task-modal__dialog');

    this.#boundBackdrop = () => {
      this.destroy();
    };
    this.#boundClose = () => {
      this.destroy();
    };

    this.#backdrop.addEventListener('click', this.#boundBackdrop);
    this.#closeBtn.addEventListener('click', this.#boundClose);
    this.#dialog.addEventListener('click', (evt) => {
      evt.stopPropagation();
    });
  };

  init = (callback) => {
    this.#destroyCallback = callback;

    if (this.#taskEditComponent !== null || !this.#modalBody) {
      return;
    }

    this.#taskEditComponent = new TaskEditView();
    this.#taskEditComponent.setFormSubmitHandler(this.#handleFormSubmit);
    this.#taskEditComponent.setDeleteClickHandler(this.#handleDeleteClick);

    this.#modal.classList.remove('task-modal--hidden');
    this.#modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('task-modal-open');

    render(
      this.#modalBody,
      this.#taskEditComponent,
      RenderPosition.BEFOREEND,
    );

    document.addEventListener('keydown', this.#escKeyDownHandler);
  };

  destroy = () => {
    if (this.#taskEditComponent === null) {
      return;
    }

    this.#destroyCallback?.();

    remove(this.#taskEditComponent);
    this.#taskEditComponent = null;

    if (this.#modal) {
      this.#modal.classList.add('task-modal--hidden');
      this.#modal.setAttribute('aria-hidden', 'true');
    }
    document.body.classList.remove('task-modal-open');

    document.removeEventListener('keydown', this.#escKeyDownHandler);
  };

  #handleFormSubmit = async (task) => {
    await this.#changeData(UserAction.ADD_TASK, UpdateType.MINOR, task);
  };

  #handleDeleteClick = () => {
    this.destroy();
  };

  #escKeyDownHandler = (evt) => {
    if (evt.key === 'Escape' || evt.key === 'Esc') {
      evt.preventDefault();
      this.destroy();
    }
  };
}
