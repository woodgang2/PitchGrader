import random

import numpy as np
from scipy.linalg import inv
from scipy.spatial.distance import mahalanobis
from scipy.stats import zscore
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler
import matplotlib.colors as mcolors

import database_driver
import stuff_plus
import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")
st.markdown(
    """
        <style>
            .appview-container .main .block-container {{
                padding-top: {padding_top}rem;
                padding-bottom: {padding_bottom}rem;
                padding-right: {padding_right}rem;
                padding-left: {padding_left}rem;
                }}

        </style>""".format(
        padding_top=1, padding_bottom=1, padding_right = 17.5, padding_left = 17.5
    ),
    unsafe_allow_html=True,
)
# st.markdown(
#     """
#         <style>
#         button {
#             height: auto;
#             padding-right: 15px !important;
#         }
#         </style>
#     """,
#     unsafe_allow_html=True,
# )

# st.write("""
# # My first app
# Hello *world!*
# """)

# st.markdown(
#     """
#     <style>
#     .reportview-container .main .block-container {
#         max-width: 50%;
#         padding-top: 5rem;
#         padding-right: 2rem;
#         padding-left: 2rem;
#         padding-bottom: 5rem;
#     }
#     .reportview-container .main .sidebar-content {
#         width: 300px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

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
    # background_color = '#f2f2f2'
    background_color = '#c1c1c1'
    # percentage = "{:.0f}%".format(percentage)

    # Create the "slider" using markdown with custom styling
    # red #ff4b4b, yellow (255, 221, 125), darker red (255, 25, 26)
    slider_bar = f"""
        <div style='width: 100%; padding-bottom: 1rem;'>  <!-- Increase padding-bottom as needed -->
        <div style='text-align: center;'>{label}</div>
        <div style='margin-top: 1rem; background-color: {background_color}; border-radius: 10px; height: 10px; position: relative;'> <!-- Adjust margin-top to increase space -->
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
if 'calculate_team_list' not in st.session_state:
    st.session_state.calculate_team_list = True

if 'show_unranked' not in st.session_state:
    st.session_state.show_unranked = False

if 'truncate_game_log' not in st.session_state:
    st.session_state.truncate_game_log = False

@st.experimental_dialog("Settings", width="large")
def settings_dialog():
    # st.header("Settings")
    # Team List
    st.write ('Team List')
    calculate_team_list = st.checkbox("Calculate team leaderboard", value=st.session_state.get("calculate_team_list", True), help = 'By default, selecting "All" in the team view will proc a calculation of overall team ranks for stuff and command')
    st.session_state.calculate_team_list = calculate_team_list
    show_unranked = st.checkbox("Show all teams on leaderboard", value=st.session_state.get("show_unranked", False), help = 'By default, teams with insufficient pitches recorded in the database are hidden in the leaderboard')
    st.session_state.show_unranked = show_unranked
    st.write ('Game Log')
    truncate_game_log = st.checkbox("Only show games from selected year in game log", value=st.session_state.get("truncate_game_log", False), help = 'By default, games from each year included in the database are displayed in the game log')
    st.session_state.truncate_game_log = truncate_game_log

    st.markdown("&#160;")
    # Submit button to apply changes
    if st.button("Save and Exit", type = 'primary'):
        st.success ("Settings Updated!")
        st.rerun()  # Closes the dialog and reruns the app to reflect changes
@st.experimental_dialog("Readme", width="large")
def readme_dialog():
    # st.header("Settings")
    # Team List
    st.write("""
    "_Well, this year I’m told the team did well because one pitcher had a fine curve ball. I understand that a curve ball is thrown with a deliberate attempt to deceive. Surely this is not an ability we should want to foster at Harvard._"
    — A quote commonly attributed to Charles Eliot, President of Harvard, but in actuality was likely sourced from Charles Eliot Norton in 1884, Professor of the History of Art at Harvard (Hershberger, 2017).
    """)

    st.markdown("""
        A good century and then some has passed since this quote entered the annals of history, and times sure have changed. Pitches are faster, break more, and every pitcher now has an arsenal of secondary pitches relying primarily on deception.
    
        This project represents an effort to assess collegiate pitchers based off of the intrinsic quality of their pitches, opposition quality notwithstanding. Significant inspiration was taken from Cameron Grove's work on PitchingBot and Professor Alan Nathan's various papers on the physics of baseball. All data was taken from trackman, and the methodology is briefly described below.
        """)

    st.markdown (""" 
    Data: The manually tagged pitch type was used for most pitches. For "corrupted" pitch tags, the trackman autotagging tool was used. Unfortunately, the trackman auto-tagging tool is... not very good, so efforts were made to correct or otherwise remove rows relying on auto pitch type. Some pitchers will have "phantom pitches", which are likely mistags (eg. somebody has 67% of their pitches tagged as sinkers and has 1% four-seams. Mistag or not, the tiny sample sizes will likely produce figures which are more incorrect than usual). Furthermore, not all games are in the database - the trackman dataset is comprised of verified and unverified logs, and only verified logs were sourced.

    Stuff Model: The stuff model is split into three submodels - contact, foul, and in-play, and further divided into fastball models, breaking ball models, and offspeed models. No attempt is made to fit the stuff model on non-swings - stuff in this context purely represents the "nastiness" of a pitch. With this in mind, I did not incorporate the count. Gradient boosted decision trees were used to fit the submodels, and hyperparamter tuning was done with optuna. Once each submodel was fit, they transformed the full set of pitches thrown to generate probabilities for each outcome. Those probabilities were used to generate run values, those run values were normalized, and then pitchers were given stuff grades based on their expected run values. 
    
    The individual stuff pitch grades represent a pitch's expected run value relative to other pitches of that type. The expected pitch run value (not in the displayed dfs) represents the difference between the expected run value of a pitch and the average expected run value of that pitch type, and the overall grade represents the pitcher's average expected pitch run value relative to other pitchers. Relievers generally lose 6-10 stuff points when transitioning to a starting role. The stuff model assumes average command. All percentile sliders on the streamlit deployment are based off of the model's generated probabilities. 
    
    - Not every column in the displayed dfs are used as features. The full sets of features used are: \[PitchType, PitcherThrows, BatterSide, RelSpeed, InducedVertBreak, HorzBreak, SpinRate, SpinEfficiency*, AxisDifference*, RelHeight, RelSide, Extension, VAA*\] for fastballs, \[PitchType, PitcherThrows, BatterSide, RelSpeed, InducedVertBreak, HorzBreak, SpinRate, SpinEfficiency*, AxisDifference*, RelHeight, RelSide, Extension, DifferenceRS*, DifferenceIVB*, DifferenceHB*\] for breaking balls and offspeeds (* ~> calculated, otherwise taken directly from trackman). 
    
    - On some of the more notable features: Axis Difference is a proxy for non-Magnus movement, and measures the difference between the inferred spin axis, which was calculated as        
                self.radar_df['InferredSpinAxis'] = np.where(self.radar_df['pfxx'] < 0,
                                                    (np.arctan(self.radar_df['pfxz'] / self.radar_df['pfxx']) * 180 / math.pi + 90) + 180,
                                                    np.arctan (self.radar_df['pfxz'] / self.radar_df['pfxx']) * 180 / math.pi + 90),
  and the spin axis given by trackman. VAA represents vertical approach angle above average, which is vertical approach angle normalized for plate height. 
  
    Location Model: Similar to the stuff model, except with 2 extra submodels, take and swing. Assumes average stuff for each pitcher. The full set of features used are: \[PitchType, PitcherThrows, BatterSide, Balls, Strikes, PlateLocHeight, PlateLocSide\].
    
    Swing Mechanics: the batters were in the database, so I had to do something with them, right? Note: the swing models/databases haven't been updated for a few months now. Some notable outputs of the model are:
      
    - Collision Coefficient - taken from Professor Alan Nathan's research, collision coefficient represents how efficiently the bat was able to convert the speed of the ball coming in and the speed of the bat into exit velocity. It scales with distance from the sweet spot, meaning the collision is most efficient in the sweet spot of the bat (I know, hard to believe) and decreases as you travel towards the tips. Collision coefficient has a linear relationship with exit velocity, so I ran a regression to estimate the collision coefficient. This assumes that the bat speed is constant, so to mitigate the effects I regressed individually for each batter, assuming that their top evit velos were produced by striking the ball in the sweet spot. It still ended up a bit overfit with exit velo, but that probably won't be a problem, right?
    
    - (Effective) Bat Speed - also taken from Professor Alan Nathan's research. It turns out, CC being overfit with EV is a problem after all. Once you have the CC of each batted ball event you can calculate bat speed, but it ends up underestimating speeds for low EV players. 
    
    - True Bat Speed - by taking only "barrels" (https://www.mlb.com/glossary/statcast/barrel) into account, we can assume that the ball impacted the bat somewhere close to the sweet spot, sidestepping the issue of calculating CC completely. Really, "True Bat Speed" would also need the     attack angle to match the launch angle, but I don't think I'd have enough data to make a stable measurement for more than a handful of batters. Probably low hanging fruit for the future.
    
    - Attack Angle - the average vertical angle of the bat when it impacts the ball. EVs are maximized when attack angle equals centerline angle, and furthermore AA = LA when LA = CA. So, AA was calculated by fitting a parabola to the highest EVs bucketed into LAs of a player's BBEs.
    
    - "Smash Factor" - a confusingly named stat form Driveline which is just balls in play divided by fouls and whiffs weighted by collision coefficient. It's stickier than zone contact and K%, so it is their "bat to ball" skill marker.
    
    - Contact Quality - intrinsic run value of ball when contact is made
    
    - Swing Decision - calculated by fitting a model to predict swings based on the difference between the expected intrinsic value of a swing vs. the run value of a take. Final metric is based off how often they choose "correctly" compared to the league. It's a little funky right now, and I need to tinker with the model a little.
        
    **References**:

  * Hershberger, R. (2017). With a Deliberate Attempt to Deceive: Correcting a Quotation Misattributed to Charles Eliot, President of
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Harvard. Baseball Research Journal, Spring 2017.
    """)

# Your title and divider with reduced whitespace
st.title('PitchGrader')
# st.markdown('<hr style="height:2px;border:none;color:#333;background-color:#333;" /> ', unsafe_allow_html=True)
# st.divider ()
# st.markdown("""---""")
# st.caption ('Stuff, Location, and Swing Mechanics models for collegiate players')
# st.title('Stuff+ Model (also a swing mechanics model now)')
# col1, col2, col3 = st.columns([4, 2, 4])
# st.write('Database last updated 5/7/2024')
col1, col2, col3 = st.columns([12, 1, 1])
st.markdown("""
    <hr style='margin-top: 0.2em; margin-bottom: 1.2em; height: 0.1em; border: none; background-color: #31333F;'>
    """, unsafe_allow_html=True)
with col1:
    st.caption ('Stuff, Location, and Swing Mechanics models for collegiate players')
with col2:
    if st.button("?"):
        readme_dialog()
with col3:
    if st.button("⚙️"):
        settings_dialog()
col1, col3 = st.columns([15, 4])
with col1:
    # st.caption ('Stuff, Location, and Swing Mechanics models for collegiate players')
    st.write('Database last updated: 5/19/2024')
    st.write('Feel free to send any questions, suggestions or bug reports to gangmu.liu@email.virginia.edu')
with col3:
    # if st.button("⚙️"):
    #     settings_dialog()
    show_color = st.toggle("Colored Grades ", value = True, help='By default, grades on the 20-80 scale are colored (coloring is disabled for large dataframes)')
    show_location = st.toggle("Location Grades", value = False, help='By default, location grades for individual pitches are not displayed')
# col1, col3 = st.columns([12, 5])
# with col1:
#     st.write('Please send any questions or bug reports to gangmu.liu@email.virginia.edu')
# with col3:
#     show_location = st.toggle("Location Grades", value = False, help='By default, location grades for individual pitches are not displayed')
# Create two text input boxes for the first and last name
if 'team_flag' not in st.session_state:
    st.session_state.team_flag = False

# if 'min_pitch' not in st.session_state:
#     st.session_state['min_pitch'] = ''

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
# col1, col4, col2, col3 = st.columns([12.5, 3, 4.5, 8])
st.markdown("""
    <style>
        /* Further reduce padding and margins around specific widgets */
        .stButton {
            margin-bottom: -10px !important;
        }
    </style>
""", unsafe_allow_html=True)
col3,_, col2, col1 = st.columns([9, 11, 4.5, 5])
with col1:
    random_team = st.button ('Random team', key = 'random_team')
    #options = ['Combined', 2024, 2023]
    # year_selected = st.selectbox ('', options = [2024, 2023], index = 1, key = 'year')
    # team_toggle = st.button("Toggle team/player", key='team_toggle', type = 'primary')
    # if (st.session_state ['team_flag']):
    #     team_toggle = st.button("Team View (switch to player)", key='team_toggle', type = 'primary')
    # else:
    #     team_toggle = st.button("Player Profile (switch to team)", key='team_toggle', type = 'primary')
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
    # button_label = "Random team" + "&nbsp;" * 2# + "　" * 1
#     team_toggle = st.button("Toggle team/player")
#     if (team_toggle):
#         st.session_state.team_flag = not st.session_state.team_flag
        # st.write (team_flag)
# team_toggle = st.button("Toggle team/player", key='team_toggle', type = 'primary')
with col3:
    show_changes_placeholder = st.empty()
col1, col3 = st.columns([4.525, 12])
with col1:
    year_selected = st.selectbox ('', options = [2024, 2023], index = 0, key = 'year')#, on_change = changed_year)
# st.markdown("""
# <hr style='margin-top: 0.2em; margin-bottom: 1.2em; height: 0.12em; border: none; background-color: #31333F;'>
# """, unsafe_allow_html=True)
container_a = st.container ()
# tab1, tab2 = st.tabs(["Player", "Team"])
# year_selected = st.selectbox ("Year", options = ['Combined', 2024, 2023], index = 1, key = 'year')
tab1, tab2 = st.tabs(["Player", "Team"])
year = year_selected
if (year_selected == 'Combined'):
    year = ''
    st.session_state["disabled"] = True
elif (year_selected == 2023):
    st.session_state["disabled"] = True
else:
    st.session_state['disabled'] = False
driver = database_driver.DatabaseDriver(year=year)
if (year_selected != 'Combined'):
    driver2 = database_driver.DatabaseDriver(year=(year-1))
else:
    driver2 = database_driver.DatabaseDriver(year=2023)
show_changes = show_changes_placeholder.button (f"Compare pitches to previous year", key = 'show_changes', disabled=st.session_state["disabled"], type = 'primary')
# driver = database_driver.DatabaseDriver(year=year)
# if (show_changes):
#     driver2 = database_driver.DatabaseDriver(year=(year-1))
stuff_driver = stuff_plus.Driver('radar2.db', 'radar_data')
# if (team_toggle):
#     st.session_state.team_flag = not st.session_state.team_flag
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
if random_team:
    random_option = random.choice(options_teams)
    st.session_state['team_name'] = random_option

def color_values (value):
    if not show_color or show_changes or pd.isna(value):
        # return f'background-color: #ffffff'
        return st.get_option('theme.backgroundColor')
    # Create a color map with specific hex values
    cmap = mcolors.LinearSegmentedColormap.from_list("colormap", ["#ff0000", "#ffff00", "#00ff00"])
    norm = mcolors.Normalize(vmin=15, vmax=85)
    # norm = mcolors.TwoSlopeNorm(vmin=20, vcenter=50, vmax=90)
    # Return color style
    rgba = cmap(norm(value))
    color = mcolors.rgb2hex(rgba)
    # if show_color:
    return f'background-color: {color}; color: black;'
    # return f'background-color: #ffffff'

# batting_percentages_df = driver.retrieve_percentages_bat_team ('All')
# pitching_percentages_df = driver.retrieve_percentages_team ('All')
# pitching_stuff_df = driver.retrieve_stuff_team ('All')
# st.success (st.session_state['selected_player_index'] )
# Conditional rendering based on the toggle state
# if not st.session_state.team_flag:
with tab1:
    # container_a.header ("Player Profile")
    # first_name = st.text_input('First Name', '', placeholder='First name', key='first_name')
    # last_name = st.text_input('Last Name', '', placeholder='Last name', key='last_name')
    # team_name = st.text_input('Team Name', '', placeholder='Team name', key='team_name')
    # st.success (st.session_state['player_name'] + ", " + st.session_state.player_name_update)
    def pick_random ():
        random_option = random.choice(options)
        st.session_state['player_name'] = random_option
    # if (st.session_state['player_name'] == ''):
    #     pick_random ()
    default_index = options.index(st.session_state['player_name']) if st.session_state['player_name'] in options else 0
    selected_name = st.selectbox('Name', options=options, index = default_index, key='player_name')#, on_change=first_click)# index=default_index, key='player_name')
    st.session_state.player_name_update = selected_name
    team_name = ''
    # When both names have been entered, display the full name
    display_name = st.empty()
    # if first_name and last_name:
    if selected_name == '':
        st.success ('Look up a player to get started!')
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
        if (df.empty) or (st.session_state.player_name_update.split(', ')[1] == 'Batter'):
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
            def populate_player_profile (driver, side = ''):
                driver.set_side (side)
                df = driver.retrieve_percentiles (name, team_name)
                if (show_changes):
                    driver.set_side (side)
                    if (show_location):
                        location_df = driver.retrieve_location (name)
                        stuff_df = driver.retrieve_stuff (name)
                        stuff_df['Type'] = 'Stuff'
                        location_df['Type'] = 'Command'
                        stuff_df1 = pd.concat([stuff_df, location_df], ignore_index=True)
                        stuff_df1 = stuff_df1.round(0)
                        # st.dataframe (stuff_df1)
                        location_df = driver2.retrieve_location (name)
                        stuff_df = driver2.retrieve_stuff (name)
                        stuff_df['Type'] = 'Stuff'
                        location_df['Type'] = 'Command'
                        stuff_df2 = pd.concat([stuff_df, location_df], ignore_index=True)
                        stuff_df2 = stuff_df2.round(0)
                        # st.dataframe (stuff_df2)
                        merged_df = stuff_df1.merge(stuff_df2, on='Type', how='left', suffixes=('_df2', '_df1'))
                        # st.dataframe (merged_df)
                    else:
                        location_df = driver.retrieve_location (name)
                        location_df = location_df [['Pitcher', 'Overall']]
                        # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                        location_df = location_df.rename(columns={'Overall': 'Command'})
                        # st.dataframe (location_df)
                        stuff_df1 = driver.retrieve_stuff (name)
                        stuff_df1 = stuff_df1.merge (location_df, on = 'Pitcher')
                        stuff_df1 = stuff_df1.round(0)
                        location_df = driver2.retrieve_location (name)
                        location_df = location_df [['Pitcher', 'Overall']]
                        # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
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
                        keyword = 'Type' if show_location else 'Pitcher'
                        if col != keyword and col in stuff_df1.columns:  # Check if column is also in df1
                            merged_df[col] = merged_df.apply(lambda row: calculate_and_format(row, col), axis=1)
                    # st.dataframe (merged_df)
                    # stuff_df.update(merged_df[stuff_df2.columns])
                    columns_to_drop = [col for col in merged_df.columns if col.endswith('_df1') or col.endswith('_df2')]
                    # st.empty ()
                    # Drop these columns
                    stuff_df = merged_df.drop(columns=columns_to_drop)
                    # st.dataframe (stuff_df)
                    st.empty ()
                    # st.table (stuff_df)
                    # st.dataframe (stuff_df)
                    # stuff_df3 = merged_df.drop(columns=columns_to_drop)
                    # st.table (stuff_df)
                    # st.dataframe (stuff_df)
                else:
                    if (show_location):
                        location_df = driver.retrieve_location (name)
                        # location_df = location_df [['Pitcher', 'Overall']]
                        # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                        # st.dataframe (location_df)
                        stuff_df = driver.retrieve_stuff (name)
                        stuff_df['Type'] = 'Stuff'
                        location_df['Type'] = 'Command'
                        stuff_df = pd.concat([stuff_df, location_df], ignore_index=True)
                        stuff_df = stuff_df.round(0)
                    else:
                        location_df = driver.retrieve_location (name)
                        location_df = location_df [['Pitcher', 'Overall']]
                        # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                        location_df = location_df.rename(columns={'Overall': 'Command'})
                        # st.dataframe (location_df)
                        stuff_df = driver.retrieve_stuff (name)
                        stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
                        stuff_df = stuff_df.round(0)
                        st.empty ()
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
                if (show_location):
                    desired_order = ['Type', 'PitchCount', 'Overall', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                stuff_df = stuff_df.rename(columns=rename_columns)
                st.empty ()

                # stuff_df = pitching_stuff_df [pitching_stuff_df ['Pitcher'] == name]
                if (show_location):
                    stuff_df = stuff_df.drop_duplicates (['Pitcher', 'Type'])
                else:
                    stuff_df = stuff_df.drop_duplicates ('Pitcher')
                stuff_df = stuff_df.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows'])
                # stuff_df = stuff_df.drop_duplicates ('Pitcher')
                if not show_location:
                    stuff_df.rename(columns={'Overall': 'Overall Stuff'}, inplace=True)
                    st.empty ()
                columns_to_drop = [column for column in stuff_df.columns if column.endswith('Usage')]
                stuff_df = stuff_df.drop(columns=columns_to_drop)
                stuff_df = stuff_df.dropna(axis=1)
                # st.success (desired_order)
                # st.success (stuff_df.columns)
                actual_order = [col for col in desired_order if col in stuff_df.columns]
                # st.success (actual_order)
                stuff_df = stuff_df[actual_order]
                st.empty ()
                # st.success (stuff_df.columns)
                if (show_location):
                    stuff_df = stuff_df.set_index('Type')
                    stuff_df.index.name = 'Type'
                    stuff_df.at['Command', 'PitchCount'] = None
                else:
                    stuff_df = stuff_df.set_index('PitchCount')
                    stuff_df.index.name = 'Pitch Count'
                st.empty ()
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
                colored_columns = [col for col in actual_order if col != 'PitchCount' and col != 'Type']
                if not show_changes:
                    stuff_df = stuff_df.style.applymap(color_values, subset=colored_columns).format("{:,.0f}")
                    st.empty ()
                container = st.container()
                container.markdown("<div margin-left: auto, margin-right: auto>", unsafe_allow_html=True)
                container.dataframe(stuff_df)
                container.markdown("</div>", unsafe_allow_html=True)
                desired_order = ['PitchCount', 'Command', 'Overall Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                log_df = driver.retrieve_game_logs(name, force_both = True)
                def classify_pitcher(df, year = year_selected):
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df[df['Date'].dt.year == year]
                    total_entries = len(df)
                    high_pitch_count = (df['PitchCount'] >= 50).sum() / total_entries
                    low_pitch_count = (df['PitchCount'] <= 40).sum() / total_entries
                    # st.dataframe (df)
                    # st.success (high_pitch_count )
                    # st.error (low_pitch_count)
                    # st.error (len (df))
                    if high_pitch_count >= 0.5:
                        return "Start"
                    elif low_pitch_count >= 0.75:
                        return "Short"
                    else:
                        return "Long"
                #year manual hack
                pitcher_type2023 = classify_pitcher(log_df.copy (), 2023)
                pitcher_type2024 = classify_pitcher(log_df.copy (), 2024)
                dict = {
                    'Start': 'Starter',
                    'Short': 'Short Reliever',
                    'Long': 'Long Reliever'
                }
                pitcher_type = dict[pitcher_type2023 if year_selected == 2023 else pitcher_type2024]
                # display_name.success (f"Pitcher: {first_name} {last_name}, {df ['PitcherTeam'].iloc [0]}. Throws: {df ['PitcherThrows'].iloc [0]}")
                if (side == ''):
                    display_name.success (f"Pitcher ({pitcher_type}): {name}. {df ['PitcherTeam'].iloc [0]}. Throws: {df ['PitcherThrows'].iloc [0]}")
                df = df.drop(columns=['ExitSpeed', 'PitcherId', 'overall_avg_xRV', 'PitchxRV'])
                df = df.drop_duplicates ('PitchType')
                df = df.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
                cols = [col for col in df.columns if col != 'xRV']
                cols.insert(2, 'xRV')
                df = df[cols]
                st.empty ()
                if (show_changes):
                    df2 = driver2.retrieve_percentiles (name, team_name)
                    # df2 = df2.drop(columns=['ExitSpeed', 'PitcherId'])
                    df2 = df2.drop_duplicates ('PitchType')
                    df2 = df2.drop (columns = ['Pitcher', 'PitcherTeam', 'PitcherThrows', 'Balls', 'Strikes'])
                    df2 = df2.drop(columns=['ExitSpeed', 'PitcherId', 'overall_avg_xRV', 'PitchxRV'])
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
                st.empty ()
                # df = stuff_df.set_index('PitchType')
                df_display = df
                df_display = df_display.set_index('PitchType')
                df_display.index.name = "Pitch Type"
                st.empty ()
                st.write ("Percentiles")
                st.dataframe(df_display)
                st.write ("Attributes")
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
                prob_df = prob_df.drop (columns = ['overall_avg_xRV', 'PitchxRV', 'EV', 'average_xRV'])
                prob_df ['xGB%'] = prob_df ['Prob_SoftGB'] + prob_df ['Prob_HardGB']
                prob_df ['xHH%'] = prob_df ['Prob_HardGB'] + prob_df ['Prob_HardLD'] + prob_df ['Prob_HardFB']
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
                    prob_df2 = prob_df2.drop (columns = ['overall_avg_xRV', 'PitchxRV', 'EV', 'average_xRV'])
                    prob_df2 ['xGB%'] = prob_df2 ['Prob_SoftGB'] + prob_df2 ['Prob_HardGB']
                    prob_df2 ['xHH%'] = prob_df2 ['Prob_HardGB'] + prob_df2 ['Prob_HardLD'] + prob_df2 ['Prob_HardFB']
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
                # input_df = st.data_editor(prob_df)
                st.dataframe(prob_df)
                pitch_types = df['PitchType'].unique().tolist()
                if (not show_changes):
                    index = st.selectbox("Pitch Type", range(len(pitch_types)), format_func=lambda x: pitch_types[x], index=0, key = f'type{side}')
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
                st.write ("History")
                stuff_history_df = driver.retrieve_stuff_history(name)
                location_history_df = driver.retrieve_location_history(name)
                location_history_df = location_history_df [['Pitcher', 'Overall', 'Year']]
                location_history_df = location_history_df.rename(columns={'Overall': 'Command'})
                location_history_df = location_history_df.drop_duplicates (['Pitcher', 'Year'])
                st.empty ()
                stuff_history_df = stuff_history_df.drop_duplicates (['Pitcher', 'Year'])
                stuff_history_df = stuff_history_df.merge (location_history_df, on = 'Year')
                stuff_history_df = stuff_history_df.rename(columns=rename_columns)
                st.empty ()
                stuff_history_df ['Year'] = stuff_history_df ['Year'].astype(str)
                stuff_history_df = stuff_history_df.set_index('Year')
                st.empty ()
                stuff_history_df.index.name = 'Year'
                stuff_history_df.rename(columns={'Overall': 'Overall Stuff', 'PitcherTeam' : 'Team'}, inplace=True)
                st.empty ()
                stuff_history_df [desired_order] = stuff_history_df [desired_order].round(0)
                desired_order = ['Team', 'PitchCount', 'Command', 'Overall Stuff', 'FF', 'FF%', 'SI', 'SI%', 'FC', 'FC%', 'SL', 'SL%', 'CU', 'CU%', 'FS', 'FS%', 'CH', 'CH%']
                stuff_history_df = stuff_history_df[desired_order]
                st.empty ()
                # columns_to_drop = [column for column in stuff_history_df.columns if column.endswith('Usage')]
                # stuff_history_df = stuff_history_df.drop(columns=columns_to_drop)
                stuff_history_df = stuff_history_df.dropna(axis=1, how = 'all')
                # stuff_history_df.update(stuff_history_df.filter(like='%').apply(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x))
                stuff_history_df.loc[:, stuff_history_df.columns.str.contains('%')] = stuff_history_df.filter(like='%').applymap(lambda x: '{:.2f}'.format(x) if pd.notnull(x) else x)
                st.empty ()
                colored_columns = ['Command', 'Overall Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                usage = ['FF%', 'SI%', 'FC%', 'SL%', 'CU%', 'FS%', 'CH%']
                colored_columns = [col for col in colored_columns if col in stuff_history_df.columns]
                usage = [col for col in usage if col in stuff_history_df.columns]
                # st.success (colored_columns)
                # st.success (usage)
                pitcher_types = {
                    '2023': pitcher_type2023,
                    '2024': pitcher_type2024
                }
                stuff_history_df['Role'] = stuff_history_df.index.map(pitcher_types)
                new_columns = [stuff_history_df.columns[0]] + ['Role'] + [col for col in stuff_history_df.columns if col != 'Role' and col != stuff_history_df.columns[0]]
                stuff_history_df = stuff_history_df[new_columns]
                st.empty ()
                stuff_history_df = stuff_history_df.style.applymap(color_values, subset = colored_columns).format("{:,.0f}", subset = colored_columns + ['PitchCount'])
                st.empty ()
                st.dataframe (stuff_history_df)
                with st.expander(f"Game Log"):
                    log_df = driver.retrieve_game_logs(name)
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
                    log_df = log_df.rename(columns=rename_columns)
                    log_df = log_df.round({col: 0 for col in log_df.columns if not col.endswith('%')})
                    log_df = log_df.drop (columns = ['PitcherTeam', 'PitcherThrows', 'Pitcher'])
                    log_df = log_df.iloc[::-1].reset_index(drop=True)
                    log_df = log_df.set_index ('Date')
                    log_df = log_df.rename(columns={'Overall': 'Stuff'})
                    log_df = log_df.rename(columns={'BatterTeam': 'Opposing Team'})
                    st.empty ()
                    desired_order = ['Opposing Team', 'PitchCount', 'Command', 'Stuff', 'FF', 'FF%', 'SI', 'SI%', 'FC', 'FC%', 'SL', 'SL%', 'CU', 'CU%', 'FS', 'FS%', 'CH', 'CH%']
                    actual_order = [col for col in desired_order if col in log_df.columns]
                    log_df = log_df [actual_order]
                    if st.session_state.truncate_game_log:
                        log_df['Year'] = pd.to_datetime(log_df.index)
                        log_df = log_df[log_df['Year'].dt.year == year_selected]
                        log_df = log_df.drop (columns = ['Year'])
                    st.empty ()
                    colored_columns = ['Command', 'Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                    # usage = {col for col in log_df.columns if col.endswith('%')}
                    usage = ['FF%', 'SI%', 'FC%', 'SL%', 'CU%', 'FS%', 'CH%']
                    log_df = log_df.style.applymap(color_values, subset = colored_columns).format ("{:.2f}", subset = usage).format("{:,.0f}", subset = colored_columns)
                    st.dataframe (log_df)
                # actual_order = [col for col in desired_order if col in stuff_history_df.columns]
                # stuff_history_df = stuff_history_df[actual_order]
                # st.dataframe (stuff_history_df)
                # update = st.button("Update Percentiles", key='update_percentiles', type = 'secondary')
                # st.write ("Game Log")

            tab_B, tab_L, tab_R = st.tabs(["Overall", "vs. Left", "vs. Right"])
            with tab_B:
                populate_player_profile(driver)
            with tab_L:
                populate_player_profile(driver, 'Left')
            with tab_R:
                populate_player_profile(driver, 'Right')
            st.empty ()
            #TODO: this
            if (not show_changes):
                driver.remove_side ()
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
                prob_df = prob_df.drop (columns = ['overall_avg_xRV', 'PitchxRV', 'EV', 'average_xRV'])
                prob_df ['xGB%'] = prob_df ['Prob_SoftGB'] + prob_df ['Prob_HardGB']
                prob_df ['xHH%'] = prob_df ['Prob_HardGB'] + prob_df ['Prob_HardLD'] + prob_df ['Prob_HardFB']
                prob_df = prob_df.sort_values(by='Usage', ascending = False)
                prob_df = prob_df.set_index('PitchType')
                prob_df.index.name = "Pitch Type"
                # st.success ("test")
                location_df = driver.retrieve_location_team ('All')
                location_df = location_df [['Pitcher', 'Overall']]
                # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                #legacy: manual specified year
                driver1 = database_driver.DatabaseDriver(year=2024)
                driver12 = database_driver.DatabaseDriver(year=(2023))
                stuff_df = driver1.retrieve_stuff_team ('All')
                stuff_df = stuff_df.rename(columns={'Overall': 'Stuff'})
                stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
                # stuff_df = stuff_df.round(0)
                prob_MC_df = driver12.retrieve_percentages_team ('All')
                prob_MC_df = prob_MC_df [prob_MC_df ['Pitcher'] != name]
                stuff_df = stuff_df.drop_duplicates(subset=['Pitcher'])
                stuff_df = stuff_df.set_index('Pitcher')
                stuff_df = stuff_df [stuff_df['PitchCount'] >= 80]

                stuff_df2 = driver12.retrieve_stuff_team ('All')
                stuff_df2 = stuff_df2.rename(columns={'Overall': 'Stuff'})
                stuff_df2 = stuff_df2.merge (location_df, on = 'Pitcher')
                stuff_df2 = stuff_df2.drop_duplicates(subset=['Pitcher'])
                stuff_df2 = stuff_df2.set_index('Pitcher')
                stuff_df2 = stuff_df2 [stuff_df2['PitchCount'] >= 80]

                def get_stuff(row):
                    pitch_type = row['PitchType']
                    pitcher = row['Pitcher']
                    if pitcher in stuff_df.index:
                        return stuff_df.at[pitcher, pitch_type]
                    return None
                # Apply function to prob_MC_df
                prob_MC_df['Stuff_new'] = prob_MC_df.apply(get_stuff, axis=1)
                stuff_df = stuff_df2
                prob_MC_df['Stuff_old'] = prob_MC_df.apply(get_stuff, axis=1)
                prob_MC_df = prob_MC_df.dropna(subset=['Stuff_new', 'Stuff_old'])
                prob_MC_df ['Stuff_diff'] = prob_MC_df['Stuff_new'] - prob_MC_df['Stuff_old']
                # st.empty ()
                # prob_MC_df = prob_MC_df [prob_MC_df['PitchCount'] >= 80]
                # st.dataframe (prob_MC_df)
                # st.dataframe (prob_df)
                def calculate_mahalanobis(df_single, df_multi, columns):
                    scaler = StandardScaler()
                    scaled_multi_values = scaler.fit_transform(df_multi[columns].values)
                    scaled_single_value = scaler.transform(df_single[columns].values[0].reshape(1, -1))
                    cov_matrix = np.cov(scaled_multi_values, rowvar=False)
                    cov_matrix_inv = inv(cov_matrix)
                    df_multi['Mahalanobis'] = [mahalanobis(row, scaled_single_value[0], cov_matrix_inv) for row in scaled_multi_values]
                    return df_multi

                def compute_weights(df, epsilon=0.01):
                    # inverse_distances = 1 / (df['Mahalanobis'] + epsilon)
                    weights = np.exp(-1* df['Mahalanobis'])
                    normalized_weights = weights / weights.sum()
                    return normalized_weights

                def sample_performance(df, num_samples=1000):
                    weights = compute_weights(df)
                    sampled_indices = np.random.choice(df.index, size=num_samples, p=weights)
                    return sampled_indices

                def monte_carlo_simulation(df, sampled_indices, performance_metrics):
                    simulation_results = {metric: [] for metric in performance_metrics}
                    for metric in performance_metrics:
                        sampled_data = df.loc[sampled_indices, metric]
                        simulation_results[metric] = {
                            'mean': np.mean(sampled_data),
                            'std': np.std(sampled_data),
                            '5th_percentile': np.percentile(sampled_data, 5),
                            '75th_percentile': np.percentile(sampled_data, 75),  # Add percentile value
                            '95th_percentile': np.percentile(sampled_data, 95),
                            'pos': (sampled_data > 0).mean()
                        }
                    return simulation_results
                def find_comps(df):
                    df_sorted = df.sort_values('Mahalanobis')
                    most_similar = df_sorted.head(3)
                    least_similar = df_sorted.tail(3)
                    mean_squared_distance = np.mean(df_sorted['Mahalanobis']**2)
                    return most_similar, least_similar, mean_squared_distance

                performance_metrics = ['Stuff_diff']
                simulation_results_per_row = []
                simulation_results_per_row_std = []
                simulation_results_per_row_pos = []
                prob_df2 = prob_df [prob_df ['Usage'] > 0.01]
                running_average = 0
                count = 0
                with st.expander(f"Upside Details"):
                    for index, row in prob_df2.iterrows():
                        modified_prob_MC_df = calculate_mahalanobis(row.to_frame().T, prob_MC_df, ['RelSpeed', 'InducedVertBreak', 'HorzBreak', 'VAA', 'SpinRate', 'SpinEfficiency', 'AxisDifference', 'RelHeight', "RelSide", 'Extension', 'VertRelAngle', 'HorzRelAngle'])
                        sampled_indices = sample_performance(modified_prob_MC_df, 1000000)
                        simulation_results = monte_carlo_simulation(modified_prob_MC_df, sampled_indices, performance_metrics)
                        simulation_results_per_row.append(simulation_results['Stuff_diff']['75th_percentile'])
                        simulation_results_per_row_std.append(simulation_results['Stuff_diff']['std'])
                        simulation_results_per_row_pos.append(simulation_results['Stuff_diff']['pos'])
                        most_similar, least_similar, mean_squared_distance = find_comps(modified_prob_MC_df)
                        count += 1
                        running_average = (running_average * (count - 1) + mean_squared_distance) / count
                        st.success (simulation_results)

                    prob_df2['Raw'] = simulation_results_per_row
                    prob_df2['Vol'] = simulation_results_per_row_std
                    prob_df2['Outlook'] = simulation_results_per_row_pos
                    # prob_df2 = prob_df2 [['Usage', 'xRV', 'Raw', 'Vol', 'Outlook']]
                    # st.dataframe(prob_df2)
                    # prob_df2.reset_index(inplace=True)
                    bins = [0, 6, 6.5, 7.5, 15]
                    labels = ['-', ' ', '+', '++']
                    prob_df2['Upside'] = pd.cut(prob_df2['Raw'], bins=bins, labels=labels, right=False)
                    prob_df2 = prob_df2 [['Usage', 'xRV', 'Raw', 'Vol', 'Outlook', 'Upside']]
                    prob_df2 = round (prob_df2, 2)
                    st.dataframe(prob_df2)
                    pivot_df = prob_df2 [['Upside', 'Raw']]
                    pivot_df = pivot_df.round (2)
                    pivot_df = pivot_df.T
                    rename_columns = {
                        'ChangeUp': 'CH',
                        'Curveball': 'CU',
                        'Cutter' : 'FC',
                        'Four-Seam' : 'FF',
                        'Sinker' : 'SI',
                        'Slider' : 'SL',
                        'Splitter' : 'FS'
                    }
                    pivot_df = pivot_df.rename(columns=rename_columns)
                    # st.dataframe (pivot_df)
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
            if not show_changes:
                with st.expander(f"Player Comps"):
                    st.success (f"Unicorn Score: {round (running_average, 2)}")
    # df = pd.read_csv("my_data.csv")
    # st.line_chart(df)
# else:
with tab2:
    #Here: Team
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
    st.empty ()
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
            # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
            location_df = location_df.rename(columns={'Overall': 'Command'})
            stuff_df = driver.retrieve_stuff_team (team_name)
            stuff_df = stuff_df.rename(columns={'Overall': 'Stuff'})
            stuff_df = stuff_df.merge (location_df, on = 'Pitcher')
            stuff_df['Fastball%'] = stuff_df['Four-Seam Usage'].fillna(0) + stuff_df['Sinker Usage'].fillna(0)
            # stuff_df = stuff_df.apply(lambda x: round(x, 0) if x.name != 'Fastball%' else x)
            # stuff_df['Fastball%'] = stuff_df['Fastball%'].round(2)
            weighted_sum1 = np.sum(stuff_df['PitchCount'] * stuff_df['Stuff'])
            weighted_sum2 = np.sum(stuff_df['PitchCount'] * stuff_df['Command'])
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
                    min_pitch2 = int(min_pitch)
                    stuff_df = stuff_df [stuff_df ['PitchCount'] >= min_pitch2]
                except ValueError:
                    st.error("Invalid number for the minimum pitch count.")
            if (show_changes):
                location_df = driver2.retrieve_location_team (team_name)
                location_df = location_df [['Pitcher', 'Overall']]
                # location_df['Overall'] = location_df['Overall'].clip(lower=20, upper=80)
                location_df = location_df.rename(columns={'Overall': 'Command'})
                # st.dataframe (location_df)
                stuff_df1 = driver2.retrieve_stuff_team (team_name)
                stuff_df1 = stuff_df1.rename(columns={'Overall': 'Stuff'})
                stuff_df1 = stuff_df1.merge (location_df, on = 'Pitcher')
                stuff_df1['Fastball%'] = stuff_df1['Four-Seam Usage'].fillna(0) + stuff_df1['Sinker Usage'].fillna(0)
                stuff_df1 = stuff_df1.apply(lambda x: round(x, 0) if x.name != 'Fastball%' else x)
                stuff_df1['Fastball%'] = stuff_df1['Fastball%'].round(2)
                # stuff_df1 = stuff_df1.round(0)
                # if min_pitch:  # Check if something was entered
                #     try:
                #         min_pitch = int(min_pitch)
                #         stuff_df1 = stuff_df1 [stuff_df1 ['PitchCount'] >= min_pitch]
                #     except ValueError:
                #         print ('hi')
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
                            if (col == 'Fastball%'):
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
                            if (col == 'Fastball%'):
                                return f"{round (original, 2)} ({sign}{round (difference, 2)})"
                            else:
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
            # st.dataframe (stuff_df)
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
            stuff_df = stuff_df.set_index ('Pitcher')
            stuff_df_old = stuff_df
            if (team_name == 'All' and not show_changes):
                if (st.session_state.calculate_team_list == True):
                    with st.expander(f"Team List"):
                        # colored_columns = ['Command', 'Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                        # if not show_changes:
                        #     weighted_averages = weighted_averages.style.applymap(color_values, subset = colored_columns).format("{:,.0f}")
                        # st.dataframe (weighted_averages)
                        container_wa = st.container()
            colored_columns = ['Command', 'Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
            colored_columns = [col for col in colored_columns if col in stuff_df.columns and stuff_df[col].notna().any()]
            if not show_changes and show_color and stuff_df.shape[0] < 1000:
                stuff_df = stuff_df.style.applymap(color_values, subset = colored_columns)#
                stuff_df = stuff_df.format("{:,.0f}", subset = colored_columns + ['PitchCount'])#.format("{:.2f}", subset=['Fastball%'])
                stuff_df = stuff_df.format("{:.2f}", subset = ['Fastball%'])
            else:
                stuff_df = stuff_df.apply(lambda x: round(x, 0) if x.name != 'Fastball%' else x)
                stuff_df['Fastball%'] = stuff_df['Fastball%'].round(2)
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
                    valid_pitchers = stuff_df.index
                    df = df[df['Pitcher'].isin(valid_pitchers)]
                except ValueError:
                    print ('hey')
            cols = [col for col in df.columns if col != 'xRV']
            cols.insert(5, 'xRV')
            df = df[cols]
            prob_df_final = driver.retrieve_percentages_team (team_name)
            if (team_name == 'All'):
                prob_df_final = prob_df_final.drop (columns = ['Balls', 'Strikes'])
            else:
                prob_df_final = prob_df_final.drop (columns = ['PitcherTeam', 'Balls', 'Strikes'])
            if min_pitch:  # Check if something was entered
                try:
                    valid_pitchers = stuff_df.index
                    prob_df_final = prob_df_final[prob_df_final['Pitcher'].isin(valid_pitchers)]
                except ValueError:
                    print ('hey')
            cols = [col for col in prob_df_final.columns if col != 'xRV']
            cols.insert(5, 'xRV')
            prob_df_final = prob_df_final[cols]
            prob_df_final = round (prob_df_final, 4)
            prob_df_final = prob_df_final.drop (['PitcherId'], axis = 1)
            # df = df.sort_values(by='Usage', ascending = False)
            options = ['All', 'Fastball', 'Breaking Ball', 'Offspeed'] + list(prob_df_final['PitchType'].unique())
            pitch_selected = st.selectbox ("Pitch Type", options = options, key = 'pitch_selected')
            pitch_categories = {
                'Fastball': ['Four-Seam', 'Sinker'],
                'Breaking Ball': ['Cutter', 'Slider', 'Curveball'],
                'Offspeed': ['ChangeUp', 'Splitter']
            }
            if pitch_selected in pitch_categories:
                prob_df_final = prob_df_final[prob_df_final['PitchType'].isin(pitch_categories[pitch_selected])]
                df = df[df['PitchType'].isin(pitch_categories[pitch_selected])]
            elif pitch_selected != 'All':
                prob_df_final = prob_df_final[prob_df_final['PitchType'] == pitch_selected]
                df = df[df['PitchType'] == pitch_selected]
            df = df.drop (columns = ['overall_avg_xRV', 'PitchxRV', 'ExitSpeed', 'PitcherId'])
            prob_df_final = prob_df_final.drop (columns = ['overall_avg_xRV', 'PitchxRV', 'EV', 'average_xRV', 'ExitSpeed'])
            # prob_df_final ['xGB%'] = prob_df_final ['Prob_SoftGB'] + prob_df_final ['Prob_HardGB']
            # prob_df_final ['xHH%'] = prob_df_final ['Prob_HardGB'] + prob_df_final ['Prob_HardLD'] + prob_df_final ['Prob_HardFB']
            df = df.set_index(['Pitcher', 'PitchType'])
            prob_df_final = prob_df_final.set_index (['Pitcher', 'PitchType'])
            df_bat = df_bat.set_index ('Batter')
            st.write ("Percentiles")
            st.dataframe (df)
            st.write ("Attributes")
            st.dataframe (prob_df_final)
            st.write ("Swing Mechanics")
            st.dataframe (df_bat)
            if (team_name == 'All' and not show_changes and st.session_state.calculate_team_list == True):
                stuff_df = stuff_df_old
                # st.dataframe (stuff_df)
                grouped = stuff_df.groupby('PitcherTeam')
                desired_columns = ['Command', 'Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                weighted_sums = grouped.apply(lambda x: pd.Series(
                    {f'Weighted_{col}': np.sum(x['PitchCount'][x[col].notna()] * x[col].dropna()) for col in desired_columns} |
                    {f'Total_{col}_PitchCount': np.sum(x['PitchCount'][x[col].notna()]) for col in desired_columns} |
                    {'Total_PitchCount': np.sum(x['PitchCount'])}
                ))

                # Calculate the weighted averages
                weighted_averages = pd.DataFrame({
                    'PitcherTeam': weighted_sums.index,
                    'PitchCount': weighted_sums['Total_PitchCount'],
                    **{col: (weighted_sums[f'Weighted_{col}'] / weighted_sums[f'Total_{col}_PitchCount']) for col in desired_columns}
                })
                # container_wa.dataframe(weighted_averages)
                weighted_averages.set_index('PitcherTeam', inplace=True)
                max_pitch_count = weighted_averages['PitchCount'].max()
                eligible_teams = weighted_averages[weighted_averages['PitchCount'] >= max_pitch_count/2]
                eligible_teams['Stuff Rank'] = eligible_teams['Stuff'].rank(ascending=False, method='min')
                eligible_teams['Command Rank'] = eligible_teams['Command'].rank(ascending=False, method='min')
                weighted_averages = weighted_averages.join(eligible_teams[['Stuff Rank', 'Command Rank']], how='left')
                order = ['PitchCount', 'Command', 'Command Rank', 'Stuff', 'Stuff Rank', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                weighted_averages = weighted_averages [order]
                colored_columns = ['Command', 'Stuff', 'FF', 'SI', 'FC', 'SL', 'CU', 'FS', 'CH']
                # container_wa.dataframe(weighted_averages)
                if (st.session_state.show_unranked == False):
                    weighted_averages = weighted_averages.dropna (subset = ['Stuff Rank'])
                if not show_changes:
                    weighted_averages = weighted_averages.style.applymap(color_values, subset=colored_columns).format("{:,.0f}")
                container_wa.dataframe(weighted_averages)
            # pitch_types = df['PitchType'].unique().tolist()
            # index = st.selectbox("Pitch Type", range(len(pitch_types)), format_func=lambda x: pitch_types[x])
            # temp = df['PitchType'].iloc [index]
            # stuff_df = stuff_df.dropna(axis=1)




