from models.DataBaseManager import DatabaseManager
from datetime import datetime

class Account:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def filterBalance(self, balanceUnfiltred):
        balanceSepared = str(balanceUnfiltred.replace(",", ".")).split(".")
        balanceIntPart = int(balanceSepared[0] if balanceSepared[0] != '' else 0)
        balanceDecimalPart = 0
        if len(balanceSepared) > 1:
            balanceDecimalPartEx, balanceDecimalPart = divmod(int(balanceSepared[1] if balanceSepared[1] != '' else 0), 100)
            balanceIntPart += balanceDecimalPartEx
        
        return (balanceIntPart, int(str(balanceDecimalPart).zfill(2)))

    def addAccount(self, bank, agency, name, balanceUnfiltred, day, mounth, year):
        balanceIntPart, balanceDecimalPart = self.filterBalance(balanceUnfiltred)

        query = """
            INSERT INTO Account (Bank, Agency, Name, BalanceIntPart, BalanceDecimalPart, LastMovDay, LastMovMounth, LastMovYear)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute(query, (bank, agency, name, balanceIntPart, balanceDecimalPart, day, mounth, year))

    def addBalance(self, bank, agency,  balance):
        try:
            balance = float(balance)
        except:
            balance = 0.0

        balanceIntPart, balanceDecimalPart = self.db.fetchall("SELECT BalanceIntPart, BalanceDecimalPart FROM Account WHERE BANK = ?", [bank])[0]
        oldBalance = float(f"{balanceIntPart}.{balanceDecimalPart}")

        oldBalance += balance
        oldBalanceIntPart, oldBalanceDecimalPart = str(oldBalance).split(".")
        self.db.execute("UPDATE Account SET BalanceIntPart = ?, BalanceDecimalPart = ?, LastMovDay = ?, LastMovMounth = ?, LastMovYear = ? WHERE Bank = ? AND Agency = ?", [oldBalanceIntPart, oldBalanceDecimalPart, str(datetime.today().day), str(datetime.today().month), str(datetime.today().year), bank, agency])
    
    def editAccount(self, bank, agency, name, balanceUnfiltred, day, mounth, year):
        balanceIntPart, BalanceDecimalPart = self.filterBalance(balanceUnfiltred)

        query = """
            UPDATE Account
            SET Name = ?, BalanceIntPart = ?, BalanceDecimalPart = ?,  LastMovDay = ?, LastMovMounth = ?, LastMovYear = ?
            WHERE Bank = ? AND Agency = ?  
        """
        self.db.execute(query, (name, balanceIntPart, BalanceDecimalPart, day, mounth, year, bank, agency))

    def removeAccount(self, bank, agency):
        query = "DELETE FROM Account WHERE Bank = ? AND Agency = ?"
        self.db.execute(query, (bank, agency))

    def filterAccounts(self, bank: list, agency: list, balance: list):
        query = "SELECT * FROM Account WHERE "
        queryConditions = []
        params = []

        if len(bank) == 2:
            queryConditions.append(f"Bank {bank[0]} ?")
            params.append(bank[1])    
        if len(agency) == 2:
            queryConditions.append(f"Agency {agency[0]} ?")
            params.append(agency[1])    
        if len(balance) == 2:
            queryConditions.append(f"BalanceIntPart {balance[0]} ?")
            params.append(balance[1])    

        if queryConditions:
            query += (' AND '.join(queryConditions)) + ";"
            return self.db.fetchall(query, params)
        
        return self.getAllAccounts()

    def getAllAccounts(self):
        return self.db.fetchall("SELECT * FROM Account")
    
    def getAllBanks(self):
        return list(map(lambda x: x[0], self.db.fetchall("SELECT Bank FROM Account")))
    
    def getAllAgency(self):
        return list(map(lambda x: x[0], self.db.fetchall("SELECT Agency FROM Account")))
    
    def getAllBankAndAgency(self):
        return self.db.fetchall("SELECT Bank, Agency FROM Account")

    def getBalance(self, bank, agency):
        res = self.db.fetchall("SELECT BalanceIntPart, BalanceDecimalPart FROM Account WHERE Bank = ? AND Agency = ?", [bank, agency])
        return res[0] if res else []

    def getAccount(self, bank, agency):
        res = self.db.fetchall("""
        SELECT Name, BalanceIntPart, BalanceDecimalPart, LastMovDay, LastMovMounth, LastMovYear 
        FROM Account 
        WHERE Bank = ? AND Agency = ? 
        AND (SELECT COUNT(*) FROM Account WHERE Bank = ? AND Agency = ?) = 1
        """, [bank, agency, bank, agency])

        return res[0] if res else []