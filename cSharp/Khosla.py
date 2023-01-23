from math import sqrt#, pi

class KhoDiv:
    def __init__(self, len: float):
        self.len = len
        #self.piles = piles
    
    def base_pressure(self):
        pass


class pile:
    def __init__(self, topRl: float, BotRl: float, Hw = KhoDiv, FirstPile:bool = None, LastPile:bool = None) -> None:
        self.topRl = topRl
        self.botRl = BotRl
        self.depth = self.topRl - self.botRl
        self.Hw = Hw

        if FirstPile is None:
            FirstPile = False
        if LastPile is None:
            LastPile = False

        if FirstPile is True and LastPile is True:
            raise Exception('can\'t be both first and last pile')
        
        self.First = FirstPile
        self.Last = LastPile


        self.alpha = self.Hw.len/self.depth
        self.Laamda = (1+sqrt(1+self.alpha**2))/2

  

if __name__ == '__main__':
    #example usage
    #still making
    Hw1 = KhoDiv(48.0)
    pile1 = pile(96.0, 89.0, Hw1, LastPile= True)
    pile2 = pile(96.0, 89.0, Hw1)
    pile3 = pile(94.0, 87.0, Hw1)

    piles = [pile1, pile2, pile3]
    print(pile1.First)