from typing import Dict, Union
import json 

class Distribution:
    def __init__(self, 
        criteria:str = None,  
        quota: int = 0, 
        winCriteria: Union[float, None] = None, 
        conditions:dict = {}, 
        requiredDistribtionConditions:list = ["reel_weights", "force_wincap", "force_freespins"],
        ):

        assert quota > 0, "non-zero quota value must be assigned"

        self._quota = quota
        self._criteria = criteria
        self._requiredDistribtionConditions = requiredDistribtionConditions
        self._winCriteria = winCriteria
        self.verifyAndSetConditions(conditions)
        
    def dictFormat(self) -> dict:
        dictFormat = {
            'criteria': self._criteria,
            'rtp': self._rtp,
            'hr': self._hr,
            'avg': self._avg,
        }
        return dictFormat
    
    def verifyAndSetConditions(self, conditions):
        conditionKeys = list(conditions.keys())
        for rk in self._requiredDistribtionConditions:
            assert rk in conditionKeys, f"condition missing required key: {rk}\n conditionKeys"
        self._conditions = conditions

    def getCriteria(self):
        return self._criteria

    def getQuota(self):
        return self._quota
    
    def getWinCriteria(self):
        return self._winCriteria 
    
    def getRequiredDistributionConditions(self):
        return self._requiredDistribtionConditions

    def __str__(self):
        return f"Criteria: {self._criteria}\nConditions: {json.dumps(self._conditions)}"
    
    def __repr__(self):
        return f"Criteria: {self._criteria}\nAvg. Win: {self._avg}\n RTP: {self._rtp}\n Hit-Rate: {self._hr}"
        
        
class DistributionConditions:
    def __init__(self, criteria: str, **kwargs: Dict[str, Dict[str, Union[float, int]]]):
        """
        DistributionCondition keys must match Distribution 
        """
        conditions = {}
        for dis,cond in kwargs:
            conditions[dis] = {
                "distribution": criteria,
                "conditions": cond
            }
        return conditions
        
        
