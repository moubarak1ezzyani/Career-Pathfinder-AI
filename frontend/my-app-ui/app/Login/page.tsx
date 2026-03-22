"use client";

import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      // FastAPI utilise OAuth2PasswordRequestForm, qui attend du FormData (x-www-form-urlencoded) par défaut pour le login
      const formData = new URLSearchParams();
      formData.append("username", email); // FastAPI utilise 'username' pour l'email dans OAuth2
      formData.append("password", password);

      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      if (!res.ok) throw new Error("Identifiants incorrects");

      const data = await res.json();
      login(data.access_token); // Appelle la fonction login du contexte
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-96">
        <h2 className="text-2xl mb-6 font-bold text-center text-gray-800">Connexion</h2>
        {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}
        
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 mb-4 border rounded text-black"
          required
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-6 border rounded text-black"
          required
        />
        <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
          Se connecter
        </button>
      </form>
    </div>
  );
}