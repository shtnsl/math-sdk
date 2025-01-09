class Symbol:
    def __init__(self, name:str, payTable:dict=None, specials:list[str] = None) -> None:
        self.name = name 
        self.payTable = payTable
        self.inWin = False 
        self.specialFunctions = []
        if specials is not None:
            self.special = True 
            for arg in specials:
                setattr(self, arg, True)
        else:
            self.special = False 
        self.assignPayingBool()
            
    def registerSpecialFunction(self,specialFunction: callable):
        self.specialFunctions.append(specialFunction)
    
    def applySpecialFunction(self):
        for fun in self.specialFunctions:
            fun(self)

    def assignPayingBool(self) -> None:
        if self.payTable is not None:
            self.isPaying = True
        else:
            self.isPaying = False 

    def isSpecialSymbol(self) -> None:
        return self.special 

    def checkAttribute(self, *args) -> None:
        for arg in args:
            if hasattr(self, arg):
                return True 
        return False
    
    def getAttribute(self, attribute):
        return getattr(self, attribute)
    
    def assignAttribute(self, attributeDict: dict) -> None:
        for prop,value in attributeDict.items():
            setattr(self, prop, value)

    def __eq__(self, name:str) -> None:
        if self.name == name:
            return True 
        return False 
