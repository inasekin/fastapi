import SiteMenuView from './view/site-menu-view.js';
import TasksModel from './model/tasks-model.js';
import { render, RenderPosition } from './utils/render.js';
import BoardPresenter from './presenter/board-presenter.js';
import AuthPanelView from './view/auth-panel-view.js';
import { MenuItem } from './utils/constants.js';
import * as api from './services/api.js';

const authOverlay = document.getElementById('auth-overlay');
const appShell = document.querySelector('.app-shell');
const siteHeaderElement = appShell.querySelector('.main__control');
const controlTrailing = siteHeaderElement.querySelector('.control__trailing');
const logoutBtn = controlTrailing.querySelector('#app-logout');

const authPanel = new AuthPanelView();
const siteMenuComponent = new SiteMenuView();

render(authOverlay, authPanel, RenderPosition.BEFOREEND);
render(controlTrailing, siteMenuComponent, RenderPosition.AFTERBEGIN);

const tasksModel = new TasksModel();
const boardPresenter = new BoardPresenter(appShell, tasksModel);

let boardInitialized = false;

const showLoggedInChrome = () => {
  authOverlay.classList.add('auth-overlay--hidden');
  authOverlay.setAttribute('aria-hidden', 'true');
  appShell.classList.remove('app-shell--hidden');
  appShell.removeAttribute('aria-hidden');
  authPanel.element.classList.add('visually-hidden');
  siteMenuComponent.element.classList.remove('visually-hidden');
  logoutBtn.classList.remove('visually-hidden');
};

const showLoggedOutChrome = () => {
  authOverlay.classList.remove('auth-overlay--hidden');
  authOverlay.setAttribute('aria-hidden', 'false');
  appShell.classList.add('app-shell--hidden');
  appShell.setAttribute('aria-hidden', 'true');
  authPanel.element.classList.remove('visually-hidden');
  siteMenuComponent.element.classList.add('visually-hidden');
  logoutBtn.classList.add('visually-hidden');
};

const bootstrapBoard = async () => {
  if (!boardInitialized) {
    boardPresenter.init();
    boardInitialized = true;
  }
  await boardPresenter.refreshFromServer();
};

const enterAfterAuth = async () => {
  showLoggedInChrome();
  try {
    await bootstrapBoard();
  } catch {
    api.clearToken();
    showLoggedOutChrome();
    window.alert('Сессия недействительна. Войдите снова.');
  }
};

authPanel.setSubmitHandlers({
  onLogin: async (username, password) => {
    await api.login(username, password);
    await enterAfterAuth();
  },
  onRegister: async (username, password) => {
    await api.register(username, password);
    await api.login(username, password);
    await enterAfterAuth();
  },
});

logoutBtn.addEventListener('click', () => {
  api.clearToken();
  window.location.reload();
});

const handleTaskNewFormClose = () => {
  siteMenuComponent.setMenuItem(MenuItem.TASKS);
};

const handleSiteMenuClick = (menuItem) => {
  if (menuItem === MenuItem.ADD_NEW_TASK) {
    boardPresenter.createTask(handleTaskNewFormClose);
  }
};

siteMenuComponent.setMenuClickHandler(handleSiteMenuClick);

showLoggedOutChrome();

if (api.getToken()) {
  void enterAfterAuth();
}
