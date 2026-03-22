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
      const formData = new URLSearchParams();
      formData.append("username", email); 
      formData.append("password", password);

      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

      // API_URL
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      if (!res.ok) {
        // On récupère la vraie erreur du backend pour comprendre ce qui cloche
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || "Identifiants incorrects ou serveur injoignable");
      }

      const data = await res.json();
      login(data.access_token); 
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

        {/* Le lien vers la page d'inscription ajouté ici */}
        <p className="mt-4 text-sm text-center text-gray-600">
          Pas encore de compte ? <a href="/register" className="text-blue-600 hover:underline">S'inscrire</a>
        </p>
      </form>
    </div>
  );
}