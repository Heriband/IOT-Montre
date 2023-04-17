
class Obstacle:

    def __init__(self,niv):
        self.niv = niv
        self.position = 128

    def getPosition(self):
        return self.position
    
    def setPosition(self, p):
        self.position = p

    def getNiv(self):
        return self.niv