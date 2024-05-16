import database_driver
import stuff_plus
import location_plus
def calculate_grades ():
    driver = database_driver.DatabaseDriver ()
    driver.update_DB()
    stuff_plus.generate_all()
    location_plus.generate_all()
    # driver = database_driver.DatabaseDriver ()
    driver.update_GUI()
    driver = database_driver.DatabaseDriver (2023)
    driver.update_GUI()
    driver = database_driver.DatabaseDriver (2024)
    driver.update_GUI()

calculate_grades()