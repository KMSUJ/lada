import logging


class Candidate:
    def __init__(self, id=""):
        self.log = logging.getLogger(__name__)
        self.id = id
        self.score = list()

    def compare(self, other, epsilon=1e-8):
        assert len(self.score) == len(other.score)
        assert len(self.score[-1]) == len(other.score[-1])

        for i in range(-1, len(self.score) - 1):
            self_score = self.score[i][0]
            other_score = other.score[i][0]

            if self_score < other_score - epsilon:
                return -1
            elif self_score > other_score + epsilon:
                return 1

        for i in range(1, len(self.score[-1])):
            self_score = self.score[-1][i]
            other_score = other.score[-1][i]

            if self_score < other_score - epsilon:
                return -1
            elif self_score > other_score + epsilon:
                return 1

        return 0

    def __lt__(self, other):
        c = self.compare(other)
        if c != 0:
            return c < 0

        return self.id < other.id  # arbitrary order

    def shortest_score(self):
        return min(len(score) for score in self.score)

    def __eq__(self, other):
        # necessary for being a dictionary key
        return self.id == other.id

    def __hash__(self):
        # necessary for being a dictionary key
        return hash(self.id)

    def __repr__(self):
        return f'Candidate({self.id})'
