"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./context/AuthContext";

export default function Home() {
  const { logout } = useAuth();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // On vérifie directement dans le navigateur si un token existe
    const token = localStorage.getItem("token");
    
    if (!token) {
      // Pas de token = on le jette dehors vers la page de login !
      router.push("/login");
    } else {
      // Il a un token, on le laisse entrer
      setIsChecking(false);
    }
  }, [router]);

  // Pendant qu'on vérifie, on affiche un petit message d'attente
  // pour éviter que la page "clignote" avant la redirection
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-xl font-semibold text-gray-600">Vérification de l'accès...</p>
      </div>
    );
  }

  // S'il est connecté, il voit ce contenu :
  return (
    <main className="min-h-screen p-8 bg-gray-50 text-black">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md mt-10">
        <h1 className="text-3xl font-bold mb-4 text-blue-600">
          Bienvenue sur Career Pathfinder AI 🚩
        </h1>
        <p className="text-gray-700 mb-8 text-lg">
          Félicitations ! Si tu vois cette page, c'est que la connexion entre ton frontend Next.js et ton backend FastAPI fonctionne parfaitement avec JWT. 🎉
        </p>
        
        <button 
          onClick={logout}
          className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600 transition-colors"
        >
          Se déconnecter
        </button>
      </div>
    </main>
  );
}