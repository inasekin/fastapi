import BoardView from '../view/board-view.js';
import KanbanBoardView from '../view/kanban-board-view.js';
import BoardToolbarView from '../view/board-toolbar-view.js';
import TaskPresenter from './task-presenter.js';
import TaskNewPresenter from './task-new-presenter.js';
import { render, RenderPosition, remove } from '../utils/render.js';
import { UpdateType, UserAction } from '../utils/constants.js';
import * as api from '../services/api.js';

const VALID_STATUSES = new Set(['pending', 'in_progress', 'completed']);

export default class BoardPresenter {
  #boardContainer = null;
  #tasksModel = null;

  #boardComponent = new BoardView();
  #kanbanComponent = new KanbanBoardView();
  #toolbarComponent = new BoardToolbarView();
  #taskPresenter = new Map();
  #taskNewPresenter = null;

  #viewMode = 'list';
  #searchQuery = '';
  #topN = 5;
  #sortBy = 'created_at';
  #order = 'desc';

  constructor(boardContainer, tasksModel) {
    this.#boardContainer = boardContainer;
    this.#tasksModel = tasksModel;

    this.#taskNewPresenter = new TaskNewPresenter(this.#handleViewAction);

    this.#tasksModel.addObserver(this.#handleModelEvent);
  }

  get tasks() {
    return this.#tasksModel.tasks;
  }

  init = () => {
    render(
      this.#boardContainer,
      this.#boardComponent,
      RenderPosition.BEFOREEND
    );
    render(
      this.#boardComponent,
      this.#toolbarComponent,
      RenderPosition.BEFOREEND
    );
    render(
      this.#boardComponent,
      this.#kanbanComponent,
      RenderPosition.BEFOREEND
    );

    this.#taskNewPresenter.setBoardView(this.#boardComponent);

    this.#toolbarComponent.setHandlers({
      onApplySort: (sortBy, order) => {
        this.#sortBy = sortBy;
        this.#order = order;
        this.#viewMode = 'list';
        this.#reloadCurrentViewSafe();
      },
      onResetList: (sortBy, order) => {
        this.#sortBy = sortBy;
        this.#order = order;
        this.#viewMode = 'list';
        this.#reloadCurrentViewSafe();
      },
      onSearch: (q) => {
        this.#searchQuery = q;
        this.#viewMode = 'search';
        this.#reloadCurrentViewSafe();
      },
      onTop: (n) => {
        this.#topN = n;
        this.#viewMode = 'top';
        this.#reloadCurrentViewSafe();
      },
    });

    this.#toolbarComponent.syncSortUi(this.#sortBy, this.#order);
    this.#renderBoard();
  };

  refreshFromServer = async () => {
    await this.#reloadCurrentView();
  };

  #reloadCurrentViewSafe = () => {
    void this.#reloadCurrentView().catch((err) => {
      window.alert(err.message || 'Ошибка загрузки задач');
    });
  };

  createTask = (callback) => {
    this.#taskNewPresenter.init(callback);
  };

  #reloadCurrentView = async () => {
    let tasks;
    if (this.#viewMode === 'search') {
      tasks = await api.searchTasks(this.#searchQuery);
    } else if (this.#viewMode === 'top') {
      tasks = await api.topPriorityTasks(this.#topN);
    } else {
      tasks = await api.listTasks(this.#sortBy, this.#order);
    }
    this.#tasksModel.replaceTasks(tasks);
  };

  #handleModeChange = () => {
    this.#taskNewPresenter.destroy();
    this.#taskPresenter.forEach((presenter) => presenter.resetView());
  };

  #handleViewAction = (actionType, _updateType, update) =>
    this.#handleViewActionAsync(actionType, update);

  #handleViewActionAsync = async (actionType, update) => {
    try {
      if (actionType === UserAction.UPDATE_TASK) {
        await api.updateTask(update.id, {
          title: update.title,
          description: update.description,
          status: update.status,
          priority: update.priority,
        });
      } else if (actionType === UserAction.ADD_TASK) {
        await api.createTask({
          title: update.title,
          description: update.description,
          status: update.status,
          priority: update.priority,
        });
        this.#taskNewPresenter.destroy();
      } else if (actionType === UserAction.DELETE_TASK) {
        await api.deleteTask(update.id);
      }
      await this.#reloadCurrentView();
    } catch (err) {
      window.alert(err.message || 'Ошибка');
    }
  };

  #handleModelEvent = (updateType, data) => {
    switch (updateType) {
      case UpdateType.PATCH:
        if (data && this.#taskPresenter.get(data.id)) {
          this.#taskPresenter.get(data.id).init(data);
        }
        break;
      case UpdateType.MINOR:
        this.#clearBoard();
        this.#renderBoard();
        break;
      case UpdateType.MAJOR:
        this.#clearBoard({ resetSortType: true });
        this.#renderBoard();
        break;
      default:
        break;
    }
  };

  #statusForTask = (task) => {
    const s = task.status;
    return VALID_STATUSES.has(s) ? s : 'pending';
  };

  #renderTask = (task) => {
    const listEl = this.#kanbanComponent.getListElForStatus(this.#statusForTask(task));
    if (!listEl) {
      return;
    }
    const taskPresenter = new TaskPresenter(
      listEl,
      this.#handleViewAction,
      this.#handleModeChange
    );
    taskPresenter.init(task);
    this.#taskPresenter.set(task.id, taskPresenter);
  };

  #renderTasks = (tasks) => {
    tasks.forEach((task) => this.#renderTask(task));
  };

  #clearBoard = ({ resetSortType = false } = {}) => {
    this.#taskNewPresenter.destroy();
    this.#taskPresenter.forEach((presenter) => presenter.destroy());
    this.#taskPresenter.clear();

    if (resetSortType && this.#toolbarComponent) {
      this.#toolbarComponent.syncSortUi(this.#sortBy, this.#order);
    }
  };

  #renderBoard = () => {
    const tasks = this.tasks;
    this.#renderTasks(tasks);
  };
}
