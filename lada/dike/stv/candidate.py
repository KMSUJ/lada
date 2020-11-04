import logging
import random as rnd


class Candidate:
    def __init__(self, id=""):
        self.log = logging.getLogger(__name__)
        self.id = id
        self.score = list()

    def __lt__(self, other):
        for j in range(min(self.shortest_score(), other.shortest_score())):
            for k in range(-1, min(len(self.score), len(other.score))):
                if self.score[k][j] < other.score[k][j]:
                    return True
                elif self.score[k][j] > other.score[k][j]:
                    return False

        random_choice = rnd.choice([True, False])
        self.log.info(f'A random choice has been made: {self} {"<" if random_choice else ">"} {other}')
        return random_choice

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
