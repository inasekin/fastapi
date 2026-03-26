import AbstractView from '../view/abstract-view.js';

export const RenderPosition = {
  BEFOREBEGIN: 'beforebegin',
  AFTERBEGIN: 'afterbegin',
  BEFOREEND: 'beforeend',
  AFTEREND: 'afterend',
};

export const render = (container, element, place) => {
  const parent =
    container instanceof AbstractView ? container.element : container;
  const child = element instanceof AbstractView ? element.element : element;

  switch (place) {
    case RenderPosition.BEFOREBEGIN:
      parent.before(child);
      break;
    case RenderPosition.AFTERBEGIN:
      parent.prepend(child);
      break;
    case RenderPosition.BEFOREEND:
      parent.append(child);
      break;
    case RenderPosition.AFTEREND:
      parent.after(child);
      break;
  }
};

// Принцип работы прост:
// 1. создаём пустой div-блок
// 2. берём HTML в виде строки и вкладываем в этот div-блок, превращая в DOM-элемент
// 3. возвращаем этот DOM-элемент
export const createElement = (template) => {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = template;
  const root = wrapper.firstElementChild;
  if (!root) {
    throw new Error('Шаблон не содержит корневого HTML-элемента');
  }
  return root;
};

// Единственный нюанс, что HTML в строке должен иметь общую обёртку,
// то есть быть чем-то вроде <nav><a>Link 1</a><a>Link 2</a></nav>,
// а не просто <a>Link 1</a><a>Link 2</a>
export const replace = (newElement, oldElement) => {
  if (newElement === null || oldElement === null) {
    throw new Error('Невозможно заменить несуществующие элементы');
  }

  const newChild =
    newElement instanceof AbstractView ? newElement.element : newElement;
  const oldChild =
    oldElement instanceof AbstractView ? oldElement.element : oldElement;

  const parent = oldChild.parentElement;

  if (parent === null) {
    throw new Error('Родительский элемент не существует');
  }

  parent.replaceChild(newChild, oldChild);
};

export const remove = (component) => {
  if (component === null) {
    return;
  }

  if (!(component instanceof AbstractView)) {
    throw new Error('Можно удалить только компоненты');
  }

  component.element.remove();
  component.removeElement();
};
