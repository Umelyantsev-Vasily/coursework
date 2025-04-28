from config import FILE_EX
from src.reports import get_dataframe
from src.services import find_pfone_transactions
from src.views import accept_date

if __name__ == "__main__":
    print(accept_date("2018-05-20 15:30:00"))
    print(find_pfone_transactions(FILE_EX))
    print(get_dataframe(FILE_EX))
