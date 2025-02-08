class HumanizedQueueMessage:
    def __init__(self, isLast: bool, text_piece: str = "", final_text: str = ""):
        self.isLast = isLast
        self.text_piece = text_piece
        self.final_text = final_text

    def to_dict(self):
        return {
            "isLast": self.isLast,
            "text_piece": self.text_piece,
            "final_text": self.final_text
        }
