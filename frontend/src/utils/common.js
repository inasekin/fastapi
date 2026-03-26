import dayjs from 'dayjs';

export const getRandomInteger = (a = 0, b = 1) => {
  const lower = Math.ceil(Math.min(a, b));
  const upper = Math.floor(Math.max(a, b));

  return Math.floor(lower + Math.random() * (upper - lower + 1));
};

export const isDatesEqual = (dateA, dateB) =>
  (dateA === null && dateB === null) || dayjs(dateA).isSame(dateB, 'D');

export const isTaskExpired = (dueDate) =>
  dueDate && dayjs().isAfter(dueDate, 'D');

export const formatTaskDueDate = (dueDate) =>
  dueDate ? dayjs(dueDate).format('D MMMM') : '';
