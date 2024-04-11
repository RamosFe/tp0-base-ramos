from typing import List
from .utils import Bet, store_bets, load_bets, has_won

import logging


class StoreManager:
    def __init__(self, number_of_agencies: int):
        self._expected_agencies = number_of_agencies
        self._finished_agencies = 0

    def winners_available(self) -> bool:
        return self._expected_agencies == self._finished_agencies

    def notify_agency_finished(self):
        self._finished_agencies += 1

        if self.winners_available():
            logging.info("action: sorteo | result: success")

    def store_bet(self, bets: List[Bet]):
        store_bets(bets)

    def get_winners(self, agency_id) -> List[Bet]:
        bets = load_bets()
        winners = list(filter(lambda x: has_won(x) and x.agency == agency_id, bets))
        return winners
