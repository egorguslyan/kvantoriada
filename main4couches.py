import pandas as pd
from PyQt5 import QtWidgets
from list_account import ListAccount

if __name__ == '__main__':
    couches_data = pd.read_csv('couches.csv', delimiter=',', dtype='str')
    couches = pd.DataFrame(couches_data)
    sportsmen_data = pd.read_csv('users.csv', delimiter=',')
    sportsmen = pd.DataFrame(sportsmen_data)

    app = QtWidgets.QApplication([])
    application = ListAccount('couch', couches, sportsmen)
    application.show()
    application.exec()
