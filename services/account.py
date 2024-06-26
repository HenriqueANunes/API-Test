from fastapi import status

from services.custom_http_exception import CustomHttpException

# Global dictionary to store bank account data so its state is preserved between requests without using a database
DICT_BANK = {}


def reset():
    global DICT_BANK
    DICT_BANK = {}  # Resetting the dictionary
    return 'OK'


class Account:
    """
    A class to represent a bank account.

    Attributes
    ----------
    account_id : str
        a string that represents the account id

    Methods
    -------
    get_balance():
        Returns the balance of the account.
    deposit(amount: float, destination_id: str = None):
        Deposits an amount into an account.
    withdraw(amount: float):
        Withdraws an amount from the account.
    transfer(amount: float, destination_id: str):
        Transfers an amount from the account to a destination account.
    """

    def __init__(self, account_id: str):
        self.account_id = account_id

    def get_balance(self) -> dict:
        if not self.account_id:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        if self.account_id not in DICT_BANK:
            raise CustomHttpException(status_code=status.HTTP_404_NOT_FOUND,
                                      content=0)

        return DICT_BANK[self.account_id]['balance']

    def deposit(self, amount: float, destination_id: str = None) -> dict:
        destination_id = destination_id or self.account_id

        if not destination_id:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        if amount < 0:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        if destination_id not in DICT_BANK:
            DICT_BANK[destination_id] = {
                'balance': amount,
            }

        else:
            DICT_BANK[destination_id]['balance'] += amount

        response = {
            'destination': {
                'id': destination_id,
                'balance': DICT_BANK[destination_id]['balance']
            }
        }

        return response

    def withdraw(self, amount: float) -> dict:
        if not self.account_id:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        if amount < 0:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        if self.account_id not in DICT_BANK:
            raise CustomHttpException(status_code=status.HTTP_404_NOT_FOUND,
                                      content=0)

        if amount > DICT_BANK[self.account_id]['balance']:
            raise CustomHttpException(status_code=status.HTTP_400_BAD_REQUEST,
                                      content=0)

        DICT_BANK[self.account_id]['balance'] -= amount

        response = {
            'origin': {
                'id': self.account_id,
                'balance': DICT_BANK[self.account_id]['balance']
            }
        }

        return response

    def transfer(self, amount: float, destination_id: str) -> dict:

        withdraw_response = self.withdraw(amount=amount)
        deposit_response = self.deposit(amount=amount, destination_id=destination_id)

        return {**withdraw_response, **deposit_response}
