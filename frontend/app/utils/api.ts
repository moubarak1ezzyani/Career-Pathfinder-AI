const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  // On récupère le token stocké localement
  const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
  
  // On prépare les headers de base (sans forcer le Content-Type tout de suite)
  const headers: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string>),
  };

  // 🚨 LA CORRECTION EST ICI :
  // Si on n'envoie PAS un fichier (FormData) et qu'on n'a pas déjà précisé de Content-Type,
  // alors seulement on met "application/json".
  // Si c'est un FormData, on ne met rien, et le navigateur gèrera le "multipart/form-data" tout seul !
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

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