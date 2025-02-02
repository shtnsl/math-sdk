from typing import Dict 
class SymbolStorage:
    def __init__(self, config: object, allSymbols: list):
        self.config = config
        self.symbols: Dict[str, Symbol] = {}
        for symbol in allSymbols:
            self.symbols[symbol] = Symbol(self.config, symbol)

    def createSymbolState(self, symbolName:str) -> object:
        return Symbol(self.config, symbolName)

    def getSymbol(self, name: str) -> object:
        if name not in self.symbols:
            self.symbols[name] = Symbol(self.config, name)
        return self.symbols[name]
    
class Symbol:
    def __init__(self, config: object, name:str) -> None:
        self.name = name 
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
                payValue.append({str(tup[0]):val})
        if self.name not in list(payingSymbols):
            self.isPaying = False 
            self.payTable = None
        else:
            self.isPaying = True
            self.payTable = payValue

    def isSpecialSymbol(self) -> bool:
        return self.special 

    def checkAttribute(self, *args) -> bool:
        for arg in args:
            if hasattr(self, arg) and (type(getattr(self, arg)) != bool or getattr(self,arg)==True):
                return True 
        return False
    
    def getAttribute(self, attribute) -> type:
        return getattr(self, attribute)
    
    def assignAttribute(self, attributeDict: dict) -> None:
        for prop,value in attributeDict.items():
            setattr(self, prop, value)

    def __eq__(self, name:str) -> bool:
        if self.name == name:
            return True 
        return False 
