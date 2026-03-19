"use client";

import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Play, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function CareerPathfinder() {
  // States for CV Analysis
  const [file, setFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // States for Interview
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [evaluation, setEvaluation] = useState<any>(null);
  const [loadingQuiz, setLoadingQuiz] = useState(false);
  const [loadingEval, setLoadingEval] = useState(false);

  // --- Actions ---
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Attempting to connect to:", `${API_BASE}/analyze`);
    if (!file) return;
    setLoadingAnalysis(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDesc);

    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData);
      setAnalysis(res.data);
    } catch (err) {
      alert("Error connecting to Backend");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const generateQuiz = async () => {
    if (!jobDesc) return alert("Please provide a job description first.");
    setLoadingQuiz(true);
    const formData = new FormData();
    formData.append('job_description', jobDesc);

    try {
      const res = await axios.post(`${API_BASE}/generate-quiz`, formData);
      setQuestions(res.data.questions);
      setEvaluation(null); // Reset old evaluation
    } catch (err) {
      alert("Error generating quiz");
    } finally {
      setLoadingQuiz(false);
    }
  };

  const submitInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingEval(true);
    try {
      const res = await axios.post(`${API_BASE}/evaluate-interview`, {
        questions: { questions },
        candidate_answers: answers
      });
      setEvaluation(res.data);
    } catch (err) {
      alert("Error evaluating interview");
    } finally {
      setLoadingEval(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-12">
      <div className="max-w-5xl mx-auto space-y-10">
        
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Career Pathfinder AI</h1>
          <p className="text-slate-500">Analyze your CV and simulate technical interviews with Qwen 2.5</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* LEFT: CV ANALYSIS */}
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-6 text-blue-600 font-bold uppercase text-sm">
              <Upload size={18} /> <span>Step 1: Analysis</span>
            </div>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <input 
                type="file" 
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <textarea 
                placeholder="Paste Job Description here..."
                className="w-full h-32 p-3 border rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all text-blue-700"
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
              />
              <button 
                disabled={loadingAnalysis}
                className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 disabled:bg-blue-300 flex justify-center items-center gap-2"
              >
                {loadingAnalysis ? <Loader2 className="animate-spin" /> : "Run AI Matching"}
              </button>
            </form>

            {analysis && (
              <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
                <div className="text-3xl font-black text-blue-700">{analysis.match_score}% Match</div>
                <div className="mt-2 text-sm text-slate-600">
                  <strong>Missing:</strong> {analysis.data.missing_skills.join(', ') || "None!"}
                </div>
              </div>
            )}
          </section>

          {/* RIGHT: INTERVIEW SIMULATOR */}
          <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 mb-6 text-green-600 font-bold uppercase text-sm">
              <Play size={18} /> <span>Step 2: Simulation</span>
            </div>
            
            {questions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-400 mb-4 text-sm">Ready to test your skills?</p>
                <button 
                  onClick={generateQuiz}
                  className="bg-green-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-green-700"
                >
                  {loadingQuiz ? <Loader2 className="animate-spin mx-auto" /> : "Generate 10 Questions"}
                </button>
              </div>
            ) : (
              <form onSubmit={submitInterview} className="space-y-6">
                <div className="max-h-[500px] overflow-y-auto space-y-6 pr-2">
                  {questions.map((q) => (
                    <div key={q.number} className="space-y-2">
                      <p className="font-semibold text-indigo-600">Q{q.number}: {q.question_text}</p>
                      <textarea 
                        className="w-full p-2 border rounded-lg bg-slate-50 focus:bg-white transition-colors text-indigo-700"
                        onChange={(e) => setAnswers({...answers, [q.number]: e.target.value})}
                        required
                      />
                    </div>
                  ))}
                </div>
                {!evaluation && (
                  <button className="w-full bg-slate-900 text-white py-3 rounded-xl font-bold hover:bg-black">
                    {loadingEval ? <Loader2 className="animate-spin mx-auto" /> : "Submit Interview"}
                  </button>
                )}
              </form>
            )}

            {evaluation && (
              <div className="mt-6 space-y-4">
                <div className="p-4 bg-slate-900 text-white rounded-xl flex justify-between items-center">
                  <span className="text-lg">Score</span>
                  <span className="text-4xl font-black">{evaluation.score_out_of_10}/10</span>
                </div>
                <div className="space-y-2">
                  {evaluation.answer_details.map((detail: any) => (
                    <div key={detail.number} className="p-3 border rounded-lg flex items-start gap-3">
                      {detail.is_correct ? <CheckCircle className="text-green-500 mt-1" /> : <AlertCircle className="text-red-500 mt-1" />}
                      <div>
                        <p className="text-sm font-bold">Question {detail.number}</p>
                        <p className="text-xs text-slate-500">{detail.justification}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <button 
                  onClick={() => setQuestions([])}
                  className="w-full text-slate-500 text-sm hover:underline"
                >
                  Start New Interview
                </button>
              </div>
            )}
          </section>

        </div>
      </div>
    </main>
  );
}