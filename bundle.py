import random


class Bundle:
    def __init__(self, common, rare, epic, leg, save):
        self.common = common
        self.rare = rare
        self.epic = epic
        self.leg = leg
        self.save = save

    def open(self):
        rarities = [random.randint(1, 100) for _ in range(5)]
        if all(i > 34 for i in rarities):
            rarities[0] = 20
        random.shuffle(rarities)

        cards = []
        for i in rarities:
            if i < 3:
                cards.append(random.choice(self.leg))
            elif i < 15:
                cards.append(random.choice(self.epic))
            elif i < 35:
                cards.append(random.choice(self.rare))
            else:
                cards.append(random.choice(self.common))

        return cards