"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }), 
        // Si ton backend attend "username" au lieu de "email" pour le register, 
        // remplace la ligne ci-dessus par : body: JSON.stringify({ username: email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Erreur lors de l'inscription");
      }

      setSuccess(true);
      // Redirection vers le login après 2 secondes
      setTimeout(() => {
        router.push("/login");
      }, 2000);

    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-96 text-black">
        <h2 className="text-2xl mb-6 font-bold text-center text-gray-800">Inscription</h2>
        
        {error && <p className="text-red-500 mb-4 text-sm text-center">{error}</p>}
        {success && <p className="text-green-500 mb-4 text-sm text-center">Compte créé ! Redirection...</p>}
        
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 mb-4 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-6 border rounded"
          required
        />
        <button type="submit" className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700">
          Créer mon compte
        </button>

        <p className="mt-4 text-sm text-center text-gray-600">
          Déjà un compte ? <a href="/login" className="text-blue-600 hover:underline">Se connecter</a>
        </p>
      </form>
    </div>
  );
}