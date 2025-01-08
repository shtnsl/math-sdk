class Symbol:
    def __init__(self, name:str, payTable:dict=None, specials:list[str] = None, functionMap: dict = None) -> None:
        self.name = name 
        self.payTable = payTable
        self.inWin = False 
        if specials is not None:
            self.special = True 
            for arg in specials:
                setattr(self, arg, True)
        else:
            self.special = False 

        if functionMap and name in functionMap:
            functionName = functionMap[name]
            if functionName in globals():
                globals()[functionName](self)

        self.assignPayingBool()
            
    def assignPayingBool(self):
        if self.payTable is not None:
            self.isPaying = True
        else:
            self.isPaying = False 

    def isSpecialSymbol(self):
        return self.special 

    def checkAttribute(self, *args):
        for arg in args:
            if hasattr(self, arg):
                return True 
        return False
    
    def getAttribute(self, attribute):
        return getattr(self, attribute)
    
    
    def assignAttribute(self, attributeDict: dict):
        for property,value in attributeDict:
            setattr(self, property, value)

    def __eq__(self, name:str) -> None:
        if self.name == name:
            return True 
        return False 
