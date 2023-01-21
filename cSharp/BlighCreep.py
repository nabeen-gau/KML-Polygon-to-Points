class Headworks:
    def __init__(self, Head: float, Len: float, SpGr: float):
        self.Head = Head
        self.Len = Len #creeplength
        self.SpGr =SpGr
        self.c = self.Head/self.Len

class point():
    def __init__(self,x: float, hw: Headworks) -> None:
        self.Pos = x #creep length upto the point
        self.Hw = hw
    def upliftPressure(self):
        return self.Hw.Head - self.Hw.c * self.Pos
    def ReqThickness(self):
        return round(4/3 * (self.upliftPressure()/(self.Hw.SpGr-1)), 2)

if __name__ == "__main__":
    Hw1 = Headworks(Head = 4.0, Len = 36.0, SpGr = 2.24)
    Hw2 = Headworks(10, 72, 2.26)
    A = point(4*2+4, Hw1)
    B = point(8, Hw2)
    print(A.ReqThickness())
    print(B.ReqThickness())