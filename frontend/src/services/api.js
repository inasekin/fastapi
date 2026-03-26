const TOKEN_KEY = 'access_token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

const formatDetail = (data, fallback) => {
  if (!data || typeof data !== 'object') {
    return fallback;
  }
  if (typeof data.detail === 'string') {
    return data.detail;
  }
  if (Array.isArray(data.detail)) {
    return data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
  }
  if (data.detail !== undefined) {
    return JSON.stringify(data.detail);
  }
  return fallback;
};

const apiFetch = async (path, options = {}) => {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (
    options.body &&
    typeof options.body === 'object' &&
    !(options.body instanceof FormData) &&
    !(options.body instanceof URLSearchParams)
  ) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }
  const res = await fetch(`/api${path}`, { ...options, headers });
  const text = await res.text();
  if (res.status === 204) {
    return null;
  }
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }
  if (!res.ok) {
    throw new Error(formatDetail(data, res.statusText));
  }
  return data;
};

export const register = (username, password) =>
  apiFetch('/auth/register', {
    method: 'POST',
    body: { username, password },
  });

export const login = async (username, password) => {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);
  const res = await fetch('/api/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  const text = await res.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = {};
    }
  }
  if (!res.ok) {
    throw new Error(formatDetail(data, res.statusText));
  }
  setToken(data.access_token);
  return data;
};

export const listTasks = (sortBy = 'created_at', order = 'desc') => {
  const params = new URLSearchParams({ sort_by: sortBy, order });
  return apiFetch(`/tasks?${params.toString()}`);
};

export const searchTasks = (q) => {
  const params = new URLSearchParams({ q });
  return apiFetch(`/tasks/search?${params.toString()}`);
};

export const topPriorityTasks = (n) => {
  const params = new URLSearchParams({ n: String(n) });
  return apiFetch(`/tasks/top-priority?${params.toString()}`);
};

export const createTask = (payload) =>
  apiFetch('/tasks', { method: 'POST', body: payload });

export const updateTask = (id, payload) =>
  apiFetch(`/tasks/${id}`, { method: 'PATCH', body: payload });

export const deleteTask = (id) => apiFetch(`/tasks/${id}`, { method: 'DELETE' });
