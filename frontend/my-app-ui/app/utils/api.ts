const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  // On récupère le token stocké localement
  const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
  
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Si le token est invalide/expiré, on déconnecte l'utilisateur
    if (typeof window !== 'undefined') {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  }

  return response;
}