import os
import sys
import copy
from datetime import datetime, timezone
import pytest

# Ensure script directory is in sys.path
SCRIPT_DIR = r"c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills"
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import project_memory_cli
from project_memory_cli import (
    UniversalMilestoneParser,
    compute_agent_project_scores,
    apply_feedback,
    DEFAULT_SETTINGS,
)


@pytest.fixture(autouse=True)
def block_production_save(monkeypatch):
    """Garantit formellement qu'aucun test ne peut écrire dans data.json ou le cache de production."""
    monkeypatch.setattr(project_memory_cli, "save_data", lambda *args, **kwargs: None)
    monkeypatch.setattr(project_memory_cli, "save_cache", lambda *args, **kwargs: None)


def test_milestone_r_interval_parsing():
    """Vérifie le parsing de R/2026-10-22/P2D avant et après satisfaction du cycle."""
    parser = UniversalMilestoneParser(default_lambda=0.3)
    expr = "R/2026-10-22/P2D"

    # Le 25 octobre 2026 : l'occurrence du 22/10 + 2D = 24/10 est échue (dans le passé)
    now_oct25 = datetime(2026, 10, 25, 10, 0, 0)

    # 1. Avant satisfaction : last_satisfied_date = 22/10
    # Le cycle du 24/10 n'est pas encore satisfait -> overdue -> urgency = 1.0
    res_unsat = parser.parse(expr, now=now_oct25, last_satisfied_date="2026-10-22T14:25:48.956220+00:00")
    assert res_unsat.is_overdue is True
    assert res_unsat.urgency_factor == 1.0
    assert res_unsat.target_datetime is not None
    assert res_unsat.target_datetime.strftime("%Y-%m-%d") == "2026-10-24"

    # 2. Après satisfaction : last_satisfied_date = 25/10 (ou >= 24/10)
    # L'occurrence du 24/10 a été satisfaite -> la prochaine est le 26/10
    res_sat = parser.parse(expr, now=now_oct25, last_satisfied_date="2026-10-25T09:00:00")
    assert res_sat.is_overdue is False
    assert res_sat.target_datetime is not None
    assert res_sat.target_datetime.strftime("%Y-%m-%d") == "2026-10-26"
    assert 0.0 < res_sat.urgency_factor < 1.0


def test_agent_only_no_autonomy_decay():
    """Vérifie que pour un projet agent_only: true, p_scale == 1.0 et autonomy_decay == 1.0."""
    now_oct25 = datetime(2026, 10, 25, 10, 0, 0, tzinfo=timezone.utc)
    proj_stat = {
        "rotationBonus": 0.0,
        "totalReviews": 0,
        "currentScore": 50.0,
        "lastSatisfiedMilestoneDate": "2026-10-22T14:25:48.956220+00:00",
        "agent": {
            "baseScore": 50.0,
            "currentScore": 50.0,
            "rotationBonus": 10.0,
            "totalReviews": 5,
            "sessionsSinceHuman": 10,  # Ne doit pas amortir si is_agent_only=True
            "lastSatisfiedMilestoneDate": "2026-10-22T14:25:48.956220+00:00",
            "reviewHistory": [],
            "recentWorkDates": []
        }
    }

    # Calcul sans agent_only : sessions_since_human=10 amortirait massivement le score
    scores_decayed, _ = compute_agent_project_scores(
        proj_stat=copy.deepcopy(proj_stat),
        total_reviews=0,
        deadline_str="",
        milestone_str="R/2026-10-22/P2D",
        last_sat_milestone="2026-10-22T14:25:48.956220+00:00",
        rf=0.2,
        recency_weight=0.5,
        now_dt=now_oct25,
        is_agent_only=False
    )
    assert scores_decayed["p_milestone"] < 0.01  # Amorti par 0.5^10

    # Calcul avec agent_only=True : p_scale et autonomy_decay restent 1.0
    scores_agent_only, _ = compute_agent_project_scores(
        proj_stat=copy.deepcopy(proj_stat),
        total_reviews=0,
        deadline_str="",
        milestone_str="R/2026-10-22/P2D",
        last_sat_milestone="2026-10-22T14:25:48.956220+00:00",
        rf=0.2,
        recency_weight=0.5,
        now_dt=now_oct25,
        is_agent_only=True
    )
    assert scores_agent_only["p_milestone"] == 1.0
    assert scores_agent_only["p_eff"] == 1.0
    assert scores_agent_only["effective_score"] == 100.0


def test_feedback_agent_milestone_and_duration():
    """Vérifie la mise à jour de lastSatisfiedMilestoneDate et duration_minutes lors d'un feedback --agent."""
    data = {
        "settings": copy.deepcopy(DEFAULT_SETTINGS),
        "stats": {
            "projects": {
                "notes/🤖 Consolidation et Exploration Dream.md": {
                    "rotationBonus": 0.0,
                    "totalReviews": 0,
                    "lastReviewDate": "",
                    "agent_only": True,
                    "reviewHistory": [],
                    "recentWorkDates": [],
                    "agent": {
                        "baseScore": 50.0,
                        "currentScore": 50.0,
                        "totalReviews": 2,
                        "sessionsSinceHuman": 0,
                        "reviewHistory": [],
                        "recentWorkDates": []
                    }
                }
            },
            "globalStats": {
                "totalReviews": 10,
                "totalPomodoroTime": 450.0,
                "totalAgentReviews": 2,
                "totalAgentPomodoroTime": 90.0
            }
        }
    }

    # Simuler un feedback agent de 45 minutes avec action "ok"
    matched_key, new_score = apply_feedback(
        project_path="notes/🤖 Consolidation et Exploration Dream.md",
        action="ok",
        worked=True,
        data=data,
        elapsed_minutes=45.0,
        is_agent=True
    )

    proj = data["stats"]["projects"]["notes/🤖 Consolidation et Exploration Dream.md"]
    agent_obj = proj["agent"]

    # 1. Vérification sessionsSinceHuman reste 0 pour agent_only
    assert agent_obj["sessionsSinceHuman"] == 0

    # 2. Vérification duration_minutes enregistré dans reviewHistory
    assert len(agent_obj["reviewHistory"]) == 1
    assert agent_obj["reviewHistory"][-1]["duration_minutes"] == 45.0
    assert agent_obj["reviewHistory"][-1]["action"] == "ok"

    # 3. Vérification de lastSatisfiedMilestoneDate mis à jour car ratio = 45/45 = 1.0 >= 0.5
    assert "lastSatisfiedMilestoneDate" in agent_obj
    assert agent_obj["lastSatisfiedMilestoneDate"] is not None
    assert proj["lastSatisfiedMilestoneDate"] == agent_obj["lastSatisfiedMilestoneDate"]

    # 4. Vérification du cumul globalStats agent
    assert data["stats"]["globalStats"]["totalAgentReviews"] == 3
    assert data["stats"]["globalStats"]["totalAgentPomodoroTime"] == 135.0
