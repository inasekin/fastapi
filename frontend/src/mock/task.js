import dayjs from 'dayjs';
import { nanoid } from 'nanoid';
import { COLORS } from '../utils/constants.js';
import { getRandomInteger } from '../utils/common.js';

const generateDescription = () => {
  const descriptions = [
    'Изучить теорию',
    'Сделать домашку',
    'Пройти интенсив на соточку',
  ];

  const randomIndex = getRandomInteger(0, descriptions.length - 1);

  return descriptions[randomIndex];
};

const generateDate = () => {
  const isDate = Boolean(getRandomInteger(0, 1));

  if (!isDate) {
    return null;
  }

  const maxDaysGap = 7;
  const daysGap = getRandomInteger(-maxDaysGap, maxDaysGap);

  return dayjs().add(daysGap, 'day').toDate();
};

const getRandomColor = () => {
  const randomIndex = getRandomInteger(0, COLORS.length - 1);

  return COLORS[randomIndex];
};

export const generateTask = () => {
  const dueDate = generateDate();

  return {
    id: nanoid(),
    description: generateDescription(),
    dueDate,
    color: getRandomColor(),
  };
};
