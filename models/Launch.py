from models.DataBaseManager import DatabaseManager
from datetime import datetime

class Launch:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def addLaunch(self, bank, agency, typ, number, valueUnfiltred, history, situation, IsChecked,
                  movimentDay, movimentMonth, movimentYear, emissionDay, emissionMonth, emissionYear):
        valueIntPart, valueDecimalPart = self.filterValue(valueUnfiltred)

        query = """
            INSERT INTO Launch (Bank, Agency, Typ, Number, ValueIntPart, ValueDecimalPart, History, Situation, IsChecked,
                               MovimentDay, MovimentMonth, MovimentYear, EmissionDay, EmissionMonth, EmissionYear)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(query, (bank, agency, typ, number, valueIntPart, valueDecimalPart, history, situation, IsChecked,
                                movimentDay, movimentMonth, movimentYear, emissionDay, emissionMonth, emissionYear))

    def editLaunch(self, bank, agency, typ, number, valueUnfiltred, history, IsChecked, situation, emissionDay, emissionMonth, emissionYear):
        valueIntPart, valueDecimalPart = self.filterValue(valueUnfiltred)

        query = """
            UPDATE Launch
            SET Bank = ?, Agency = ?, Typ = ?, ValueIntPart = ?, ValueDecimalPart = ?, History = ?, IsChecked = ?, Situation = ?,
                EmissionDay = ?, EmissionMonth = ?, EmissionYear = ?, MovimentDay = ?, MovimentMonth = ?, MovimentYear = ?
            WHERE Number = ?
        """
        
        self.db.execute(query, (bank, agency, typ, valueIntPart, valueDecimalPart, history, IsChecked, situation,
                                emissionDay, emissionMonth, emissionYear, datetime.today().day, datetime.today().month, datetime.today().year, number))

    def changeSituation(self, situation, number, bank, agency):
        query = """UPDATE Launch SET Situation = ? WHERE Number = ? AND Bank = ? AND Agency = ?"""
        
        self.db.execute(query, (situation, number, bank, agency))

    def filterLaunch(self, bank = "", agency = "", number = "", value = [], typ = "", emdate = [], mvdate = [], sit = '', tic = ''):
        query = "SELECT id, Bank, Agency, Typ, Number, ValueIntPart, ValueDecimalPart, History, Situation, IsChecked, MovimentDay, MovimentMonth, MovimentYear, EmissionDay, EmissionMonth, EmissionYear FROM Launch WHERE "
        queryConditions = []
        params = []

        if bank != '':
            queryConditions.append(f"Bank = ?")
            params.append(bank)    
        if sit != '':
            sit = 1 if sit == True else 0
            queryConditions.append(f"Situation = {sit}")
        if tic != '':
            tic = 1 if tic == True else 0
            queryConditions.append(f"IsChecked = {tic}")
        if agency != '':
            queryConditions.append(f"Agency = ?")
            params.append(agency)    
        if number != '':
            queryConditions.append(f"Number = ?")
            params.append(number)    
        if value:
            if len(value) == 2:
                valueIntPart = (str(value[1]).split("."))[0]
                queryConditions.append(f"ValueIntPart {value[0]} ?")
                params.append(valueIntPart)
            else:
                valueIntPart = (str(value[0]).split("."))[0]
                queryConditions.append(f"ValueIntPart = ?")
                params.append(valueIntPart)
        if typ != '':
            queryConditions.append(f"Typ = ?")
            params.append(typ)  
        if emdate:
            if len(emdate) == 2:
                queryConditions.append(f"(EmissionYear {emdate[0]} ? OR (EmissionYear = ? AND EmissionMonth {emdate[0]} ?) OR (EmissionYear = ? AND EmissionMonth = ? AND EmissionDay {emdate[0]}= ?))")
                day, month, year = str(emdate[1]).split("/")
                params.append(year)
                params.append(year)
                params.append(month)
                params.append(year)
                params.append(month)
                params.append(day)
            else:
                queryConditions.append(f"EmissionYear = ? AND EmissionMonth = ? AND EmissionDay = ?")
                day, month, year = str(emdate[0]).split("/")
                params.append(year)
                params.append(month)
                params.append(day)
        if mvdate:
            if len(mvdate) == 2:
                queryConditions.append(f"(EmissionYear {mvdate[0]} ? OR (EmissionYear = ? AND EmissionMonth {mvdate[0]} ?) OR (EmissionYear = ? AND EmissionMonth = ? AND EmissionDay {mvdate[0]}= ?))")
                day, month, year = str(mvdate[1]).split("/")
                params.append(year)
                params.append(year)
                params.append(month)
                params.append(year)
                params.append(month)
                params.append(day)
            else:
                queryConditions.append(f"EmissionYear = ? AND EmissionMonth = ? AND EmissionDay = ?")
                day, month, year = str(mvdate[0]).split("/")
                params.append(year)
                params.append(month)
                params.append(day)

        if queryConditions:
            query += (' AND '.join(queryConditions)) + ";"
            return self.db.fetchall(query, params)
        
        return self.getAllLaunches()

    def removeLaunch(self, number, bank, agency):
        query = "DELETE FROM Launch WHERE Number = ? AND Bank = ? AND Agency = ?"
        self.db.execute(query, [number, bank, agency])

    def getAllLaunches(self):
        return self.db.fetchall("SELECT id, Bank, Agency, Typ, Number, ValueIntPart, ValueDecimalPart, History, Situation, IsChecked, MovimentDay, MovimentMonth, MovimentYear, EmissionDay, EmissionMonth, EmissionYear FROM Launch")

    def getLaunch(self, number, agency, bank):
        res = self.db.fetchall("""
            SELECT Typ, ValueIntPart, ValueDecimalPart, History, IsChecked, EmissionDay, EmissionMonth, EmissionYear
            FROM Launch
            WHERE Number = ? AND Agency = ? AND Bank = ?
        """, [number, agency, bank])
        
        return res[0] if res else [''] * 8
    
    def getAllLaunchNotReleased(self):
        return self.db.fetchall(
            """
            SELECT ValueIntPart, ValueDecimalPart, Bank, Agency, Number
            FROM Launch
            WHERE Situation = 0 
            AND (EmissionYear < ? 
                OR (EmissionYear = ? AND EmissionMonth < ?) 
                OR (EmissionYear = ? AND EmissionMonth = ? AND EmissionDay <= ?))
            """,
            [str(datetime.today().year)[2:], str(datetime.today().year)[2:], datetime.today().month, 
            str(datetime.today().year)[2:], datetime.today().month, datetime.today().day]
        )
    
    def getValue(self, number):
        return self.db.fetchall("SELECT ValueIntPart, ValueDecimalPart FROM Launch WHERE Number = ?", [number])
    
    def getSituationAndValue(self, bank, agency, number):
        res = self.db.fetchall("SELECT Situation, ValueIntPart, ValueDecimalPart FROM Launch WHERE Bank = ? AND Agency = ? AND Number = ?", [bank, agency, number])
        return res[0] if res else [0, 0, 0]
    
    def getNumbersBanksAgencys(self):
        return self.db.fetchall("SELECT Bank, Agency, Number FROM Launch")
    
    def getId(self, number, bank, agency):
        res = self.db.fetchall("""
            SELECT id
            FROM Launch
            WHERE Number = ? AND Agency = ? AND Bank = ?
        """, [number, agency, bank])
        
        return res[0] if res else 0

    def filterValue(self, valueUnfiltred):
        valueSepared = str(eval(valueUnfiltred.replace(",", "."))).split(".")
        valueIntPart = int(valueSepared[0] if valueSepared[0] != '' else 0)
        valueDecimalPart = 0
        if len(valueSepared) > 1:
            valueDecimalPartEx, valueDecimalPart = divmod(int(valueSepared[1] if valueSepared[1] != '' else 0), 100)
            valueIntPart += valueDecimalPartEx
        
        return valueIntPart, int("{:02}".format(valueDecimalPart))