from typing import Dict 
class SymbolStorage:
    def __init__(self, config: object, allSymbols: list):
        self.config = config
        self.symbols: Dict[str, Symbol] = {}
        for symbol in allSymbols:
            self.symbols[symbol] = Symbol(self.config, symbol)

    def create_symbol_state(self, symbol_name:str) -> object:
        return Symbol(self.config, symbol_name)

    def get_symbol(self, name: str) -> object:
        if name not in self.symbols:
            self.symbols[name] = Symbol(self.config, name)
        return self.symbols[name]
    
class Symbol:
    def __init__(self, config: object, name:str) -> None:
        self.name = name 
        self.special_functions = []
        self.special = False
        is_special = False
        for special_property in config.special_symbols.keys():
            if name in config.special_symbols[special_property]:
                setattr(self, special_property, True)
                is_special = True
            else:
                if not(hasattr(self, special_property)):
                    setattr(self, special_property, False)
        
        if is_special:
            setattr(self, 'special', True)

        self.assign_paying_bool(config)
            
    def register_special_function(self,special_function: callable) -> None:
        self.special_functions.append(special_function)
    
    def applySpecialFunction(self) -> callable:
        for fun in self.special_functions:
            fun(self)

    def assign_paying_bool(self, config) -> None:
        payingSymbols = set()
        pay_value = []
        for tup,val in config.paytable.items():
            assert type(tup[1]) == str, "paytable expects string for symbol name, (kind, symbol): value"
            payingSymbols.add(tup[1])
            if self.name == tup[1]:
                pay_value.append({str(tup[0]):val})
        if self.name not in list(payingSymbols):
            self.is_paying = False 
            self.paytable = None
        else:
            self.is_paying = True
            self.paytable = pay_value

    def is_special(self) -> bool:
        return self.special 

    def check_attribute(self, *args) -> bool:
        for arg in args:
            if hasattr(self, arg) and (type(getattr(self, arg)) != bool or getattr(self,arg)==True):
                return True 
        return False
    
    def get_attribute(self, attribute) -> type:
        return getattr(self, attribute)
    
    def assign_attribute(self, attributeDict: dict) -> None:
        for prop,value in attributeDict.items():
            setattr(self, prop, value)

    def __eq__(self, name:str) -> bool:
        if self.name == name:
            return True 
        return False 
