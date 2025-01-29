from warnings import warn
from src.calculations.statistics import normalize
from src.config.constants import *
from typing import List, Dict


class BetMode:
    """
    ##Sample BetMode Input Criteria##
    name="base",
    title="Base Game",
    description="Starting Game Mode",
    rtp=0.97,
    cost=1.0,
    autoCloseDisabled=False,
    isFeature = False,
    isEnhancedMode=False,
    isBuyBonus=False,
    maxWin=self.winCap,
    """
    def __init__(
        self, 
        name: str, 
        title: str,
        description: str,
        cost: float, 
        rtp: float,
        maxWin: float,
        autoCloseDisabled: bool, 
        isFeature:bool, 
        isEnhancedMode: bool, 
        isBuyBonus: bool, 
        distributions: object
        ):

        self._name = name 
        self._title = title 
        self._description = description
        self._cost = cost
        self._maxWin = maxWin
        self._autoCloseBetDisabled = autoCloseDisabled
        self._isFeature = isFeature
        self._isEnhancedMode = isEnhancedMode
        self._isBuyBonus = isBuyBonus
        self._distributions = distributions
        self.checkAndSetRTP(rtp)
        self.setForceKeys()
        
    def __repr__(self):
        return (
            f"BetMode(name={self._name},  title={self._title}, description={self._description}"
            f"cost={self._cost}, maxWin={self._maxWin}, rtp={self._rtp}, autoCloseDisabled={self._autoCloseBetDisabled} "
            f"isFeature={self._isFeature}, isEnhancedMode={self._isEnhancedMode}, isBuyBonus={self._isBuyBonus} "
        )
        
    def checkAndSetRTP(self, rtp:float) -> None:
        if rtp >= 1.0:
            raise Warning(f"Return To Player is >=1.0!: {rtp}")
        self._rtp = rtp

    def setForceKeys(self):
        self._force_keys = []

    def addForceKey(self, forceKey: list):
        self._force_keys.append(str(forceKey))  # type:ignore

    def lockForceKeys(self):
        self._force_keys = tuple(sorted(self._force_keys))

    def getForceKeys(self):
        return self._force_keys

    def getName(self):
        return self._name

    def getCost(self):
        return self._cost

    def getFeature(self):
        return self._isFeature

    def getEnhancedMode(self):
        return self._isEnhancedMode

    def getAutoCloseDisabled(self):
        return self._autoCloseBetDisabled

    def getBuyBonus(self):
        return self._isBuyBonus

    def getMaxWin(self):
        return self._maxWin

    def getTitle(self):
        return self._title

    def getDescription(self):
        return self._description

    def getRTP(self):
        return self._rtp

    def getDistributions(self):
        return self._distributions
    
    def getDistributionConditions(self, targetCriteria: str) -> dict:
        for d in self.getDistributions():
            if d._criteria == targetCriteria:
                return d._conditions
        return RuntimeError(f"target critera: {targetCriteria} not found in betMode-distributions.")
