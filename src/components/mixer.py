class Mixer:

    def __init__(self, error_limit: int, scores: list[float]):
        self.errors: list[int] = [] 
        self.error_limit: int = error_limit
        self.scores: list[float] = scores

    def __compute_diff__(self, pred_conf: list[int], actual_conf: list[int]) -> list[list]:
        diff: list[int] = []
        for i in range(pred_conf):
            diff[i] = pred_conf[i] - actual_conf[i]
        return diff
    
    def __compute_weight__(self, pred_conf: list[int], actual_conf: list[int]) -> float:
        curr_weight: float = 0.0
        diffs: list[int] = self.__compute_diff__(pred_conf, actual_conf)
        for i in range(pred_conf):
            curr_weight += abs(diffs[i] * self.scores[i])
        return min(curr_weight, 1)
    
    def __store_weight__(self, weight: float): 
        self.errors.append(weight)
        if len(self.errors) > self.error_limit: self.errors.remove(self.errors[0])

    def __compute_distance(self) -> float:
        num: float = 0.0
        den: float = 0.0
        for i in range(self.errors):
            num += self.errors[i] * (i + 1)
            den += i + 1
        return num/den 
    
    def mix(self, measured: float, predicted: float, pred_conf: list[int], actual_conf: list[int]) -> float:
        curr_weight: float = self.__compute_weight__(pred_conf, actual_conf)
        self.__store_weight__(curr_weight)
        react_score: float = self.__compute_distance()
        pred_score: float = 1 - react_score
        target: float = (react_score * measured) + (pred_score * predicted)
        return target

            

