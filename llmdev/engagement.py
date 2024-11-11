import math

class YTEngagementUtility:
    def __init__(self, upper_bound=20, lower_bound=0, min_score=0, max_score=25):
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.min_score = min_score
        self.max_score = max_score

    def find_engagement(self, likes, comments, views):
        # handle division by zero
        if views == 0:
            return 0

        engagement_score = (likes / views) * 100 + math.log(1 + comments)
        capped_score = min(engagement_score, self.upper_bound)
        bounded_score = max(capped_score, self.lower_bound)
        normalized_engagement = (bounded_score - self.min_score) / (self.max_score - self.min_score)
        return max(0, min(normalized_engagement, 1))

    def set_bounds(self, upper_bound=None, lower_bound=None):
        if upper_bound is not None:
            self.upper_bound = upper_bound
        if lower_bound is not None:
            self.lower_bound = lower_bound

    def set_min_max_scores(self, min_score=None, max_score=None):
        if min_score is not None:
            self.min_score = min_score
        if max_score is not None:
            self.max_score = max_score

if __name__ == "__main__":
    calculator = YTEngagementUtility(upper_bound=20, lower_bound=0, min_score=0, max_score=25)

    likes = 1000
    comments = 200
    views = 10000

    score = calculator.find_engagement(likes, comments, views)
    print(f"Normalized Engagement Score: {score}")

    calculator.set_bounds(upper_bound=15)
    calculator.set_min_max_scores(min_score=5, max_score=30)

    new_score = calculator.find_engagement(likes, comments, views)
    print(f"Updated Normalized Engagement Score: {new_score}")
