"""Untested similarity-collapse baseline. No IDs, labels or answers accepted."""
import hashlib
import math


def choose_groups(texts, query_scores, similarities, threshold=0.95):
    """Greedy complete-link grouping; strongest-query member represents a group.

    Ties between different texts use content hashes. Identical text/score ties
    use input index: representative identity may change but its text does not.
    Complete-link prevents a chain of pairwise links from merging dissimilar ends.
    """
    n = len(texts)
    if not n or len(query_scores) != n or len(similarities) != n:
        raise ValueError('Invalid group inputs.')
    if not -1 <= threshold <= 1:
        raise ValueError('Invalid threshold.')
    if any(not math.isfinite(float(s)) for s in query_scores):
        raise ValueError('Nonfinite query score.')
    if any(len(row) != n or any(not math.isfinite(float(s)) for s in row)
           for row in similarities):
        raise ValueError('Invalid similarity matrix.')
    order = sorted(range(n), key=lambda i: (
        -float(query_scores[i]), hashlib.sha256(texts[i].encode()).hexdigest(), i))
    groups = []
    for i in order:
        for group in groups:
            if all(float(similarities[i][j]) >= threshold for j in group):
                group.append(i)
                break
        else:
            groups.append([i])
    return dict(canonical_order=order, groups=groups,
                representatives=[g[0] for g in groups])
