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
        if all(i > 35 for i in rarities):
            rarities[0] = 20
        random.shuffle(rarities)

        cards = []
        for i in rarities:
            if i < 4:
                cards.append(random.choice(self.leg))
            elif i < 16:
                cards.append(random.choice(self.epic))
            elif i < 36:
                cards.append(random.choice(self.rare))
            else:
                cards.append(random.choice(self.common))

        return cards