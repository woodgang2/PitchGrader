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

def add_sides ():
    start_year = 2023
    end_year = 2024
    # stuff_plus.add_stuff_ratings(side = stuff_plus.Side.Left)
    # stuff_plus.add_stuff_ratings(side = stuff_plus.Side.Right)
    location_plus.add_location_ratings(side = location_plus.Side.Left)
    location_plus.add_location_ratings(side = location_plus.Side.Right)
    database_driver.update_gui(side = 'Left')
    database_driver.update_gui(side = 'Right')
    for year in range(start_year, end_year + 1):
        stuff_plus.add_stuff_ratings(year = year, side = stuff_plus.Side.Left)
        stuff_plus.add_stuff_ratings(year = year, side = stuff_plus.Side.Right)
        location_plus.add_location_ratings(year = year, side = location_plus.Side.Left)
        location_plus.add_location_ratings(year = year, side = location_plus.Side.Right)
        database_driver.update_gui(year = year, side = 'Left')
        database_driver.update_gui(year = year, side = 'Right')


# calculate_grades()
add_sides()
# table_names = ["batting_variables", "Percentiles_Batters", "Probabilities_Batters", "variable"]
# database_driver.copy_tables('radar2_old.db', 'radar2.db', table_names)
# driver = database_driver.DatabaseDriver ()
# driver.update_GUI()
# driver = database_driver.DatabaseDriver (2023)
# driver.update_GUI()
# driver = database_driver.DatabaseDriver (2024)
# driver.update_GUI()