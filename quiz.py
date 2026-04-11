class Quiz:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            question=data["question"],
            answer=data["answer"],
        )