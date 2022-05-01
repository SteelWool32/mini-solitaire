class Move:
    def __init__(
        self,
        source = None,
        target = None,
        amount = 0,
        flip_source_top = False,
        flip_source_pile = False,
        flip_target_top = False,
        flip_target_pile = False
    ):
        self.source = source
        self.target = target
        self.amount = amount
        self.flip_source_top = flip_source_top
        self.flip_source_pile = flip_source_pile
        self.flip_target_top = flip_target_top
        self.flip_target_pile = flip_target_pile