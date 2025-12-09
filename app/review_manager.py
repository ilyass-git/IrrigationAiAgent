"""
Gestion des revues d'experts liées aux décisions d'irrigation.
"""
from __future__ import annotations

import datetime
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class ReviewManager:
    """Charge, enregistre et résume les revues d'expert."""

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.data: Optional[pd.DataFrame] = None
        self._ensure_file_exists()
        self.load_data()

    def _ensure_file_exists(self) -> None:
        """Crée le fichier CSV avec l'en-tête s'il n'existe pas."""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            header = (
                "review_id,decision_id,decision,decision_timestamp,"
                "review_timestamp,expert_name,stars,comment\n"
            )
            self.csv_path.write_text(header, encoding="utf-8")

    def load_data(self) -> None:
        """Charge les données depuis le fichier CSV."""
        if self.csv_path.exists():
            self.data = pd.read_csv(self.csv_path, quotechar='"', escapechar='\\')
        else:
            self.data = pd.DataFrame()

    def _persist(self) -> None:
        """Sauvegarde les données actuelles dans le CSV."""
        if self.data is not None:
            self.data.to_csv(self.csv_path, index=False)

    def add_review(
        self,
        decision_id: str,
        decision: str,
        decision_timestamp: str,
        expert_name: str,
        stars: int,
        comment: str,
    ) -> Dict:
        """Ajoute une nouvelle revue et la sauvegarde."""
        stars_clamped = max(1, min(5, int(stars)))
        review = {
            "review_id": str(uuid.uuid4()),
            "decision_id": decision_id,
            "decision": decision,
            "decision_timestamp": decision_timestamp,
            "review_timestamp": datetime.datetime.now().isoformat(),
            "expert_name": expert_name or "Expert anonyme",
            "stars": stars_clamped,
            "comment": comment or "",
        }

        columns = [
            "review_id",
            "decision_id",
            "decision",
            "decision_timestamp",
            "review_timestamp",
            "expert_name",
            "stars",
            "comment",
        ]

        if self.data is None or len(self.data) == 0:
            self.data = pd.DataFrame(columns=columns)

        new_row = pd.DataFrame([review], columns=columns)
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        self._persist()

        return review

    def get_recent_reviews(self, limit: int = 5) -> List[Dict]:
        """Retourne les dernières revues."""
        if self.data is None or len(self.data) == 0:
            return []

        recent = self.data.tail(limit).iloc[::-1]  # du plus récent au plus ancien
        records = recent.to_dict(orient="records")
        return [self._normalize_record(record) for record in records]

    def get_statistics(self) -> Dict:
        """Statistiques globales sur les revues."""
        if self.data is None or len(self.data) == 0:
            return {
                "total_reviews": 0,
                "average_stars": None,
                "last_review_at": None,
            }

        avg_stars = (
            float(self.data["stars"].mean())
            if "stars" in self.data.columns and len(self.data) > 0
            else None
        )
        last_review_at = (
            self.data["review_timestamp"].iloc[-1]
            if "review_timestamp" in self.data.columns and len(self.data) > 0
            else None
        )

        return {
            "total_reviews": int(len(self.data)),
            "average_stars": round(avg_stars, 2) if avg_stars is not None else None,
            "last_review_at": last_review_at,
        }

    def get_summary_for_llm(self, limit: int = 10) -> str:
        """Génère un résumé textuel des revues pour le LLM, focalisé sur les notes."""
        if self.data is None or len(self.data) == 0:
            return (
                "REVUES D'EXPERTS\n"
                "================\n"
                "Aucune revue disponible pour le moment.\n"
            )

        stats = self.get_statistics()
        recent_reviews = self.get_recent_reviews(limit=limit)

        # Calculer la distribution des notes
        stars_values = [int(r.get("stars", 0)) for r in recent_reviews if str(r.get("stars", "")).isdigit()]
        if not stars_values:
            return "REVUES D'EXPERTS\n================\nAucune note valide disponible.\n"
        
        avg_stars = sum(stars_values) / len(stars_values)
        low_reviews = sum(1 for s in stars_values if s < 3)
        high_reviews = sum(1 for s in stars_values if s >= 4)

        summary_lines = [
            "REVUES D'EXPERTS (NOTES)",
            "=========================",
            f"Nombre total de revues analysées : {len(recent_reviews)}",
            f"Note moyenne des revues récentes : {avg_stars:.1f} / 5",
            f"Revues négatives (<3⭐) : {low_reviews}",
            f"Revues positives (≥4⭐) : {high_reviews}",
        ]

        # Ajouter les dernières notes avec contexte minimal
        summary_lines.append("\nDERNIÈRES NOTES (les plus récentes en premier) :")
        for review in recent_reviews[:10]:
            stars = int(review.get("stars", 0))
            decision = review.get("decision", "N/A")
            # Simplifier la décision pour le résumé
            decision_short = "IRRIGUER" if "IRRIGUER" in str(decision).upper() else "NE PAS IRRIGUER"
            summary_lines.append(f"- {stars}⭐ ({decision_short})")

        # Règles basées sur les notes
        summary_lines.append("\nRÈGLES D'APPRENTISSAGE :")
        if avg_stars < 3.0:
            summary_lines.append("⚠️ ATTENTION : Note moyenne faible. Les experts critiquent les décisions récentes.")
            summary_lines.append("   → Être plus prudent et reconsidérer l'approche.")
        elif avg_stars >= 4.0:
            summary_lines.append("✓ Note moyenne excellente. Les experts approuvent les décisions récentes.")
            summary_lines.append("   → Continuer avec la même approche si conditions similaires.")
        else:
            summary_lines.append("⚠ Note moyenne acceptable mais à améliorer.")
            summary_lines.append("   → Analyser les critiques pour améliorer les décisions.")

        if low_reviews >= 3:
            summary_lines.append(f"\n🚨 ALERTE : {low_reviews} revues négatives récentes. Changer d'approche.")

        return "\n".join(summary_lines)

    def _normalize_record(self, record: Dict) -> Dict:
        """Convertit les valeurs pandas/numpy en types Python natifs."""
        normalized: Dict = {}
        for key, value in record.items():
            if pd.isna(value):
                normalized[key] = None
            elif hasattr(value, "item"):
                normalized[key] = value.item()
            else:
                normalized[key] = value
        return normalized

