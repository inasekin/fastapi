import AbstractView from './abstract-view.js';

const createTemplate = () => `
  <div class="auth-panel">
    <p class="auth-panel__brand">Task manager</p>
    <h2 class="auth-panel__heading" data-auth-heading>Вход</h2>
    <form class="auth-panel__form auth-panel__form--login" data-auth-mode="login">
      <label class="auth-panel__label">
        Логин
        <input class="auth-panel__input" type="text" name="username" required autocomplete="username" />
      </label>
      <label class="auth-panel__label">
        Пароль
        <input class="auth-panel__input" type="password" name="password" required autocomplete="current-password" />
      </label>
      <div class="auth-panel__actions">
        <button class="auth-panel__submit control__button" type="submit">Войти</button>
        <button class="auth-panel__switch" type="button" data-switch="register" aria-label="Перейти к регистрации">Регистрация</button>
      </div>
    </form>
    <form class="auth-panel__form auth-panel__form--register visually-hidden" data-auth-mode="register">
      <label class="auth-panel__label">
        Логин
        <input class="auth-panel__input" type="text" name="username" required autocomplete="username" />
      </label>
      <label class="auth-panel__label">
        Пароль
        <input class="auth-panel__input" type="password" name="password" required autocomplete="new-password" />
      </label>
      <div class="auth-panel__actions">
        <button class="auth-panel__submit control__button" type="submit">Создать аккаунт</button>
        <button class="auth-panel__switch" type="button" data-switch="login" aria-label="Вернуться ко входу">Уже есть аккаунт</button>
      </div>
    </form>
    <p class="auth-panel__error visually-hidden" role="alert" aria-live="polite"></p>
  </div>
`;

export default class AuthPanelView extends AbstractView {
  get template() {
    return createTemplate();
  }

  setSubmitHandlers = (handlers) => {
    this._handlers = handlers;
    this.element.querySelectorAll('.auth-panel__form').forEach((form) => {
      form.addEventListener('submit', this.#handleFormSubmit);
    });
    this.element.querySelectorAll('[data-switch]').forEach((btn) => {
      btn.addEventListener('click', this.#handleSwitch);
    });
  };

  showError = (message) => {
    const el = this.element.querySelector('.auth-panel__error');
    el.textContent = message;
    el.classList.remove('visually-hidden');
  };

  clearError = () => {
    const el = this.element.querySelector('.auth-panel__error');
    el.textContent = '';
    el.classList.add('visually-hidden');
  };

  #handleFormSubmit = async (evt) => {
    evt.preventDefault();
    this.clearError();
    const form = evt.target;
    const mode = form.dataset.authMode;
    const fd = new FormData(form);
    const username = String(fd.get('username') || '').trim();
    const password = String(fd.get('password') || '');
    try {
      if (mode === 'login') {
        await this._handlers.onLogin(username, password);
      } else {
        await this._handlers.onRegister(username, password);
      }
    } catch (err) {
      this.showError(err.message || 'Ошибка');
    }
  };

  #handleSwitch = (evt) => {
    evt.preventDefault();
    const target = evt.currentTarget.dataset.switch;
    const loginForm = this.element.querySelector('[data-auth-mode="login"]');
    const registerForm = this.element.querySelector('[data-auth-mode="register"]');
    const heading = this.element.querySelector('[data-auth-heading]');
    if (target === 'register') {
      loginForm.classList.add('visually-hidden');
      registerForm.classList.remove('visually-hidden');
      heading.textContent = 'Регистрация';
    } else {
      registerForm.classList.add('visually-hidden');
      loginForm.classList.remove('visually-hidden');
      heading.textContent = 'Вход';
    }
    this.clearError();
  };
}
