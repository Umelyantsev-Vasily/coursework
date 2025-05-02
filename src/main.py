from pprint import pprint

from config import FILE_EX
from src.reports import get_dataframe
from src.services import find_pfone_transactions
from src.views import accept_date

if __name__ == "__main__":
    print(accept_date("2018-04-22 18:16:00"))
    pprint(find_pfone_transactions(FILE_EX))
    print(get_dataframe(FILE_EX))
