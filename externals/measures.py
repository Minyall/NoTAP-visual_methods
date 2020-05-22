import numpy as np
from externals.hungarian import Hungarian


class JaccardBinary:
    """
    Simple binary Jaccard-based ranking comparison, which does not take into account rank positions.
    """

    def similarity(self, gold_ranking, test_ranking):
        sx = set(gold_ranking)
        sy = set(test_ranking)
        numer = len(sx.intersection(sy))
        if numer == 0:
            return 0.0
        denom = len(sx.union(sy))
        if denom == 0:
            return 0.0
        return float(numer) / denom

    def __str__(self):
        return "%s" % self.__class__.__name__


class AverageJaccard(JaccardBinary):
    """
    A top-weighted version of Jaccard, which takes into account rank positions.
    This is based on Fagin's Average Overlap Intersection Metric.
    """

    def similarity(self, gold_ranking, test_ranking):
        k = min(len(gold_ranking), len(test_ranking))
        total = 0.0
        for i in range(1,
                       k + 1):  # takes a single topic list from ref and sampled terms,
                                # iterates over and adds a word to the check each time.
            total += JaccardBinary.similarity(self, gold_ranking[0:i], test_ranking[0:i])
        return total / k


class RankingSetAgreement:
    """
    Calculates the agreement between pairs of ranking sets, using a specified measure of
    similarity between rankings.
    """

    def __init__(self, metric=AverageJaccard()):
        self.metric = metric

    def similarity(self, rankings1, rankings2):
        """
        Calculate the overall agreement between two different ranking sets. This is given by the
        mean similarity values for all matched pairs.
        """
        self.results = None
        self.S = self.build_matrix(rankings1, rankings2)
        score, self.results = self.hungarian_matching()
        return score

    def build_matrix(self, rankings1, rankings2):
        """
        Construct the similarity matrix between the pairs of rankings in two
        different ranking sets.
        """
        rows = len(rankings1)
        cols = len(rankings2)
        S = np.zeros((rows, cols))
        for row in range(rows):
            for col in range(cols):
                S[row, col] = self.metric.similarity(rankings1[row], rankings2[col])
        return S

    def hungarian_matching(self):
        """
        Solve the Hungarian matching problem to find the best matches between columns and rows based on
        values in the specified similarity matrix.
        """
        # apply hungarian matching
        h = Hungarian()
        C = h.make_cost_matrix(self.S)
        h.calculate(C)
        results = h.get_results()
        # compute score based on similarities
        score = 0.0
        for (row, col) in results:
            score += self.S[row, col]
        score /= len(results)
        return score, results
