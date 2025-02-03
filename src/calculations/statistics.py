import random 

def get_random_outcome(distribution: dict, totalWeight:float = None) -> type:
    assert type(distribution) == dict, "distribution must be of type: dict "
    if totalWeight is None: totalWeight = sum(distribution.values())
    roll = random.uniform(0,totalWeight)
    cumulative = 0.0
    for value,weight in distribution.items():
        cumulative += weight
        if cumulative >= roll:
            return value 
    
    return Exception("error drawing item from distribution")

def getMean_Std_Median(dist:dict) -> tuple[float, float, float]:
    total = 0
    count = 0
    stdTotal = 0
    for win in dist:
        total += win*dist[win]
        count += dist[win]

    mean = total/count if count > 0 else 0
    median = 0
    sortedDistKeys = list(dist.keys())
    sortedDistKeys.sort()
    loopCount = 0
    gotMedian = False
    for win in sortedDistKeys:
        loopCount += dist[win]
        stdTotal += ((win-mean)**2)*dist[win]/count

        if (not gotMedian) and loopCount > count/2:
            median = win
            gotMedian = True

    return mean, stdTotal**0.5, median

def normalize(distribution)->None:
    count = 0
    for key in distribution:
        count += distribution[key]

    for key in distribution:
        distribution[key] = distribution[key]/count
