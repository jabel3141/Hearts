from Player import Player
from Deck import Deck


class SimpleAI(Player):
    def __init__(self, name):
        super().__init__(name)

    def select_pass_card(self):
        all_cards = self.hand.clubs + self.hand.diamonds + self.hand.spades + self.hand.hearts
        return sorted(all_cards, key=Deck.card_rank_to_sort_val)[-1]

    def select_play_card(self, game_state):
        plays = self.legal_plays(game_state)

        if game_state.trick.suit == 'x':
            return sorted(plays, key=Deck.card_rank_to_sort_val)[0]  # if leading, play lowest legal value
        elif game_state.trick.suit == plays[0][-1:]:
            played_cards = list(filter(lambda a: a != 0, game_state.trick.trick))
            played_cards.sort(key=Deck.card_rank_to_sort_val, reverse=True)

            # Play highest card in the leading suit that does not win the trick if possible, otherwise lowest card
            augmented_plays = plays + [played_cards[0]]
            augmented_plays.sort(key=Deck.card_rank_to_sort_val)
            index = augmented_plays.index(played_cards[0])
            if index == 0:
                return augmented_plays[1]
            else:
                return augmented_plays[index - 1]
        else:
            return sorted(plays, key=Deck.card_rank_to_sort_val)[-1]  # If throwing a card away, play highest card
