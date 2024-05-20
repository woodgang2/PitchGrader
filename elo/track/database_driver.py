import enum

import pandas as pd
import glob
import os
import sqlite3
import streamlit as st
from matplotlib import pyplot as plt

from sqlalchemy import create_engine
from tqdm import tqdm

class DatabaseDriver:
    def __init__(self, year = '', side = ''):
        self.year = year
        self.side = side
        self.df = []
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.db_file = 'radar2.db'

    def read_data(self):
        # Path pattern to match all CSV files in the current directory and all subdirectories
        path_pattern = os.path.join(self.current_dir, '**', '*.csv')

        # Use glob to get a list of CSV files in the directory and all subdirectories
        csv_files = glob.glob(path_pattern, recursive=True)

        # Filter out files containing "unverified" or "positioning" in their names
        csv_files = [f for f in csv_files if "unverified" not in f and "positioning" not in f]

        # Initialize an empty list to store DataFrames
        dfs = []

        # Loop through the list of csv files with a progress bar
        for file in tqdm(csv_files, desc="Reading CSV files"):
            # Read the csv file and append it to the list of DataFrames
            df = pd.read_csv(file)
            dfs.append(df)

        # Concatenate all the DataFrames in the list into a single DataFrame
        if dfs:  # Check if the list is not empty
            self.df = pd.concat(dfs, ignore_index=True)
            print (df)
        else:
            print("No valid CSV files found.")

    def write_data (self):
        # Path to the SQLite database file
        db_file = os.path.join(self.current_dir, 'radar2.db')

        # Create a connection to the database
        conn = sqlite3.connect(db_file)

        # Write the DataFrame to a SQL table named 'radar_data'
        self.df.to_sql('radar_data', conn, if_exists='replace', index=False)

        # Close the database connection
        conn.close()

    def write_data_parquet (self):
        self.df.to_parquet(f'radar2.parquet', engine='pyarrow', compression='LZ4')

    def retrieve_percentiles (self, player, team = None):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3{self.side}.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Percentiles_Stuff_Pitchers{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        if team != '':
            df = df [df['PitcherTeam'] == team]
        df = df [df['Pitcher'] == player]
        # print (df)
        return df

    def retrieve_percentiles_batter (self, player, team = None):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Percentiles_Batters'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        if team != '':
            df = df [df['BatterTeam'] == team]
        df = df [df['Batter'] == player]
        return df

    def retrieve_percentiles_bat_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Percentiles_Batters'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        if team != 'All':
            df = df [df['BatterTeam'] == team]
        return df
    def retrieve_percentages (self, player):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3{self.side}.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Stuff_Probabilities_Pitchers{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        df = df [df['Pitcher'] == player]
        # print (df)
        return df

    def retrieve_percentages_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Stuff_Probabilities_Pitchers{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        if (team != 'All'):
            df = df [df['PitcherTeam'] == team]
        # print (df)
        return df

    def write_percentages (self):
        db_filename = os.path.join(self.current_dir, 'radar2.db')
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Stuff_Probabilities_Pitchers{self.year}{side}'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # df.to_parquet (f'test.parquet', engine='pyarrow', compression='lz4')
        # exit (0)
        # conn.close()
        # print (df)
        self.write_data_table(df, table)
        return df

    def retrieve_percentages_batter (self, player):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Probabilities_Batters'
        # table = 'batting_variables'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        # df = df [['Batter', 'BatterTeam', 'BatterSide', 'AverageBatSpeed', 'AverageSF', 'SwingDecision', 'AverageEA', 'AverageI', 'NeutralExitSpeed', 'NeutralHR']]
        df = df [df['Batter'] == player]
        # df = df.round(3)
        # df ['AverageBatSpeed'] = df ['AverageBatSpeed'].round(2)
        # df ['NeutralExitSpeed'] = df ['NeutralExitSpeed'].round(2)
        # self.write_data(df, 'Probabilities_Batters')
        return df

    def retrieve_percentages_bat_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Probabilities_Batters'
        # table = 'batting_variables'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        # df = df [['Batter', 'BatterTeam', 'BatterSide', 'AverageBatSpeed', 'AverageSF', 'SwingDecision', 'AverageEA', 'AverageI', 'NeutralExitSpeed', 'NeutralHR']]
        if (team != 'All'):
            df = df [df['BatterTeam'] == team]
        # df = df.round(3)
        # df ['AverageBatSpeed'] = df ['AverageBatSpeed'].round(2)
        # df ['NeutralExitSpeed'] = df ['NeutralExitSpeed'].round(2)
        # self.write_data(df, 'Probabilities_Batters')
        return df

    def retrieve_percentiles_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Percentiles_Stuff_Pitchers{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # df = df[df['PitchType'] == 'Four-Seam']
        # temp = df ["xRV"].values.tolist ()
        #
        # plt.hist (temp, color = "red")
        # plt.show()
        # conn.close()
        if (team != 'All'):
            df = df [df['PitcherTeam'] == team]
        # print (df)
        return df

    def write_percentiles (self):
        db_filename = os.path.join(self.current_dir, 'radar2.db')
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Percentiles_Stuff_Pitchers{self.year}{side}'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # print (df)
        self.write_data_table(df, table)
        return df

    def retrieve_percentiles_team_bat (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Percentiles_Batters'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        if (team != 'All'):
            df = df [df['BatterTeam'] == team]
        # print (df)
        return df
    def write_percentiles_bat (self):
        db_filename = os.path.join(self.current_dir, 'radar2.db')
        table = 'Percentiles_Batters'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # print (df)
        self.write_data_table(df, table)
        return df

    def retrieve_stuff_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Pitcher_Stuff_Ratings_20_80_scale{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # temp = df ["Four-Seam"].values.tolist ()
        #
        # plt.hist (temp, bins = 100, histtype = "step", color = "red")
        # plt.show()
        # conn.close()
        if (team != 'All'):
            df = df [df['PitcherTeam'] == team]
        # print (df)
        return df

    def retrieve_location_team (self, team):
        db_filename = os.path.join(self.current_dir, f'Data/{self.year}radar3.db')
        table = f'Pitcher_Location_Ratings_20_80_scale{self.year}'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        if (team != 'All'):
            df = df [df['PitcherTeam'] == team]
        # print (df)
        return df

    def retrieve_stuff (self, player, year = None):
        if (year is None):
            year = self.year
        db_filename = os.path.join(self.current_dir, f'Data/{year}radar3{self.side}.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Pitcher_Stuff_Ratings_20_80_scale{year}{side}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        df = df [df['Pitcher'] == player]
        # print (df)
        return df

    def retrieve_stuff_history (self, player):
        df1 = self.retrieve_stuff(player, 2023)
        df2 = self.retrieve_stuff(player, 2024)
        df1['Year'] = 2023
        df2['Year'] = 2024
        df = pd.concat([df1, df2])
        return df

    def retrieve_location_history (self, player):
        df1 = self.retrieve_location(player, 2023)
        df2 = self.retrieve_location(player, 2024)
        df1['Year'] = 2023
        df2['Year'] = 2024
        df = pd.concat([df1, df2])
        return df

    def retrieve_location (self, player, year = None):
        if (year is None):
            year = self.year
        db_filename = os.path.join(self.current_dir, f'Data/{year}radar3{self.side}.db')
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Pitcher_Location_Ratings_20_80_scale{year}{side}'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        df = df [df['Pitcher'] == player]
        # print (df)
        return df

    def set_side (self, side):
        self.side = side


    def write_stuff (self):
        db_filename = os.path.join(self.current_dir, 'radar2.db')
        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Pitcher_Stuff_Ratings_20_80_scale{self.year}{side}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        self.write_data_table(df, table)
        # print (df)
        return df
    def write_locations (self):
        db_filename = os.path.join(self.current_dir, 'radar4.db')
        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        side = f'_{self.side}'
        if (self.side == ''):
            side = ''
        table = f'Pitcher_Location_Ratings_20_80_scale{self.year}{side}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        self.write_data_table(df, table)
        # print (df)
        return df


    def retrieve_all_pitches (self, player):
        db_filename = os.path.join(self.current_dir, f'{self.year}radar2.db')

        # Create a connection to the database
        # conn = sqlite3.connect(db_file)
        # db_filename = 'radar2.db'
        table = f'Stuff_Probabilities{self.year}'
        # table = 'Stuff_Probabilities'
        # conn = sqlite3.connect(db_filename)
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        df = df [df['Pitcher'] == player]
        # print (df)
        return df

    def read_variable_data (self, table_name = 'variables'):
        print ("Reading variable data")
        # table_name = 'variables'
        conn = sqlite3.connect(f'{self.db_file}')
        total_rows = pd.read_sql_query(f'SELECT COUNT(*) FROM {table_name}', conn).iloc[0, 0]
        chunksize = 10000
        pbar = tqdm(total=total_rows)
        df_list = []
        for chunk in pd.read_sql_query(f'SELECT * FROM {table_name}', conn, chunksize=chunksize):
            df_list.append(chunk)
            pbar.update(chunk.shape[0])
        input_variables_df = pd.concat(df_list, ignore_index=True)
        pbar.close()
        # print (self.radar_df ['PitchCall'].unique ())
        value_map = {
            'FoulBallNotFieldable' : 'Foul',
            'FoulBallFieldable' : 'Foul',
            'FoulBall' : 'Foul',
            'WildPitch' : 'Ball',
            'SwinginStrike' : 'SwingingStrike',
            'StirkeCalled' : 'StrikeCalled',
            'BallinDirt' : 'Ball',
            'BallCalled' : 'Ball'
        }
        input_variables_df['PitchCall'] = input_variables_df['PitchCall'].replace(value_map)
        input_variables_df = input_variables_df[input_variables_df['PitchCall'] != 'Undefined']
        input_variables_df = input_variables_df[input_variables_df['PitchCall'] != 'CatchersInterference']
        input_variables_df = input_variables_df[input_variables_df['PitchCall'] != 'BattersInterference']
        value_map = {
            'Flyball' : 'FlyBall',
            'Popup' : 'FlyBall',
            'PopUp' : 'FlyBall',
            'Groundball' : 'GroundBall',
            'groundBall' : 'GroundBall'
        }
        input_variables_df['TaggedHitType'] = input_variables_df['TaggedHitType'].replace(value_map)
        # input_variables_df = input_variables_df[input_variables_df['TaggedHitType'] != 'Undefined']
        input_variables_df = input_variables_df[input_variables_df['TaggedHitType'] != 'Bunt']
        input_variables_df = input_variables_df[input_variables_df['TaggedHitType'] != ',']
        # input_variables_df = input_variables_df.loc[(input_variables_df['PitchType'] == 'Cutter') & (input_variables_df['DifferenceRS'] != 0), 'PitchType'] = 'Cutter_S'
        # input_variables_df.loc[(input_variables_df['PitchType'] == 'Cutter') & (input_variables_df['DifferenceRS'] != 0), 'PitchType'] = 'Cutter_S'
        # input_variables_df = input_variables_df.merge(
        #     self.radar_df[['PitchUID', 'AutoPitchType']],
        #     on='PitchUID',
        #     how='left'
        input_variables_df = input_variables_df.drop_duplicates(subset='PitchUID', keep='first')
        # input_variables_df.loc[(input_variables_df['PitchType'] == 'Fastball') & (input_variables_df['AutoPitchType'] != 'Changeup'), 'PitchType'] = input_variables_df['AutoPitchType']
        # input_variables_df.loc[(input_variables_df['PitchType'] == 'Fastball') & (input_variables_df['AutoPitchType'] == 'Changeup'), 'PitchType'] = 'Sinker'
        # input_variables_df = input_variables_df.drop ('AutoPitchType', axis = 1)
        print (input_variables_df ['PitchCall'].unique ())
        print (input_variables_df ['TaggedHitType'].unique ())
        print (input_variables_df ['PitchType'].unique ())

        # print (input_variables_df)
        # self.radar_df.to_sql ('radar_data', conn, if_exists='replace', index=False)
        conn.close()
        return input_variables_df

    def write_data_table (self, df, table = 'variables', number = 3):#_Pitchers'):
        # numeric_cols = self.input_variables_df.select_dtypes(include='number').columns.tolist()
        #
        # averages_df = self.input_variables_df.groupby(['Pitcher', 'PitchType'])[numeric_cols].mean().reset_index()
        # averages_df[numeric_cols] = averages_df[numeric_cols].apply(lambda x: round(x, 2))
        # averages_df = averages_df.merge(self.input_variables_df[['Pitcher', 'PitcherTeam', 'PitcherThrows']].drop_duplicates(),
        #                                 on='Pitcher', how='left')
        # # Reordering columns to have PitcherTeam and PitcherThrows as the first two columns after Pitcher and PitchType
        # final_columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'PitchType'] + [col for col in averages_df.columns if col not in ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'PitchType']]
        # self.input_variables_df = averages_df[final_columns]
        chunk_size = 1000  # Adjust based on your needs and system capabilities
        num_chunks = len(df) // chunk_size + 1
        conn = sqlite3.connect(f'Data/{self.year}radar{number}{self.side}.db')
        conn.execute(f'DROP TABLE IF EXISTS {table}')
        with tqdm(total=len(df), desc="Writing to database") as pbar:
            for start in range(0, len(df), chunk_size):
                end = min(start + chunk_size, len(df))
                chunk = df.iloc[start:end]
                chunk.to_sql(table, conn, if_exists='append', index=False)
                pbar.update(len(chunk))
        conn.close()

    def read_table_data (self, table_name = 'radar_data'):
        print ("Reading radar data")
        conn = sqlite3.connect(f'{self.db_file}')
        total_rows = pd.read_sql_query(f'SELECT COUNT(*) FROM {table_name}', conn).iloc[0, 0]

        # Choose a chunk size
        chunksize = 10000

        # Initialize a progress bar
        pbar = tqdm(total=total_rows)

        # Placeholder DataFrame
        df_list = []

        # Read data in chunks
        for chunk in pd.read_sql_query(f'SELECT * FROM {table_name}', conn, chunksize=chunksize):
            df_list.append(chunk)
            pbar.update(chunk.shape[0])

        # Concatenate all chunks into a single DataFrame
        radar_df = pd.concat(df_list, ignore_index=True)
        # print (self.radar_df)
        # numeric_series = pd.to_numeric(self.radar_df['HitTrajectoryXc8'], errors='coerce')

        # Count the number of non-NaN values (i.e., numeric values)
        # num_numeric_values = numeric_series.notna().sum()
        # print (num_numeric_values)
        # Close the progress bar
        pbar.close()

        # Close the database connection
        print (radar_df ['PitchCall'].unique ())
        value_map = {
            # 'Fastball': 'Four-Seam',
            # 'ChangeUp': 'ChangeUp',
            'FourSeamFastBall': 'Four-Seam',
            'TwoSeamFastBall': 'Sinker',
            'Undefined': 'Other',
            # 'Knuckleball': 'Other',
            'OneSeamFastball': 'Sinker',
            ',': 'Other'
            # Add other replacements here if necessary
        }
        # radar_df['PitchType'] = radar_df['TaggedPitchType'].replace(value_map)
            # self.radar_df.to_sql ('radar_data', conn, if_exists='replace', index=False)
        print ('Finished reading radar data')
        # filtered_df = self.radar_df[self.radar_df['PitcherTeam'] == 'VIR_CAV']
        # filtered_df = filtered_df[['Pitcher']]
        # filtered_df.to_sql('UVA_Pitchers', conn, if_exists='replace', index=False)
        conn.close()
        return radar_df
    def add_column (self, columns, table = 'batting_variables'):
        radar_df = self.read_table_data()
        temp_df = self.read_table_data (table)
        temp_df = temp_df.merge (radar_df [columns], on = 'PitchUID')
        self.write_data_table (temp_df, table)

    def remove_duplicates (self, table = 'batting_variables'):
        temp_df = self.read_table_data(table)
        temp_df = temp_df.drop_duplicates(subset = 'PitchUID')
        self.write_data_table (temp_df, table)

    def write_percentages_batter (self):
        db_filename = os.path.join(self.current_dir, 'radar2.db')
        # table = 'Probabilities_Batters'
        table = 'batting_variables'
        query = f'SELECT * FROM {table}'
        engine = create_engine(f'sqlite:///{db_filename}')
        df = pd.read_sql_query(query, engine)
        # conn.close()
        df = df [['Batter', 'BatterTeam', 'BatterSide', 'AttackAngle', 'TrueBatSpeed', 'AverageBatSpeed', 'AverageHandSpeed', 'AverageBarrelSpeed', 'AverageSF', 'SwingDecision', 'AverageEA', 'AverageI', 'NeutralExitSpeed', 'NeutralHR']]
        # df = df [df['Batter'] == player]
        df = df.round(3)
        df ['AverageBatSpeed'] = df ['AverageBatSpeed'].round(2)
        df ['AverageHandSpeed'] = df ['AverageHandSpeed'].round(2)
        df ['AverageBarrelSpeed'] = df ['AverageBarrelSpeed'].round(2)
        df ['NeutralExitSpeed'] = df ['NeutralExitSpeed'].round(2)
        self.write_data_table(df, 'Probabilities_Batters')
        return df
    def update_GUI (self):
        self.write_percentages_batter()
        self.write_percentages()
        self.write_percentiles_bat()
        self.write_percentiles()
        self.write_stuff()
        self.write_locations ()
    def update_DB (self):
        self.read_data()
        self.write_data()

    def retrieve_game_logs (self, player, force_both = False):
        if (force_both is False):
            db_filename = os.path.join(self.current_dir, f'Data/game_logs{self.side}.parquet')
        else:
            db_filename = os.path.join(self.current_dir, f'Data/game_logs.parquet')
        df = pd.read_parquet(db_filename)
        df = df [df['Pitcher'] == player]
        return df

def copy_tables(source_db, target_db, table_names):
    # Connect to the source database
    src_conn = sqlite3.connect(source_db)
    src_cursor = src_conn.cursor()

    # Connect to the target database
    tgt_conn = sqlite3.connect(target_db)
    tgt_cursor = tgt_conn.cursor()

    # Iterate over each table name to copy it
    for table_name in table_names:
        # Fetch the creation SQL for each table from the source database
        src_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        create_table_sql = src_cursor.fetchone()[0]

        # Create the table in the target database
        tgt_cursor.execute(create_table_sql)
        tgt_conn.commit()

        # Copy all data from the source table to the target table
        src_cursor.execute(f"SELECT * FROM {table_name}")
        rows = src_cursor.fetchall()
        placeholders = ', '.join(['?'] * len(rows[0])) if rows else ''
        tgt_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
        tgt_conn.commit()

    # Close connections
    src_conn.close()
    tgt_conn.close()


driver = DatabaseDriver ()
# driver.retrieve_percentages_batter()
# driver.add_column(['PitchUID', 'PlayResult'], 'batting_variables')
# driver.add_column(['PitchUID', 'Angle', 'Direction'], 'batting_variables')
# driver.remove_duplicates('variables')
# driver.remove_duplicates('batting_variables')
# driver.retrieve_percentiles_team('VIR_CAV')
# driver.retrieve_percentiles("Moore, Bryson")
# driver.read_data()
# driver.write_data()
# driver.write_locations ()
# driver = DatabaseDriver ()
# driver.write_percentages()

def update_gui (year = '', side = ''):
    driver = DatabaseDriver (year, side)
    driver.write_percentages_batter()
    driver.write_percentages()
    driver.write_percentiles_bat()
    driver.write_percentiles()
    driver.write_stuff()
    driver.write_locations ()

# update_gui()
# update_gui(2023)
# update_gui(2024)