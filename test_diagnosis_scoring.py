"""FINAL配点 + Q5同点優先の検証（1,024通り）"""
from collections import Counter
from itertools import product

from app import app, calculate_scores
from database import get_db

EXPECTED_WIN_RATES = {
    1: 16.3,
    2: 21.8,
    3: 11.2,
    4: 26.0,
    5: 10.9,
    6: 4.7,
    7: 5.0,
    8: 4.1,
}
EXPECTED_SCORE_TIES = 27.5
EXPECTED_Q5_ALSO_TIED = 4.1


def q5_scores_for(choice_ids):
    db = get_db()
    q5 = Counter()
    choice_id = choice_ids[-1]
    rows = db.execute(
        "SELECT type_id, score FROM choice_scores WHERE choice_id = ?",
        (choice_id,),
    ).fetchall()
    db.close()
    for row in rows:
        q5[row["type_id"]] += row["score"]
    return q5


def test_result_page_shows_type_rankings_in_ja_and_en():
    with app.test_client() as client:
        client.post(
            "/result",
            data={"choice_id": ["1", "6", "12", "15", "18"]},
            follow_redirects=True,
        )
        ja = client.get("/result").get_data(as_text=True)
        assert "🥇 1位" in ja
        assert "🥈 2位" in ja
        assert "🥉 3位" in ja
        assert "19%" not in ja
        assert "その他" not in ja

        with client.session_transaction() as sess:
            sess["lang"] = "en"
        en = client.get("/result").get_data(as_text=True)
        assert "🥇 1st" in en
        assert "🥈 2nd" in en
        assert "🥉 3rd" in en


def simulate():
    winners = Counter()
    score_ties = 0
    q5_also_tied = 0

    for picks in product(range(4), repeat=5):
        choice_ids = [q * 4 + pick + 1 for q, pick in enumerate(picks)]
        ranked = calculate_scores(choice_ids)
        winners[ranked[0]["id"]] += 1

        totals = {r["id"]: r["score"] for r in ranked}
        top = ranked[0]["score"]
        tied = [tid for tid, s in totals.items() if s == top]
        if len(tied) > 1:
            score_ties += 1
            q5 = q5_scores_for(choice_ids)
            winner_q5 = max(q5.get(t, 0) for t in tied)
            if sum(1 for t in tied if q5.get(t, 0) == winner_q5) > 1:
                q5_also_tied += 1

    return winners, score_ties, q5_also_tied


def main():
    test_result_page_shows_type_rankings_in_ja_and_en()
    winners, score_ties, q5_also_tied = simulate()

    print("=== Implementation verification ===")
    print(f"Reachable types as #1: {sorted(winners.keys())}")
    assert sorted(winners.keys()) == list(range(1, 9))

    print("\nWin rates:")
    max_diff = 0.0
    for tid in range(1, 9):
        actual = winners[tid] / 10.24
        expected = EXPECTED_WIN_RATES[tid]
        diff = abs(actual - expected)
        max_diff = max(max_diff, diff)
        print(f"  Type {tid}: {actual:5.1f}% (expected {expected:5.1f}%, diff {diff:+.1f}pp)")

    print(f"\nScore ties at top: {score_ties}/1024 ({score_ties/10.24:.1f}%)")
    print(f"Q5 also tied (needs type_id): {q5_also_tied}/1024 ({q5_also_tied/10.24:.1f}%)")

    assert max_diff <= 0.1
    assert abs(score_ties / 10.24 - EXPECTED_SCORE_TIES) <= 0.5
    assert abs(q5_also_tied / 10.24 - EXPECTED_Q5_ALSO_TIED) <= 0.5
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
