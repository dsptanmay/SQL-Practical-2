import os
import sys

import pretty_errors
import pymysql as sql
import questionary as qr
from tabulate import tabulate

from rich import print

pretty_errors.activate()


class DBInterface:
    def __init__(self) -> None:
        print(sys.version)
        print(sys.executable)
        term = os.get_terminal_size()
        print("-" * term.columns)
        print("CAB DB System".center(term.columns))
        print("-" * term.columns)

        username = qr.text(
            "Enter the username for MySQL:", default="tanmay03", qmark=">>>"
        ).ask()
        password = qr.password("Enter the password for MySQL:", qmark=">>>").ask()
        try:
            sql.connect(host="localhost", user=username, password=password)
        except sql.Error as e:
            print("Credentials are wrong!")
            print(e)
            exit()
        else:
            database = qr.text("Enter the name of the database:", qmark=">>>").ask()

        try:
            self.db = db = sql.connect(
                host="localhost",
                user=username,
                password=password,
                database=database,
            )
        except sql.Error as e:
            print(e)
            exit()
        else:
            print("Successfully connected to database!")
            self.cursor = db.cursor()

        self.run()

    def run(self):
        choices = [
            "Add A New CAB",
            "Delete CAB based on VCode",
            "Show All CAB Data",
            "Show All CAB Data for 'SUZUKI' Make",
            "EXIT",
        ]

        while True:
            action = qr.select(
                "Choose an action:", choices=choices, default=choices[4], qmark=">>"
            ).ask()

            if action == choices[0]:
                self.addNewCab()
            elif action == choices[1]:
                self.delCab()
            elif action == choices[2]:
                self.showAll()
            elif action == choices[3]:
                self.showAllSpecific()
            elif action == choices[4]:
                print("Exiting the program...")
                exit(0)
            else:
                print("Error in choosing action!")
                exit()

    def addNewCab(self):
        self.cursor.execute("SELECT * FROM CABHUB;")
        results = self.cursor.fetchall()
        currentVCodes = [row[0] for row in results]
        # print(currentVCodes)
        while True:
            Vcode = qr.text(
                "Enter the vehicle code(Length=3,Digits only):",
                validate=lambda x: len(x) == 3 and x.isdigit() is True,
            ).ask()
            if Vcode not in currentVCodes:
                Vcode = int(Vcode)
                break
            else:
                print("Code has already been used! Please try a different code")

        VehicleName: str = qr.text(
            "Enter the name of the Vehicle:", validate=lambda x: 0 < len(x) <= 50
        ).ask()
        VehicleName = VehicleName.capitalize()
        Make: str = qr.text(
            "Enter the Brand of the Vehicle:", validate=lambda x: 0 < len(x) <= 15
        ).ask()
        Make = Make.capitalize()
        cabColor: str = qr.text(
            "Enter the color of the Cab:", validate=lambda x: 0 < len(x) <= 15
        ).ask()
        cabColor = cabColor.capitalize()

        capacityCab = qr.text(
            "Enter the Capacity of the Cab:",
            validate=lambda x: x.isdigit() is True and int(x) > 0,
        ).ask()
        capacityCab = int(capacityCab)

        chargesCab = qr.text(
            "Enter the Charges for the Cab:",
            validate=lambda x: x.isdigit() is True and int(x) > 0,
        ).ask()
        chargesCab = int(chargesCab)

        query = "INSERT INTO CABHUB VALUES({}, '{}', '{}', '{}', {}, {})".format(
            Vcode, VehicleName, Make, cabColor, capacityCab, chargesCab
        )
        toBeIns = (Vcode, VehicleName, Make, cabColor, capacityCab, chargesCab)
        print(toBeIns)
        try:
            self.cursor.execute(query=query)
        except sql.Error as e:
            print(e)
            print("Error in Inserting Data!")
            return
        else:
            self.db.commit()
            print("Record successfully inserted!")
        # print(Vcode, type(Vcode))

    def delCab(self):
        self.cursor.execute("SELECT * FROM CABHUB;")
        results = self.cursor.fetchall()
        if len(results) == 0:
            print("Currently, there is no data!\n")
            print("Insert some data first!")
            return
        currentVCodes = [row[0] for row in results]

        print("Current Data:\n\n")
        print(
            tabulate(
                results,
                headers=[
                    "VCODE",
                    "VEHICLE NAME",
                    "MAKE",
                    "COLOR",
                    "CAPACITY",
                    "CHARGES",
                ],
                tablefmt="fancy_grid",
            )
        )
        print("\n\n")

        while True:
            delVcode = str(input("Enter the VCode for the Cab to be deleted: "))
            if int(delVcode) not in currentVCodes:
                print("Invalid Vcode!")
            elif delVcode.isdigit() is False:
                print("Enter digits only!")
            else:
                delVcode = int(delVcode)
                break

        query = "DELETE FROM CABHUB WHERE VCode=%d" % delVcode

        try:
            self.cursor.execute(query)
        except sql.Error as e:
            print(e)
            print("Error in deleting record!")
            return
        else:
            self.db.commit()
            print("Record successfully deleted!")

    def showAll(self):
        self.cursor.execute("SELECT * FROM CABHUB;")
        results = self.cursor.fetchall()
        print(
            tabulate(
                results,
                headers=[
                    "VCode",
                    "Vehicle Name",
                    "Make",
                    "Color",
                    "Capacity",
                    "Charges",
                ],
                tablefmt="fancy_grid",
            )
        )

    def showAllSpecific(self):
        self.cursor.execute("SELECT * FROM CABHUB WHERE Make='Suzuki';")
        results = self.cursor.fetchall()
        print(
            tabulate(
                results,
                headers=[
                    "VCode",
                    "Vehicle Name",
                    "Make",
                    "Color",
                    "Capacity",
                    "Charges",
                ],
                tablefmt="fancy_grid",
            )
        )


if __name__ == "__main__":
    app = DBInterface()
