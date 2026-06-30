const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5002/api";


export function getToken() {
  return localStorage.getItem("nutritrack_token");
}


export function setToken(token) {
  if (token) {
    localStorage.setItem("nutritrack_token", token);
  } else {
    localStorage.removeItem("nutritrack_token");
  }
}


export async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }

  return data;
}


export const api = {
  signup: (payload) => apiRequest("/auth/signup", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => apiRequest("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  me: () => apiRequest("/auth/me"),
  dashboard: (date) => apiRequest(`/dashboard/today${date ? `?date=${date}` : ""}`),
  profile: () => apiRequest("/profile"),
  updateProfile: (payload) => apiRequest("/profile", { method: "PUT", body: JSON.stringify(payload) }),
  meals: (date) => apiRequest(`/meals?date=${date}`),
  addMeal: (payload) => apiRequest("/meals", { method: "POST", body: JSON.stringify(payload) }),
  deleteMeal: (id) => apiRequest(`/meals/${id}`, { method: "DELETE" }),
  foods: (query) => apiRequest(`/foods?q=${encodeURIComponent(query || "")}`),
  estimate: (description) => apiRequest("/nutrition/estimate", {
    method: "POST",
    body: JSON.stringify({ description }),
  }),
  weeklyAnalytics: () => apiRequest("/analytics/week"),
};
