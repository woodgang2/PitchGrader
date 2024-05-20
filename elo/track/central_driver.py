import database_driver
import stuff_plus
import location_plus
def calculate_grades ():
    driver = database_driver.DatabaseDriver ()
    driver.update_DB()
    stuff_plus.generate_all()
    location_plus.generate_all()
    # driver = database_driver.DatabaseDriver ()
    database_driver.update_gui()
    database_driver.update_gui(2023)
    database_driver.update_gui(2024)
    # driver.update_GUI()
    # driver = database_driver.DatabaseDriver (2023)
    # driver.update_GUI()
    # driver = database_driver.DatabaseDriver (2024)
    # driver.update_GUI()

# calculate_grades()
table_names = ["batting_variables", "Percentiles_Batters", "Probabilities_Batters", "variable"]

# Copy tables from 'ABC.db' to 'DEF.db'
database_driver.copy_tables('radar2_old.db', 'radar2.db', table_names)
database_driver.update_gui()
database_driver.update_gui(2023)
database_driver.update_gui(2024)