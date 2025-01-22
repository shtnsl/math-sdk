class Symbol:
    def __init__(self, config: object, name:str) -> None:
        self.name = name 
        self.payTable = config.payTable
        self.inWin = False 
        self.specialFunctions = []
        isSpecial = False
        for specialProperty in config.specialSymbols.keys():
            if name in config.specialSymbols[specialProperty]:
                setattr(self, specialProperty, True)
                isSpecial = True
            else:
                if not(hasattr(self, specialProperty)):
                    setattr(self, specialProperty, False)
        
        if isSpecial:
            setattr(self, 'special', True)
        else:
            setattr(self, 'special', False)
        self.assignPayingBool(config)
            
    def registerSpecialFunction(self,specialFunction: callable) -> None:
        self.specialFunctions.append(specialFunction)
    
    def applySpecialFunction(self) -> callable:
        for fun in self.specialFunctions:
            fun(self)

    def assignPayingBool(self, config) -> None:
        payingSymbols = set()
        payValue = []
        for tup,val in config.payTable.items():
            assert type(tup[1]) == str, "paytable expects string for symbol name, (kind, symbol): value"
            payingSymbols.add(tup[1])
            if self.name == tup[1]:
                payValue.append({tup: val})
        if self.name not in list(payingSymbols):
            self.isPaying = False 
        else:
            self.isPaying = True
    
        self.payTable = payValue

    def isSpecialSymbol(self) -> None:
        return self.special 

    def checkAttribute(self, *args) -> None:
        for arg in args:
            if hasattr(self, arg) and (type(getattr(self, arg)) != bool or getattr(self,arg)==True):
                return True 
        return False
    
    def getAttribute(self, attribute) -> type:
        return getattr(self, attribute)
    
    def assignAttribute(self, attributeDict: dict) -> None:
        for prop,value in attributeDict.items():
            setattr(self, prop, value)

    def __eq__(self, name:str) -> None:
        if self.name == name:
            return True 
        return False 
