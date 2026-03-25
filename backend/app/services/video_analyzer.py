import cv2
import os
import sys
from deepface import DeepFace
from collections import Counter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.core.config import vid_stress

def analyze_video_offline(video_path):
    # Vérifier si le fichier existe
    if not os.path.exists(video_path):
        print(f"Erreur : Le fichier {video_path} n'existe pas.")
        return None

    # Chargement de la vidéo
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0: fps = 30  # Valeur par défaut si indéterminé
    
    frame_count = 0
    emotions_list = []

    print(f"--- Analyse de la vidéo : {video_path} ---")
    print("Traitement en cours (1 frame par seconde pour optimiser le CPU)...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Optimisation CPU : On analyse seulement une image toutes les 'fps' (1 image/sec)
        if frame_count % fps == 0:
            try:
                # Analyse DeepFace
                # detector_backend='opencv' est le plus rapide pour le CPU
                results = DeepFace.analyze(
                    frame, 
                    actions=['emotion'], 
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                
                # Récupération de l'émotion dominante
                if isinstance(results, list):
                    dom_emotion = results[0]['dominant_emotion']
                else:
                    dom_emotion = results['dominant_emotion']
                
                emotions_list.append(dom_emotion)
                print(f"Seconde {frame_count//fps} : {dom_emotion}")
                
            except Exception as e:
                # On ignore les frames où le visage n'est pas détectable
                pass

        frame_count += 1
        
    cap.release()

    # --- Calcul des caractéristiques finales ---
    if not emotions_list:
        return {"error": "Aucun visage détecté ou vidéo illisible."}

    # Classification pour les scores
    stress_emotions = ["fear", "angry", "sad", "disgust"]
    confidence_emotions = ["happy", "neutral"]
    
    total_frames = len(emotions_list)
    stress_count = sum(1 for e in emotions_list if e in stress_emotions)
    confidence_count = sum(1 for e in emotions_list if e in confidence_emotions)
    
    # Calcul des métriques demandées
    emotion_dominant = Counter(emotions_list).most_common(1)[0][0]
    stress_score = round((stress_count / total_frames) * 100)
    confidence_score = round((confidence_count / total_frames) * 100)

    return {
        "emotion_dominant": emotion_dominant,
        "stress_score": f"{stress_score}%",
        "confidence_score": f"{confidence_score}%"
    }

# --- TEST DU SCRIPT ---
if __name__ == "__main__":
    # Remplacez par le chemin de votre vidéo locale pour tester
    PATH_TO_VIDEO = vid_stress
    
    result = analyze_video_offline(PATH_TO_VIDEO)
    
    if result:
        print("\n" + "="*30)
        print("RESULTATS DE L'ANALYSE")
        print("="*30)
        print(f"Emotion Dominante : {result.get('emotion_dominant')}")
        print(f"Score de Stress    : {result.get('stress_score')}")
        print(f"Score de Confiance : {result.get('confidence_score')}")
        print("="*30)