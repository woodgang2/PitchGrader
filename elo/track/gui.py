import random

import numpy as np
from scipy.stats import zscore
from scipy.spatial import distance

import database_driver
import stuff_plus
import streamlit as st
import pandas as pd

# st.write("""
# # My first app
# Hello *world!*
# """)


def interpolate_color(minval, maxval, val, color_palette):
    """Interpolate between colors in color_palette where color_palette
       is an array of tuples/lists with 3 integers indicating RGB values."""
    max_index = len(color_palette)-1
    v = float(val-minval) / float(maxval-minval) * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    r1, g1, b1 = color_palette[i1]
    r2, g2, b2 = color_palette[i2]
    f = v - i1
    return int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1))

def color_for_value(value):
    # Define the color transition [0%, 50%, 100%]
    colors = [(26, 28, 244), (128, 128, 128), (255, 25, 25)]  # Blue, Grey, Red
    r, g, b = interpolate_color(0, 100, value, colors)
    return f'#{r:02x}{g:02x}{b:02x}'
def display_static_slider(label, value, max_value=100.0):
    # Calculate the percentage position of the value
    if (value != value):
        value = -1
    percentage = value
    value_str = str(int(value))
    min_width = 35  # This is the minimum width for 1-2 digit numbers
    extra_width_per_digit = 10  # Additional width for each extra digit
    bubble_width = min_width + (len(value_str) - 2) * extra_width_per_digit
    if len(value_str) < 2:
        bubble_width = min_width
    color = color_for_value(value)
    value = int (value)
    # percentage = "{:.0f}%".format(percentage)

    # Create the "slider" using markdown with custom styling
    # red #ff4b4b, yellow (255, 221, 125), darker red (255, 25, 26)
    slider_bar = f"""
        <div style='width: 100%; padding-bottom: 1rem;'>  <!-- Increase padding-bottom as needed -->
        <div style='text-align: center;'>{label}</div>
        <div style='margin-top: 1rem; background-color: #f2f2f2; border-radius: 10px; height: 10px; position: relative;'> <!-- Adjust margin-top to increase space -->
            <div style='position: absolute; top: -20px; left: {percentage}%; transform: translateX(-50%);'>
                <div style='background-color: {color}; color: white; padding: 0.5rem; border-radius: 20px; width: {bubble_width}px; text-align: center;'>
                    {value}
                </div>
            </div>
        </div>
    </div>
    """


    # Display the slider bar
    st.markdown(slider_bar, unsafe_allow_html=True)

# Example of displaying the static sliders
# col1, col2 = st.columns(2)
#
# # Display static sliders within these columns
# # display_static_slider('Overall xRun Value', 97)
# # display_static_slider('xSwStr%', 97)
# # display_static_slider('xK%', 91)
# # display_static_slider('xGB%', 92)
# with col1:
#     st.markdown(display_static_slider('Overall xRun Value', 97), unsafe_allow_html=True)
#     st.markdown(display_static_slider('xSwStr%', 97), unsafe_allow_html=True)
#
# with col2:
#     st.markdown(display_static_slider('xK%', 91), unsafe_allow_html=True)
#     st.markdown(display_static_slider('xGB%', 92), unsafe_allow_html=True)
# st.empty ()
st.markdown("""
    <style>
    .reportview-container .markdown-text-container {
        padding-top: 0rem;
    }
    .reportview-container .main .block-container{
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Your title and divider with reduced whitespace
st.title('PitchGrader')
# st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" /> ', unsafe_allow_html=True)
# st.divider ()
# st.markdown("""---""")
st.caption ('Stuff, Command, and Swing Mechanics models for collegiate players')
# st.title('Stuff+ Model (also a swing mechanics model now)')
st.write('Database last updated 4/10/2024')
st.write('Please send any questions or bug reports to wsg9mf@virginia.edu')
# Create two text input boxes for the first and last name
if 'team_flag' not in st.session_state:
    st.session_state.team_flag = False

# if 'selected_player_index' not in st.session_state:
#     st.session_state ['selected_player_index'] = 0
#
if 'player_name_update' not in st.session_state:
    st.session_state.player_name_update = ''

if 'player_name' not in st.session_state:
    st.session_state['player_name'] = ''

if 'team_name_update' not in st.session_state:
    st.session_state.team_name_update = ''

if 'team_name' not in st.session_state:
    st.session_state['team_name'] = ''

if 'disabled' not in st.session_state:
    st.session_state["disabled"] = False

# Your database initialization
# driver = database_driver.DatabaseDriver()
# stuff_driver = stuff_plus.Driver('radar2.db', 'radar_data')
# Update dataset button
col1, col2, col3 = st.columns([4, 2, 4])
with col1:
    team_toggle = st.button("Toggle team/player", key='team_toggle', type = 'primary')
#     update = st.button("Update Dataset", key='update_dataset', type = 'primary')
#     if update:
#         st.write (f"I'm just a placeholder button")
        # st.write('Updating. May take a while')
        # driver.read_data()
        # stuff_plus.process_data()
        # stuff_plus.run_model()
        # stuff_plus.generate_stuff_ratings()
        # driver.write_data()
        # st.write('Updated. You may have to reload the page to see the effects')
# Button to toggle between personal details and team view
with col2:
    random_player = st.button ("Random player", key = 'random_player')
#     team_toggle = st.button("Toggle team/player")
#     if (team_toggle):
#         st.session_state.team_flag = not st.session_state.team_flag
        # st.write (team_flag)
# team_toggle = st.button("Toggle team/player", key='team_toggle', type = 'primary')
with col3:
    show_changes_placeholder = st.empty()
year_selected = st.selectbox ("Year", options = ['Combined', 2024, 2023], index = 1, key = 'year')

year = year_selected
if (year_selected == 'Combined'):
    year = ''
    st.session_state["disabled"] = True
elif (year_selected == 2023):
    st.session_state["disabled"] = True
else:
    st.session_state['disabled'] = False
driver = database_driver.DatabaseDriver(year=year)
driver2 = database_driver.DatabaseDriver(year=(year-1))
show_changes = show_changes_placeholder.button (f"Compare pitches to previous year", key = 'show_changes', disabled=st.session_state["disabled"])
# driver = database_driver.DatabaseDriver(year=year)
# if (show_changes):
#     driver2 = database_driver.DatabaseDriver(year=(year-1))
stuff_driver = stuff_plus.Driver('radar2.db', 'radar_data')
if (team_toggle):
    st.session_state.team_flag = not st.session_state.team_flag
# random_player = st.button ("Random player", key = 'random_player')
batting_percentiles_df = driver.retrieve_percentiles_bat_team ('All')
pitching_stuff_df = driver.retrieve_stuff_team ('All')
# batting_names_raw = batting_percentiles_df ['Batter']
# pitching_names_raw = pitching_stuff_df ['Pitcher']
# combined_names_raw = pd.concat([batting_names_raw, pitching_names_raw])
# Extract names and teams, and add a label for type

batting_percentiles_df ['Role'] = 'Batter'
batting_percentiles_df ['Name'] = batting_percentiles_df ['Batter']
batting_percentiles_df ['Team'] = batting_percentiles_df ['BatterTeam']
pitching_stuff_df ['Role'] = 'Pitcher'
pitching_stuff_df ['Name'] = pitching_stuff_df ['Pitcher']
pitching_stuff_df ['Team'] = pitching_stuff_df ['PitcherTeam']
combined_df = pd.concat([batting_percentiles_df, pitching_stuff_df])
combined_df['Name_Sorted'] = combined_df['Name'].str.lstrip()
combined_df = combined_df.sort_values(by='Name_Sorted')
combined_df.reset_index(drop=True, inplace=True)
combined_names = combined_df.apply(lambda x: f"{' '.join(x['Name'].split(', ')[::-1])} - {x['Team']}, {x['Role']}", axis=1)
combined_dict = dict(zip(combined_names, combined_df['Name']))

# batting_names = batting_percentiles_df.apply(lambda x: f"{' '.join(x['Batter'].split(', ')[::-1])} - {x['BatterTeam']}, Batter", axis=1)
# # batting_dict = {f"{' '.join(x['Batter'].split(', ')[::-1])} - {x[f'BatterTeam']}, Batter": x['Batter'] for _, x in batting_percentiles_df.iterrows()}
# pitching_names = pitching_stuff_df.apply(lambda x: f"{' '.join(x['Pitcher'].split(', ')[::-1])} - {x['PitcherTeam']}, Pitcher", axis=1)
# # pitching_dict = {f"{' '.join(x['Pitcher'].split(', ')[::-1])} - {x[f'PitcherTeam']}, Pitcher": x['Pitcher'] for _, x in pitching_stuff_df.iterrows()}
# batting_dict = dict(zip(batting_names, batting_percentiles_df['Batter']))
# pitching_dict = dict(zip(pitching_names, pitching_stuff_df['Pitcher']))
# combined_dict = {**batting_dict, **pitching_dict}

pitching_stuff_df = pitching_stuff_df [pitching_stuff_df ['PitcherTeam'] != 'VIR_CAV']
team_names = sorted (pitching_stuff_df ['PitcherTeam'].unique().tolist())
options_teams = ['', 'All', 'VIR_CAV'] + team_names
# Combine into a single series
# combined_names = pd.concat([batting_names, pitching_names]).sort_values().unique()

# options = list(zip(combined_names, combined_names_raw))
# options_sorted = sorted(options, key=lambda x: x[1])
options = [''] + list(combined_names)
if random_player:
    random_option = random.choice(options)
    st.session_state['player_name'] = random_option

# batting_percentages_df = driver.retrieve_percentages_bat_team ('All')
# pitching_percentages_df = driver.retrieve_percentages_team ('All')
# pitching_stuff_df = driver.retrieve_stuff_team ('All')
# st.success (st.session_state['selected_player_index'] )
# Conditional rendering based on the toggle state
if not st.session_state.team_flag:
    # first_name = st.text_input('First Name', '', placeholder='First name', key='first_name')
    # last_name = st.text_input('Last Name', '', placeholder='Last name', key='last_name')
    # team_name = st.text_input('Team Name', '', placeholder='Team name', key='team_name')
    # st.success (st.session_state['player_name'])
    if (st.session_state.player_name_update != '') & (st.session_state['player_name'] == ''):
        st.session_state['player_name'] = st.session_state.player_name_update
    # st.success (st.session_state['player_name'])
    def pick_random ():
        random_option = random.choice(options)
        st.session_state['player_name'] = random_option
    if 'player_name' not in st.session_state:
        st.session_state['player_name'] = options[0]
    default_index = options.index(st.session_state['player_name']) if st.session_state['player_name'] in options else 0
    if default_index == 0:
        st.session_state['player_name'] = ''
    selected_name = st.selectbox('Player', options=options, index=default_index, key='player_name')
    st.session_state.player_name_update = selected_name
    team_name = ''
    # When both names have been entered, display the full name
    display_name = st.empty()
    # if first_name and last_name:
    if selected_name != '':
        # display_name = st.empty()
        # display_name.success(f'Player name: {first_name} {last_name}') #want to update this
        # name = last_name + ", " + first_name
        # name_parts = selected_name.split(' - ')[0]
        # name = name_parts.split(' ')[1] + ", " + name_parts.split(' ')[0]
        name = combined_dict.get(selected_name, '')
        # st.success (team_name)
        df = driver.retrieve_percentiles (name, team_name)
        # df = pitching_percentiles_df [pitching_percentages_df ['Pitcher'] == name]
        if (df.empty) or (selected_name.split(', ')[1] == 'Batter'):
            df = driver.retrieve_percentiles_batter(name, team_name)
            # df = batting_percentiles_df [batting_percentiles_df ['Batter'] == name]
            if (df.empty):
                #want to write update here
                # st.error(f"{last_name}, {first_name} not found. Remember that the name is case sensitive. If you're looking for a batter, keep in mind that batters need to have >100 BBE to qualify")
                st.error(f"{name} not found. Something has gone wrong in the backend! Send an email to wsg9mf@virginia.edu")
            else:
                # df = df.drop (columns = ['Batter', 'BatterTeam'])
                raw_df = driver.retrieve_percentages_batter(name)
                # raw_df = batting_percentages_df [batting_percentages_df ['Batter'] == name]
                # raw_df = df
                batter_side_counts = raw_df.groupby(['Batter', 'BatterSide']).size().unstack(fill_value=0)
                batter_side_counts['Total'] = batter_side_counts.sum(axis=1)
                try:
                    batter_side_counts['LeftProp'] = batter_side_counts['Left'] / batter_side_counts['Total']
                    batter_side_counts['RightProp'] = batter_side_counts['Right'] / batter_side_counts['Total']
                    switch_batters = batter_side_counts[(batter_side_counts['LeftProp'] > 0.04) & (batter_side_counts['RightProp'] > 0.04)].index
                    raw_df.loc[raw_df['Batter'].isin(switch_batters), 'BatterSide'] = 'Switch'
                except:
                    print ('not switch hitter')
                # display_name.success (f"Batter: {first_name} {last_name}, {raw_df ['BatterTeam'].iloc [0]}. Bats: {raw_df ['BatterSide'].iloc [0]}")
                display_name.success (f"Batter: {name}. {raw_df ['BatterTeam'].iloc [0]}. Bats: {raw_df ['BatterSide'].iloc [0]}")
                raw_df = raw_df.head (1)
                raw_df = raw_df.drop (columns = ['Batter', 'BatterTeam', 'BatterSide'])
                speed_df = raw_df [['AttackAngle', 'TrueBatSpeed', 'AverageBatSpeed', 'AverageHandSpeed', 'AverageBarrelSpeed']]
                speed_df.rename(columns={'AverageBatSpeed': 'EffectiveBatSpeed', 'AverageHandSpeed': '"HandSpeed"', 'AverageBarrelSpeed' : '"BarrelSpeed"'}, inplace=True)
                raw_df = raw_df.drop (columns = ['AttackAngle', 'TrueBatSpeed', 'AverageBatSpeed', 'AverageHandSpeed', 'AverageBarrelSpeed'])
                container = st.container()
                container.markdown("<div margin-left: auto, margin-right: auto>", unsafe_allow_html=True)
                container.dataframe(speed_df)
                container.dataframe(raw_df)
                container.markdown("</div>", unsafe_allow_html=True)
                index = 0
                def add_custom_css():
                    st.markdown("""
                        <style>
                            .block-container > .row {
                                gap: 2rem;  /* Adjust the gap size as needed */
                            }
                        </style>
                    """, unsafe_allow_html=True)

                add_custom_css()
                col1, space, col2 = st.columns([2, 1, 2])

                with col1:
                    display_static_slider('Bat Speed', df ['TrueBatSpeed'].iloc [index])
                    display_static_slider('Pitch Selection', df ['SwingDecision'].iloc [index])
                    display_static_slider('Contact Efficiency', df ['AverageEA'].iloc [index])
                    display_static_slider('Neutral Exit Speed', df ['NeutralExitSpeed'].iloc [index])

                with col2:
                    # display_static_slider('Bat-to-Ball', df ['AverageSF'].iloc [index])
                    display_static_slider('Effective Bat Speed', df ['AverageBatSpeed'].iloc [index])
                    display_static_slider('Bat-to-Ball', df ['AverageSF'].iloc [index])
                    display_static_slider('Contact Quality', df ['AverageI'].iloc [index])
                    display_static_slider('"Game Power"', df ['NeutralHR'].iloc [index])

        else:
            # location_df = driver.retrieve_location (name)
            # location_df = location_df [['Pitcher', 'Overall']]
            # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
            # location_df = location_df.rename(columns={'Overall': 'Command'})
            # # st.dataframe (location_df)
            # stuff_df = driver.retrieve_stuff (name)
            # stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
            # stuff_df = stuff_df.round(0)

            if (show_changes):
                location_df = driver.retrieve_location (name)
                location_df = location_df [['Pitcher', 'Overall']]
                location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                # st.dataframe (location_df)
                stuff_df1 = driver.retrieve_stuff (name)
                stuff_df1 = stuff_df1.merge (location_df, on = 'Pitcher')
                stuff_df1 = stuff_df1.round(0)
                location_df = driver2.retrieve_location (name)
                location_df = location_df [['Pitcher', 'Overall']]
                location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                # st.dataframe (location_df)
                stuff_df2 = driver2.retrieve_stuff (name)
                # st.dataframe (stuff_df2)
                stuff_df2 = stuff_df2.merge (location_df, on = 'Pitcher')
                stuff_df2 = stuff_df2.round(0)
                # st.dataframe (stuff_df2)
                merged_df = stuff_df1.merge(stuff_df2, on='Pitcher', how='left', suffixes=('_df2', '_df1'))
                # st.dataframe (merged_df)
                # st.dataframe (merged_df)
                def calculate_and_format(row, col):
                    original = row[f"{col}_df2"]
                    if pd.isna(row[f"{col}_df1"]) or pd.isna(row[f"{col}_df2"]):
                        if isinstance(original, (int, float)) and not pd.isna (row[f"{col}_df2"]):
                            return str(round (original))
                        else:
                            return str (original)
                    else:
                        # Check if both values are numbers before attempting to calculate difference
                        if isinstance(original, (int, float)) and isinstance(row[f"{col}_df1"], (int, float)):
                            difference = original - row[f"{col}_df1"]
                            sign = '+' if difference >= 0 else ''
                            return f"{round (original)} ({sign}{round (difference)})"
                        else:
                            return str(original)
                for col in stuff_df1.columns:
                    if col != 'Pitcher' and col in stuff_df1.columns:  # Check if column is also in df1
                        merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                # stuff_df.update(merged_df[stuff_df2.columns])
                columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                # st.empty ()
                # Drop these columns
                stuff_df = merged_df.drop(columns=columns_to_drop)
                st.empty ()
                # st.table (stuff_df)
                # st.dataframe (stuff_df)
                # stuff_df3 = merged_df.drop(columns=columns_to_drop)
                # st.table (stuff_df)
                # st.dataframe (stuff_df)
            else:
                location_df = driver.retrieve_location (name)
                location_df = location_df [['Pitcher', 'Overall']]
                location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                # st.dataframe (location_df)
                stuff_df = driver.retrieve_stuff (name)
                stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
                stuff_df = stuff_df.round(0)
            rename_columns = {
                'ChangeUp': 'CH',
                'Curveball': 'CU',
                'Cutter' : 'FC',
                'Four-Seam' : 'FF',
                'Sinker' : 'SI',
                'Slider' : 'SL',
                'Splitter' : 'FS',
                'ChangeUp Usage': 'CH%',
                'Curveball Usage': 'CU%',
                'Cutter Usage' : 'FC%',
                'Four-Seam Usage' : 'FF%',
                'Sinker Usage' : 'SI%',
                'Slider Usage' : 'SL%',
                'Splitter Usage' : 'FS%'
            }
            desired_order = ['PitchCount', 'Command', 'Overall Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
            stuff_df = stuff_df.rename(columns=rename_columns)

            # stuff_df = pitching_stuff_df [pitching_stuff_df ['Pitcher'] == name]
            stuff_df = stuff_df.drop_duplicates ('Pitcher')
            stuff_df = stuff_df.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows'])
            # stuff_df = stuff_df.drop_duplicates ('Pitcher')
            stuff_df.rename(columns={'Overall': 'Overall Stuff'}, inplace=True)
            columns_to_drop = [column for column in stuff_df.columns if column.endswith('Usage')]
            stuff_df = stuff_df.drop(columns=columns_to_drop)
            stuff_df = stuff_df.dropna(axis=1)
            # st.success (desired_order)
            # st.success (stuff_df.columns)
            actual_order = [col for col in desired_order if col in stuff_df.columns]
            # st.success (actual_order)
            stuff_df = stuff_df[actual_order]
            # st.success (stuff_df.columns)
            stuff_df = stuff_df.set_index('PitchCount')
            stuff_df.index.name = 'Pitch Count'
            # stuff_df = stuff_df[desired_order]
            # st.markdown("""
            #     <style>
            #     .centered-df {
            #         margin-left: auto;
            #         margin-right: auto;
            #     }
            #     </style>
            #     """, unsafe_allow_html=True)
            # container = st.empty ()
            container = st.container()
            container.markdown("<div margin-left: auto, margin-right: auto>", unsafe_allow_html=True)
            container.dataframe(stuff_df)
            container.markdown("</div>", unsafe_allow_html=True)

            # display_name.success (f"Pitcher: {first_name} {last_name}, {df ['PitcherTeam'].iloc [0]}. Throws: {df ['PitcherThrows'].iloc [0]}")
            display_name.success (f"Pitcher: {name}. {df ['PitcherTeam'].iloc [0]}. Throws: {df ['PitcherThrows'].iloc [0]}")
            df = df.drop(columns=['ExitSpeed', 'PitcherId'])
            df = df.drop_duplicates ('PitchType')
            df = df.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
            cols = [col for col in df.columns if col != 'xRV']
            cols.insert(2, 'xRV')
            df = df[cols]
            if (show_changes):
                df2 = driver2.retrieve_percentiles (name, team_name)
                df2 = df2.drop(columns=['ExitSpeed', 'PitcherId'])
                df2 = df2.drop_duplicates ('PitchType')
                df2 = df2.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
                cols = [col for col in df2.columns if col != 'xRV']
                cols.insert(2, 'xRV')
                df2 = df2[cols]
                # st.dataframe (stuff_df2)
                merged_df = df.merge(df2, on='PitchType', how='left', suffixes=('_df2', '_df1'))
                # st.dataframe (merged_df)
                def calculate_and_format(row, col):
                    original = row[f"{col}_df2"]
                    if pd.isna(row[f"{col}_df1"]):
                        if isinstance(original, (int, float)) and not pd.isna (row[f"{col}_df2"]):
                            if (col == 'Usage'):
                                return str(round (original, 2))
                            else:
                                return str(round (original))
                        else:
                            return str (original)
                    else:
                        # Check if both values are numbers before attempting to calculate difference
                        if isinstance(original, (int, float)) and isinstance(row[f"{col}_df1"], (int, float)):
                            difference = original - row[f"{col}_df1"]
                            sign = '+' if difference >= 0 else ''
                            if (col == 'Usage'):
                                return f"{round (original, 2)} ({sign}{round (difference, 2)})"
                            else:
                                return f"{round (original)} ({sign}{round (difference)})"
                        else:
                            return str(original)

                for col in df.columns:
                    if col != 'PitchType' and col in df.columns:  # Check if column is also in df1
                        merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                # st.dataframe (df)
                # st.dataframe (merged_df)
                # df.update(merged_df[df2.columns])
                columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                # st.empty ()
                # Drop these columns
                df = merged_df.drop(columns=columns_to_drop)
                # df = merged_df [[df.columns]]
                # st.dataframe (df)

            df = df.sort_values(by='Usage', ascending = False)
            # df = stuff_df.set_index('PitchType')
            df_display = df
            df_display = df_display.set_index('PitchType')
            df_display.index.name = "Pitch Type"
            st.write ("Percentiles")
            st.dataframe(df_display)
            pitch_types = df['PitchType'].unique().tolist()
            if (not show_changes):
                index = st.selectbox("Pitch Type", range(len(pitch_types)), format_func=lambda x: pitch_types[x])
                temp = df['PitchType'].iloc [index]
                # st.title (temp)
                def add_custom_css():
                    st.markdown("""
                            <style>
                                .block-container > .row {
                                    gap: 2rem;  /* Adjust the gap size as needed */
                                }
                            </style>
                        """, unsafe_allow_html=True)

                add_custom_css()
                col1, space, col2 = st.columns([2, 1, 2])

                with col1:
                    display_static_slider('xRV', df ['xRV'].iloc [index])
                    display_static_slider('xWhiff%', df ['xWhiff%'].iloc [index])
                    display_static_slider('xFoul%', df ['xFoul%'].iloc [index])

                with col2:
                    display_static_slider('xGB%', df ['xGB%'].iloc [index])
                    display_static_slider('xHH%', 100 - df ['xHH%'].iloc [index])
                    display_static_slider('xHHFB%', 100 - df ['Prob_HardFB'].iloc [index])

            st.write ("View/Edit Raws")
            prob_df = driver.retrieve_percentages(name)
            prob_df = prob_df.drop_duplicates ('PitchType')
            # prob_df = pitching_percentages_df [pitching_percentages_df ['Pitcher'] == name]
            prob_df = prob_df.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
            cols = [col for col in prob_df.columns if col != 'xRV']
            cols.insert(2, 'xRV')
            prob_df = prob_df[cols]
            prob_df = prob_df.drop(columns=['ExitSpeed', 'PitcherId'])
            prob_df ['DifferenceRS'] = prob_df [f'DifferenceRS{year}']
            prob_df ['DifferenceHB'] = prob_df [f'DifferenceHB{year}']
            prob_df ['DifferenceIVB'] = prob_df [f'DifferenceIVB{year}']
            if (show_changes):
                prob_df2 = driver2.retrieve_percentages(name)
                prob_df2 = prob_df2.drop_duplicates ('PitchType')
                # prob_df = pitching_percentages_df [pitching_percentages_df ['Pitcher'] == name]
                prob_df2 = prob_df2.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
                cols = [col for col in prob_df2.columns if col != 'xRV']
                cols.insert(2, 'xRV')
                prob_df2 = prob_df2[cols]
                prob_df2 = prob_df2.drop(columns=['ExitSpeed', 'PitcherId'])
                #Legacy: only 2 years
                prob_df2 ['DifferenceRS'] = prob_df2 [f'DifferenceRS{year-1}']
                prob_df2 ['DifferenceHB'] = prob_df2 [f'DifferenceHB{year-1}']
                prob_df2 ['DifferenceIVB'] = prob_df2 [f'DifferenceIVB{year-1}']
                prob_df = prob_df.drop (columns = [f'DifferenceRS{year}', f'DifferenceHB{year}', f'DifferenceIVB{year}', f'DifferenceRS{year-1}', f'DifferenceHB{year-1}', f'DifferenceIVB{year-1}'])
                prob_df2 = prob_df2.drop (columns = [f'DifferenceRS{year}', f'DifferenceHB{year}', f'DifferenceIVB{year}', f'DifferenceRS{year-1}', f'DifferenceHB{year-1}', f'DifferenceIVB{year-1}'])
                # st.dataframe (stuff_df2)
                merged_df = prob_df.merge(prob_df2, on='PitchType', how='left', suffixes=('_df2', '_df1'))
                # st.dataframe (merged_df)
                def calculate_and_format(row, col):
                    original = row[f"{col}_df2"]
                    if pd.isna(row[f"{col}_df1"]):
                        if isinstance(original, (int, float)) and not pd.isna (row[f"{col}_df2"]):
                            return str(round (original, 2))
                        else:
                            return str (original)
                    else:
                        # Check if both values are numbers before attempting to calculate difference
                        if isinstance(original, (int, float)) and isinstance(row[f"{col}_df1"], (int, float)):
                            difference = original - row[f"{col}_df1"]
                            sign = '+' if difference >= 0 else ''
                            return f"{round (original, 2)} ({sign}{round (difference, 2)})"
                        else:
                            return str(original)

                for col in prob_df.columns:
                    if col != 'PitchType' and col in prob_df.columns:  # Check if column is also in df1
                        merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                # st.dataframe (prob_df)
                # st.dataframe (merged_df)
                # prob_df.update(merged_df[prob_df2.columns])
                columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                # st.success (columns_to_drop)
                # st.empty ()
                # Drop these columns
                prob_df = merged_df.drop(columns=columns_to_drop)
                # prob_df = merged_df [[prob_df.columns]]
                # st.dataframe (prob_df)

            prob_df = prob_df.sort_values(by='Usage', ascending = False)
            prob_df = prob_df.set_index('PitchType')
            prob_df.index.name = "Pitch Type"
            input_df = st.data_editor(prob_df)
            st.write ("History")
            stuff_history_df = driver.retrieve_stuff_history(name)
            location_history_df = driver.retrieve_location_history(name)
            location_history_df = location_history_df [['Pitcher', 'Overall', 'Year']]
            location_history_df = location_history_df.rename(columns={'Overall': 'Command'})
            location_history_df = location_history_df.drop_duplicates (['Pitcher', 'Year'])
            stuff_history_df = stuff_history_df.drop_duplicates (['Pitcher', 'Year'])
            stuff_history_df = stuff_history_df.merge (location_history_df, on = 'Year')
            stuff_history_df = stuff_history_df.rename(columns=rename_columns)
            stuff_history_df ['Year'] = stuff_history_df ['Year'].astype(str)
            stuff_history_df = stuff_history_df.set_index('Year')
            stuff_history_df.index.name = 'Year'
            stuff_history_df.rename(columns={'Overall': 'Overall Stuff', 'PitcherTeam' : 'Team'}, inplace=True)
            stuff_history_df [desired_order] = stuff_history_df [desired_order].round(0)
            desired_order = ['Team', 'PitchCount', 'Command', 'Overall Stuff', 'FF', 'FF%', 'SI', 'SI%', 'FC', 'FC%', 'SL', 'SL%', 'CU', 'CU%', 'FS', 'FS%', 'CH', 'CH%']
            stuff_history_df = stuff_history_df[desired_order]
            # columns_to_drop = [column for column in stuff_history_df.columns if column.endswith('Usage')]
            # stuff_history_df = stuff_history_df.drop(columns=columns_to_drop)
            stuff_history_df = stuff_history_df.dropna(axis=1, how = 'all')
            # stuff_history_df.update(stuff_history_df.filter(like='%').apply(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x))
            stuff_history_df.loc[:, stuff_history_df.columns.str.contains('%')] = stuff_history_df.filter(like='%').applymap(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x)
            st.dataframe (stuff_history_df)
            # actual_order = [col for col in desired_order if col in stuff_history_df.columns]
            # stuff_history_df = stuff_history_df[actual_order]
            # st.dataframe (stuff_history_df)
            # update = st.button("Update Percentiles", key='update_percentiles', type = 'secondary')
            # st.write ("Game Log")

            #TODO: this

            # def calculate_mahalanobis(df, columns_to_be_compared, df_target):
            #     df_scaled = df[columns_to_be_compared].apply(zscore)
            #     # st.dataframe (df_scaled)
            #     # Calculating the covariance matrix of the standardized metrics
            #     covariance_matrix = np.cov(df_scaled, rowvar=False)
            #     # Inverting the covariance matrix
            #     inv_covariance_matrix = np.linalg.inv(covariance_matrix)
            #     # Initialize a matrix to hold Mahalanobis distances
            #     distances = np.zeros((df_scaled.shape[0], df_scaled.shape[0]))
            #
            #     # Calculate the Mahalanobis distance between each pair of points
            #     for j in range(len(df_scaled)):
            #         row_i = df_target.iloc[0]
            #         row_j = df_scaled.iloc[j]
            #         # Difference vector between two rows
            #         diff = row_i - row_j
            #         # Distance calculation
            #         dist = np.sqrt(np.dot(np.dot(diff, inv_covariance_matrix), diff.T))
            #         distances[j] = dist
            #
            #     return distances
            #
            # def compute_weights(distances, epsilon=0.01):
            #     # Using reciprocal of distance as weight; adding epsilon to avoid division by zero
            #     weights = 1 / (distances + epsilon)
            #     # Normalizing weights so they sum to one across each row
            #     normalized_weights = weights / weights.sum(axis=1)[:, np.newaxis]
            #     return normalized_weights
            #
            # # Function to sample next year's performance using weighted sampling
            # def sample_performance(df, weights, num_samples=1000):
            #     # Placeholder for sampled indices
            #     sampled_indices = np.zeros((df.shape[0], num_samples), dtype=int)
            #     for i in range(df.shape[0]):
            #         # Sampling indices based on weights
            #         sampled_indices[i, :] = np.random.choice(df.index, size=num_samples, p=weights[i])
            #     return sampled_indices
            #
            # def monte_carlo_simulation(df, sampled_indices, performance_metrics):
            #     # Dictionary to store simulation results
            #     simulation_results = {metric: [] for metric in performance_metrics}
            #     # Perform simulations
            #     for metric in performance_metrics:
            #         for i in range(df.shape[0]):
            #             # Sampling performance data based on sampled indices for each metric
            #             sampled_data = df.loc[sampled_indices[i], 'Stuff_diff']
            #             # Calculating summary statistics for each player
            #             simulation_results[metric].append({
            #                 'mean': np.mean(sampled_data),
            #                 'std': np.std(sampled_data),
            #                 '5th_percentile': np.percentile(sampled_data, 5),
            #                 '95th_percentile': np.percentile(sampled_data, 95)
            #             })
            #     return simulation_results
            # st.success ("test")
            # location_df = driver.retrieve_location_team ('All')
            # location_df = location_df [['Pitcher', 'Overall']]
            # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
            # location_df = location_df.rename(columns={'Overall': 'Command'})
            # stuff_df = driver.retrieve_stuff_team ('All')
            # stuff_df = stuff_df.rename(columns={'Overall': 'Stuff'})
            # stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
            # # stuff_df = stuff_df.round(0)
            # prob_MC_df = driver2.retrieve_percentages_team ('All')
            # stuff_df = stuff_df.drop_duplicates(subset=['Pitcher'])
            # stuff_df = stuff_df.set_index('Pitcher')
            # stuff_df = stuff_df [stuff_df['PitchCount'] >= 80]
            #
            # stuff_df2 = driver2.retrieve_stuff_team ('All')
            # stuff_df2 = stuff_df2.rename(columns={'Overall': 'Stuff'})
            # stuff_df2 = stuff_df2.merge (location_df, on = 'Pitcher')
            # stuff_df2 = stuff_df2.drop_duplicates(subset=['Pitcher'])
            # stuff_df2 = stuff_df2.set_index('Pitcher')
            # stuff_df2 = stuff_df2 [stuff_df2['PitchCount'] >= 80]
            #
            # def get_stuff(row):
            #     pitch_type = row['PitchType']
            #     pitcher = row['Pitcher']
            #     if pitcher in stuff_df.index:
            #         return stuff_df.at[pitcher, pitch_type]
            #     return None
            # # Apply function to prob_MC_df
            # prob_MC_df['Stuff_new'] = prob_MC_df.apply(get_stuff, axis=1)
            # stuff_df = stuff_df2
            # prob_MC_df['Stuff_old'] = prob_MC_df.apply(get_stuff, axis=1)
            # prob_MC_df = prob_MC_df.dropna(subset=['Stuff_new', 'Stuff_old'])
            # prob_MC_df ['Stuff_diff'] = prob_MC_df['Stuff_new'] - prob_MC_df['Stuff_old']
            # # st.empty ()
            # # prob_MC_df = prob_MC_df [prob_MC_df['PitchCount'] >= 80]
            # st.dataframe (prob_MC_df)
            # st.dataframe (stuff_df)
            # columns_to_be_compared = ['RelSpeed', 'InducedVertBreak', 'HorzBreak']
            # # Assuming calculate_mahalanobis is defined
            # st.empty ()
            # prob_df = prob_df [prob_df.index == 'Four-Seam']
            # distances = calculate_mahalanobis(prob_MC_df, columns_to_be_compared, prob_df)
            # weights = compute_weights(distances)
            # sampled_indices = sample_performance(prob_MC_df, weights)
            # simulation_results = monte_carlo_simulation(prob_MC_df, sampled_indices, columns_to_be_compared)
            # st.table (simulation_results)
    # df = pd.read_csv("my_data.csv")
    # st.line_chart(df)
else:
    # st.success (st.session_state['team_name'])
    # team_name = st.text_input('Team ID (from trackman)', '', placeholder='Team ID (UVA is VIR_CAV) - Enter "All" to see all players', key='team_name')
    # team_name = st.selectbox('Team ID (UVA is VIR_CAV)', options=options_teams, key='team_name')
    if (st.session_state.team_name_update != '') & (st.session_state['team_name'] == ''):
        st.session_state['team_name'] = st.session_state.team_name_update
    # st.success (st.session_state['player_name'])
    st.session_state['team_name'] = st.session_state['team_name']
    default_index = options_teams.index(st.session_state['team_name']) if st.session_state['team_name'] in options_teams else 0
    if default_index == 0:
        st.session_state['team_name'] = ''
    # st.session_state['team_name'] = st.session_state['team_name']
    team_name = st.selectbox('Team ID (UVA is VIR_CAV)', options=options_teams, index= default_index, key='team_name')
    # st.success ('n2', team_name, 'h')
    # st.success (team_name)
    st.session_state.team_name_update = team_name
    # st.success ('n1')
    min_pitch = st.text_input('Minimum Pitch Count', '', placeholder='Pitch Count', key='min_pitch')
    display_name = st.empty()
    # st.success (team_name)
    if team_name != '':
        df = driver.retrieve_percentiles_team (team_name)
        # df = pitching_percentiles_df [pitching_percentiles_df ['PitcherTeam'] == team_name]
        df_bat = driver.retrieve_percentiles_team_bat (team_name)
        # df_bat = batting_percentiles_df [batting_percentiles_df ['BatterTeam'] == team_name]
        if (df.empty):
            #want to write update here
            st.error(f'{team_name} not found. Remember that the name is case sensitive')
        else:
            location_df = driver.retrieve_location_team (team_name)
            location_df = location_df [['Pitcher', 'Overall']]
            location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
            location_df = location_df.rename(columns={'Overall': 'Command'})
            stuff_df = driver.retrieve_stuff_team (team_name)
            stuff_df = stuff_df.rename(columns={'Overall': 'Stuff'})
            stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
            stuff_df = stuff_df.round(0)
            weighted_sum1 = np.sum(stuff_df['PitchCount'] * stuff_df['Stuff'])
            weighted_sum2= np.sum(stuff_df['PitchCount'] * stuff_df['Command'])
            # location_df1 = driver2.retrieve_location_team (team_name)
            # location_df1 = location_df1 [['Pitcher', 'Overall']]
            # location_df1['Overall'] = location_df1['Overall'].clip(lower=20, upper=80)
            # location_df1 = location_df1.rename(columns={'Overall': 'Command'})
            # # st.dataframe (location_df)
            # stuff_df1 = driver2.retrieve_stuff_team (team_name)
            # stuff_df1 = stuff_df1.rename(columns={'Overall': 'Stuff'})
            # stuff_df1 = stuff_df1.merge (location_df1, on = 'Pitcher')
            # stuff_df1 = stuff_df1.round(0)
            # MC_merged_df = stuff_df.merge(stuff_df1, on='Pitcher', how='left', suffixes=('_df2', '_df1'))
            unweighted_stuff = round (np.mean (stuff_df ['Stuff']))
            total_weights = np.sum(stuff_df['PitchCount'])
            weighted_stuff = round (weighted_sum1 / (total_weights+1e-6))
            weighted_command = round (weighted_sum2 / (total_weights+1e-6))
            if min_pitch:  # Check if something was entered
                try:
                    min_pitch = int(min_pitch)
                    stuff_df = stuff_df [stuff_df ['PitchCount'] >= min_pitch]
                except ValueError:
                    st.error("Invalid number for the minimum pitch count.")
            if (show_changes):
                location_df = driver2.retrieve_location_team (team_name)
                location_df = location_df [['Pitcher', 'Overall']]
                location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                # st.dataframe (location_df)
                stuff_df1 = driver2.retrieve_stuff_team (team_name)
                stuff_df1 = stuff_df1.rename(columns={'Overall': 'Stuff'})
                stuff_df1 = stuff_df1.merge (location_df, on = 'Pitcher')
                stuff_df1 = stuff_df1.round(0)
                if min_pitch:  # Check if something was entered
                    try:
                        min_pitch = int(min_pitch)
                        stuff_df1 = stuff_df1 [stuff_df1 ['PitchCount'] >= min_pitch]
                    except ValueError:
                        print ('hi')
                weighted_sum1_2 = np.sum(stuff_df1['PitchCount'] * stuff_df1['Stuff'])
                weighted_sum2_2= np.sum(stuff_df1['PitchCount'] * stuff_df1['Command'])
                unweighted_stuff_2 = round (np.mean (stuff_df1 ['Stuff']))
                total_weights_2 = np.sum(stuff_df1['PitchCount'])
                weighted_stuff_2 = round (weighted_sum1_2 / (total_weights_2+1e-6))
                weighted_command_2 = round (weighted_sum2_2 / (total_weights_2+1e-6))
                difference = weighted_command - weighted_command_2
                sign = '+' if difference >= 0 else ''
                weighted_command = f"{weighted_command} ({sign}{round (difference)})"
                difference = weighted_stuff - weighted_stuff_2
                sign = '+' if difference >= 0 else ''
                weighted_stuff = f"{weighted_stuff} ({sign}{round (difference)})"
                difference = unweighted_stuff - unweighted_stuff_2
                sign = '+' if difference >= 0 else ''
                unweighted_stuff = f"{unweighted_stuff} ({sign}{round (difference)})"
                # st.dataframe (stuff_df2)
                merged_df = stuff_df.merge(stuff_df1, on='Pitcher', how='left', suffixes=('_df2', '_df1'))
                # st.dataframe (merged_df)
                # st.dataframe (merged_df)
                def calculate_and_format(row, col):
                    original = row[f"{col}_df2"]
                    if pd.isna(row[f"{col}_df1"]) or pd.isna(row[f"{col}_df2"]):
                        if isinstance(original, (int, float)) and not pd.isna (row[f"{col}_df2"]):
                            return str(round (original))
                        else:
                            return str (original)
                    else:
                        # Check if both values are numbers before attempting to calculate difference
                        if isinstance(original, (int, float)) and isinstance(row[f"{col}_df1"], (int, float)):
                            difference = original - row[f"{col}_df1"]
                            sign = '+' if difference >= 0 else ''
                            return f"{round (original)} ({sign}{round (difference)})"
                        else:
                            return str(original)
                for col in stuff_df1.columns:
                    if col != 'Pitcher' and col in stuff_df1.columns:  # Check if column is also in df1
                        merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                # stuff_df.update(merged_df[stuff_df2.columns])
                columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                # st.empty ()
                # Drop these columns
                stuff_df = merged_df.drop(columns=columns_to_drop)
                st.empty ()
            rename_columns = {
                'ChangeUp': 'CH',
                'Curveball': 'CU',
                'Cutter' : 'FC',
                'Four-Seam' : 'FF',
                'Sinker' : 'SI',
                'Slider' : 'SL',
                'Splitter' : 'FS'
            }
            desired_order = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'PitchCount', 'Command', 'Stuff', 'Fastball%', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
            stuff_df = stuff_df.rename(columns=rename_columns)
            # stuff_df = pitching_stuff_df [pitching_stuff_df ['PitchingTeam'] == team_name]
            if team_name != 'All':
                stuff_df = stuff_df.drop (columns = ['PitcherTeam'])
            st.dataframe (stuff_df)
            stuff_df ['Fastball%'] = stuff_df ['Four-Seam_Usage'] + stuff_df ['Sinker_Usage']
            columns_to_drop = [column for column in stuff_df.columns if column.endswith('Usage')]
            stuff_df = stuff_df.drop(columns=columns_to_drop)
            stuff_df = stuff_df.drop_duplicates ('Pitcher')
            # if min_pitch:  # Check if something was entered
            #     try:
            #         min_pitch = int(min_pitch)
            #         stuff_df = stuff_df [stuff_df ['PitchCount'] >= min_pitch]
            #     except ValueError:
            #         st.error("Invalid number for the minimum pitch count.")
            actual_order = [col for col in desired_order if col in stuff_df.columns]
            # st.success (actual_order)
            stuff_df = stuff_df[actual_order]
            container = st.container()
            container.markdown("<div margin-left: auto, margin-right: auto>", unsafe_allow_html=True)
            container.dataframe(stuff_df)
            container.markdown("</div>", unsafe_allow_html=True)

            # weighted_command = round (np.sum(stuff_df['PitchCount'] * stuff_df['Command']) / (np.sum(stuff_df['PitchCount']+1e-6)))

            display_name.success (f"Team: {team_name}. Average Command: {weighted_command}, Average Stuff: {weighted_stuff} | {unweighted_stuff} unweighted")
            if (show_changes):
                df2 = driver2.retrieve_percentiles_team (team_name)
                # st.dataframe (stuff_df2)
                df ['T'] = df ['Pitcher'] + df ['PitchType']
                df2 ['T'] = df2 ['Pitcher'] + df2 ['PitchType']
                merged_df = df.merge(df2, on='T', how='left', suffixes=('_df2', '_df1'))
                # st.dataframe (merged_df)
                # st.dataframe (merged_df)
                def calculate_and_format(row, col):
                    original = row[f"{col}_df2"]
                    if pd.isna(row[f"{col}_df1"]) or pd.isna(row[f"{col}_df2"]):
                        if isinstance(original, (int, float)) and not pd.isna (row[f"{col}_df2"]):
                            if (col == 'Usage'):
                                return str(round (original, 2))
                            else:
                                return str(round (original))
                        else:
                            return str (original)
                    else:
                        # Check if both values are numbers before attempting to calculate difference
                        if isinstance(original, (int, float)) and isinstance(row[f"{col}_df1"], (int, float)):
                            difference = original - row[f"{col}_df1"]
                            sign = '+' if difference >= 0 else ''
                            if (col == 'Usage'):
                                return f"{round (original, 2)} ({sign}{round (difference, 2)})"
                            else:
                                return f"{round (original)} ({sign}{round (difference)})"
                        else:
                            return str(original)
                for col in df2.columns:
                    if col != 'T' and col in df.columns:
                        merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                # stuff_df.update(merged_df[stuff_df2.columns])
                columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                # st.empty ()
                # Drop these columns
                df = merged_df.drop(columns=columns_to_drop + ['T'])
                st.empty ()
            if (team_name == 'All'):
                df = df.drop (columns = ['Balls', 'Strikes'])
            else:
                df = df.drop (columns = ['PitcherTeam', 'Balls', 'Strikes'])
                df_bat = df_bat.drop (columns = ['BatterTeam'])
            if min_pitch:  # Check if something was entered
                try:
                    valid_pitchers = stuff_df['Pitcher']
                    df = df[df['Pitcher'].isin(valid_pitchers)]
                except ValueError:
                    print ('hey')
            cols = [col for col in df.columns if col != 'xRV']
            cols.insert(3, 'xRV')
            df = df[cols]
            # df = df.sort_values(by='Usage', ascending = False)
            st.dataframe(df)
            st.dataframe (df_bat)
            # pitch_types = df['PitchType'].unique().tolist()
            # index = st.selectbox("Pitch Type", range(len(pitch_types)), format_func=lambda x: pitch_types[x])
            # temp = df['PitchType'].iloc [index]
            # stuff_df = stuff_df.dropna(axis=1)




