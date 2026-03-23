"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, UserPlus } from 'lucide-react'; // Ajout des icônes

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
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Erreur lors de l'inscription");
      }

      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 2000);

    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-md bg-white p-8 rounded-3xl shadow-sm border border-slate-200 space-y-6">
        
        {/* En-tête stylisé */}
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="bg-blue-100 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto">
            <Sparkles className="text-blue-600" size={32} />
          </div>
          <div>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">Créer un compte</h2>
            <p className="text-slate-500 mt-2">Rejoins Career Pathfinder AI</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 mt-8">
          {error && (
            <div className="bg-red-50 text-red-500 p-3 rounded-xl text-sm border border-red-100 text-center font-medium">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-emerald-50 text-emerald-600 p-3 rounded-xl text-sm border border-emerald-100 text-center font-medium">
              Compte créé avec succès ! Redirection...
            </div>
          )}
          
          <input
            type="email"
            placeholder="Adresse email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-4 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all text-slate-700 bg-slate-50"
            required
          />
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-4 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all text-slate-700 bg-slate-50"
            required
          />
          
          <button type="submit" className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all flex justify-center items-center gap-2 shadow-lg shadow-blue-200 mt-2">
            <UserPlus size={20} /> Créer mon compte
          </button>

          <p className="mt-6 text-sm text-center text-slate-600">
            Déjà un compte ? <a href="/login" className="text-blue-600 font-bold hover:underline transition-all">Se connecter</a>
          </p>
        </form>
      </div>
    </main>
  );
}