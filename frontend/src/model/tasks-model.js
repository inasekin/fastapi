import AbstractObservable from '../utils/abstract-observable.js';
import { UpdateType } from '../utils/constants.js';

export default class TasksModel extends AbstractObservable {
  #tasks = [];

  set tasks(tasks) {
    this.#tasks = [...tasks];
  }

  get tasks() {
    return this.#tasks;
  }

  replaceTasks = (tasks) => {
    this.#tasks = [...tasks];
    this._notify(UpdateType.MAJOR);
  };

  updateTask = (updateType, update) => {
    const index = this.#tasks.findIndex((task) => task.id === update.id);

    if (index === -1) {
      throw new Error('Невозможно обновить несуществующую задачу');
    }

    this.#tasks = [
      ...this.#tasks.slice(0, index),
      update,
      ...this.#tasks.slice(index + 1),
    ];

    this._notify(updateType, update);
  };

  addTask = (updateType, update) => {
    this.#tasks = [update, ...this.#tasks];

    this._notify(updateType, update);
  };

  deleteTask = (updateType, update) => {
    const index = this.#tasks.findIndex((task) => task.id === update.id);

    if (index === -1) {
      throw new Error('Невозможно удалить несуществующую задачу');
    }

    this.#tasks = [
      ...this.#tasks.slice(0, index),
      ...this.#tasks.slice(index + 1),
    ];

    this._notify(updateType);
  };
}
