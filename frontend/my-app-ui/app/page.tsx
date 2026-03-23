"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from "next/navigation";
import { useAuth } from "./context/AuthContext";
import { fetchWithAuth } from "./utils/api";
import { Upload, Play, CheckCircle, AlertCircle, Loader2, LogOut, Sparkles } from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated, logout, loading: authLoading } = useAuth();
  const router = useRouter();

  // --- States pour l'Analyse de CV ---
  const [file, setFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState("");
  const [jobTargetId, setJobTargetId] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // --- States pour l'Entretien (Quiz) ---
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [evaluation, setEvaluation] = useState<any>(null);
  const [loadingQuiz, setLoadingQuiz] = useState(false);
  const [loadingEval, setLoadingEval] = useState(false);

  // 1. Action : Analyser le CV (/analyze)
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !jobDesc) return alert("Fichier et description requis !");
    
    setLoadingAnalysis(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDesc);

    try {
      // On utilise fetchWithAuth pour inclure automatiquement le Token JWT
      const res = await fetchWithAuth("/analyze", {
        method: "POST",
        body: formData, // Pas de headers JSON car c'est du FormData
      });

      if (!res.ok) throw new Error("Erreur lors de l'analyse");
      
      const data = await res.json();
      setAnalysis(data.ai_result);
      setJobTargetId(data.job_target_id); // On stocke l'ID pour le quiz
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // 2. Action : Générer le Quiz (/generate-quiz)
  const generateQuiz = async () => {
    if (!jobTargetId) return alert("Analyse ton CV d'abord !");
    
    setLoadingQuiz(true);
    const formData = new URLSearchParams();
    formData.append('job_target_id', jobTargetId.toString());

    try {
      const res = await fetchWithAuth("/generate-quiz", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });

      if (!res.ok) throw new Error("Erreur génération quiz");

      const data = await res.json();
      setQuestions(data.questions.questions);
      setSessionId(data.session_id);
      setEvaluation(null);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoadingQuiz(false);
    }
  };

  // 3. Action : Soumettre les réponses (/evaluate-interview)
  const submitInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionId) return;
    
    setLoadingEval(true);
    try {
      const res = await fetchWithAuth("/evaluate-interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          candidate_answers: answers
        }),
      });

      if (!res.ok) throw new Error("Erreur évaluation");
      const data = await res.json();
      setEvaluation(data);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoadingEval(false);
    }
  };

  if (authLoading) return <div className="h-screen flex items-center justify-center bg-slate-50"><Loader2 className="animate-spin text-blue-600" size={48} /></div>;

  // ==========================================
  // VUE 1 : NON CONNECTÉ (LANDING)
  // ==========================================
  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-2xl space-y-6">
          <div className="bg-blue-100 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
             <Sparkles className="text-blue-600" size={32} />
          </div>
          <h1 className="text-5xl font-black text-slate-900 tracking-tight">Career Pathfinder AI</h1>
          <p className="text-xl text-slate-600">
            L'intelligence artificielle au service de ton prochain job. Analyse ton CV et entraîne-toi avec Qwen 2.5.
          </p>
          <div className="flex gap-4 justify-center mt-8">
            <button onClick={() => router.push("/login")} className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 transition-all">
              Se connecter
            </button>
            <button onClick={() => router.push("/register")} className="border-2 border-slate-200 text-slate-700 px-8 py-3 rounded-xl font-bold hover:bg-slate-50 transition-all">
              Créer un compte
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ==========================================
  // VUE 2 : CONNECTÉ (DASHBOARD)
  // ==========================================
  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Barre de navigation */}
        <nav className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 font-black text-xl text-slate-900">
            <Sparkles className="text-blue-600" /> Career Pathfinder
          </div>
          <button onClick={logout} className="flex items-center gap-2 text-red-500 font-semibold hover:bg-red-50 p-2 rounded-lg transition-colors">
            <LogOut size={20} /> Déconnexion
          </button>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* GAUCHE: ANALYSE CV */}
          <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-6">
            <div className="flex items-center gap-2 text-blue-600 font-bold uppercase text-xs tracking-widest">
              <Upload size={16} /> <span>Étape 1: Analyse du profil</span>
            </div>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div className="border-2 border-dashed border-slate-200 rounded-2xl p-4 text-center hover:border-blue-400 transition-colors">
                <input 
                  type="file" 
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700"
                />
              </div>
              <textarea 
                placeholder="Colle la description du poste ici..."
                className="w-full h-40 p-4 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none transition-all text-slate-700 bg-slate-50"
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
              />
              <button 
                disabled={loadingAnalysis}
                className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 disabled:bg-blue-300 flex justify-center items-center gap-2 shadow-lg shadow-blue-200"
              >
                {loadingAnalysis ? <Loader2 className="animate-spin" /> : "Lancer le Matching AI"}
              </button>
            </form>

           {analysis && (
              <div className="mt-6 p-6 bg-blue-600 rounded-2xl text-white">
                <div className="text-sm opacity-80 uppercase font-bold mb-1">Score de Match</div>
                <div className="text-5xl font-black">{analysis?.match_score || 0}%</div>
                
                {/* Nouveau bloc beaucoup plus détaillé */}
                <div className="mt-4 text-sm bg-blue-700/50 p-4 rounded-xl space-y-3">
                   <p>
                     <strong className="text-blue-200">Compétences exigées par l'offre :</strong><br/>
                     {analysis?.data?.job_skills_required?.join(', ') || "Aucune extraite"}
                   </p>
                   <p>
                     <strong className="text-blue-200">Compétences trouvées dans le CV :</strong><br/>
                     {analysis?.data?.cv_skills_found?.join(', ') || "Aucune extraite"}
                   </p>
                   <div className="h-px bg-blue-500 w-full my-2"></div>
                   <p>
                     <strong className="text-white">Compétences manquantes :</strong><br/>
                     {analysis?.data?.missing_skills && analysis.data.missing_skills.length > 0 
                        ? <span className="text-rose-300 font-bold">{analysis.data.missing_skills.join(', ')}</span> 
                        : <span className="text-emerald-300 font-bold">Aucune ! Profil parfait 🎉</span>}
                   </p>
                </div>
              </div>
            )}
          </section>

          {/* DROITE: SIMULATEUR D'ENTRETIEN */}
          <section className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 space-y-6">
            <div className="flex items-center gap-2 text-emerald-600 font-bold uppercase text-xs tracking-widest">
              <Play size={16} /> <span>Étape 2: Simulation Technique</span>
            </div>
            
            {!questions.length ? (
              <div className="text-center py-20 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <p className="text-slate-400 mb-6 font-medium">Prêt à tester tes compétences ?</p>
                <button 
                  onClick={generateQuiz}
                  disabled={!jobTargetId || loadingQuiz}
                  className="bg-emerald-600 text-white px-10 py-4 rounded-2xl font-bold hover:bg-emerald-700 disabled:bg-slate-300 shadow-lg shadow-emerald-100 flex items-center gap-2 mx-auto"
                >
                  {loadingQuiz ? <Loader2 className="animate-spin" /> : "Générer 10 Questions"}
                </button>
              </div>
            ) : (
              <form onSubmit={submitInterview} className="space-y-6">
                <div className="max-h-[500px] overflow-y-auto space-y-6 pr-2 custom-scrollbar">
                  {questions.map((q: any) => (
                    <div key={q.number} className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                      <p className="font-bold text-slate-800 mb-3">Q{q.number}: {q.question_text}</p>
                      <textarea 
                        className="w-full p-3 border border-slate-200 rounded-xl bg-white focus:ring-2 focus:ring-emerald-500 outline-none transition-all text-slate-700 h-24"
                        placeholder="Ta réponse..."
                        onChange={(e) => setAnswers({...answers, [q.number]: e.target.value})}
                        required
                      />
                    </div>
                  ))}
                </div>
                {!evaluation && (
                  <button className="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold hover:bg-black shadow-xl">
                    {loadingEval ? <Loader2 className="animate-spin mx-auto" /> : "Terminer l'entretien"}
                  </button>
                )}
              </form>
            )}

            {evaluation && (
              <div className="mt-6 space-y-4">
                <div className="p-6 bg-slate-900 text-white rounded-2xl flex justify-between items-center">
                  <div>
                    <div className="text-xs opacity-60 uppercase font-bold">Note Finale</div>
                    <div className="text-4xl font-black">{evaluation.score_out_of_10}/10</div>
                  </div>
                  <CheckCircle size={40} className="text-emerald-400" />
                </div>
                <div className="space-y-3">
                  {evaluation.answer_details.map((detail: any) => (
                    <div key={detail.number} className="p-4 border border-slate-100 rounded-xl flex items-start gap-3 bg-white">
                      {detail.is_correct ? <CheckCircle className="text-emerald-500 shrink-0" /> : <AlertCircle className="text-rose-500 shrink-0" />}
                      <div>
                        <p className="text-sm font-bold text-slate-800">Question {detail.number}</p>
                        <p className="text-xs text-slate-500 leading-relaxed mt-1">{detail.justification}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <button 
                  onClick={() => {setQuestions([]); setEvaluation(null);}}
                  className="w-full text-slate-400 text-sm hover:text-blue-600 font-medium transition-colors"
                >
                  Recommencer un nouvel entretien
                </button>
              </div>
            )}
          </section>

        </div>
      </div>
    </main>
  );
}