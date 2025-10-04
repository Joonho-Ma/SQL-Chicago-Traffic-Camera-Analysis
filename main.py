#
# FA25 CS341
# Name: Joonho Ma
# Console-based Python program to analyze data of the Chicago traffic camera database
#   First starts with general statistics on the database.
#   Them. provides user with several choices, each providing different methods of analyzing the database
#

import sqlite3
import matplotlib.pyplot as plt

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    # Num of red cameras
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    # General statistics added referring to expected output
    # Num of speed cameras
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")

    # Num of red light violations
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")
    
    # Num of speed violations
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")

    # Range of Dates
    range_of_dates_sql = """
        SELECT MIN(Violation_Date) as min_date, MAX(Violation_Date) as max_date
        FROM (SELECT Violation_Date FROM RedViolations UNION ALL SELECT Violation_Date FROM SpeedViolations) as tot_range
        """
    dbCursor.execute(range_of_dates_sql)
    minDate, maxDate= dbCursor.fetchone()
    print("  Range of Dates in the Database:", f"{minDate} - {maxDate}")

    # Total number of red light violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")

    # Total number of red light violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")


#
# Command 1: Find an intersection by name
#
def command_1(dbConn): 
    dbCursor = dbConn.cursor()
    command_1_input = input("\n\nEnter the name of the intersection to find (wildcards _ and % allowed): ")

    # Find the intersection that matches user-entered intersection
    sql_1 = """
            SELECT Intersection_ID, Intersection
            FROM Intersections
            WHERE Intersection LIKE ?
            ORDER BY Intersection ASC;
            """
    
    dbCursor.execute(sql_1, (command_1_input,))
    rows = dbCursor.fetchall()
    if not rows:
        print("No intersections matching that name were found.")

    else:
        for i_id,i_name in rows: # Intersection ID & Intersection Name
            print(f"{i_id} : {i_name}")


#
# Command 2: Find all cameras at an intersection, Note: separated sql for redCamera and speedCamera
#
def command_2(dbConn): 
    dbCursor = dbConn.cursor()
    command_2_input = input("\nEnter the name of the intersection (no wildcards allowed): ")

    # Find red light cameras that matches the entered intersection name
    sql_2_red = """
            SELECT RedCameras.Camera_ID, RedCameras.Address
            FROM RedCameras
            JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
            WHERE Intersections.Intersection = ? COLLATE NOCASE
            ORDER BY RedCameras.Camera_ID ASC;
            """
    dbCursor.execute(sql_2_red, (command_2_input,))
    rows_red = dbCursor.fetchall()

    # Find speed cameras that matches the entered intersection name
    sql_2_speed = """
                SELECT SpeedCameras.Camera_ID, SpeedCameras.Address
                FROM SpeedCameras
                JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
                WHERE Intersections.Intersection = ? COLLATE NOCASE
                ORDER BY SpeedCameras.Camera_ID ASC;
                """
    
    dbCursor.execute(sql_2_speed, (command_2_input,))
    rows_speed = dbCursor.fetchall()

    if rows_red:
        print("\nRed Light Cameras:")
        for cam_ID, Address in rows_red:
            print(f"  {cam_ID} : {Address}")
    else:
        print("\nNo red light cameras found at that intersection.")

    if rows_speed:
        print("\nSpeed Cameras:")
        for cam_ID, Address in rows_speed:
            print(f"  {cam_ID} : {Address}")
    else:
        print("\nNo speed cameras found at that intersection.")


#
# Command 3: Helper function: decides whether user input is valid
#
def command_3_check_format(userInput):
    if not userInput:
        return False
    if userInput[4] != '-' or userInput[7] != '-':
        return False
    
    year = userInput[:4]
    month = userInput[5:7]
    date = userInput[8:]

    if year.isdigit() == False:
        return False
    elif month.isdigit() == False:
        return False
    elif date.isdigit() == False:
        return False
    return True


#
# Command 3: Percentage of violations for a specific date
#
def command_3(dbConn):
    dbCursor = dbConn.cursor()
    command_3_input = input("\nEnter the date that you would like to look at (format should be YYYY-MM-DD): ")

    # Check if the input from user was made with correct format (YYYY-MM-DD)
    if command_3_check_format(command_3_input) == False:
        print("No violations on record for that date.")
        return 0

    # Get total number of red light violatiosn for the date
    sql_3_red = """
                SELECT SUM(Num_Violations)
                FROM RedViolations
                WHERE Violation_Date = ?;
                """
    dbCursor.execute(sql_3_red, (command_3_input,))
    row_red = dbCursor.fetchone()
    res_red = row_red[0] if (row_red is not None and row_red[0] is not None) else 0

    # Get total number of speed violations for the date
    sql_3_speed = """
                SELECT SUM(Num_Violations)
                FROM SpeedViolations
                WHERE Violation_Date = ?;
                """
    dbCursor.execute(sql_3_speed, (command_3_input,))
    row_speed = dbCursor.fetchone()
    res_speed = row_speed[0] if (row_speed is not None and row_speed[0] is not None) else 0

    res_total = res_red + res_speed
    if res_total == 0:
        print("No violations on record for that date.")
        return 0

    # Calculate percentage of each value
    red_percentage = (res_red / res_total) * 100
    speed_percentage = (res_speed / res_total) * 100

    print("Number of Red Light Violations: ", f"{res_red:,}", f"({red_percentage:.3f}%)")
    print("Number of Speed Violations: ", f"{res_speed:,}", f"({speed_percentage:.3f}%)")
    print("Total Number of Violations: ", f"{res_total:,}")


#
# Command 4: Number of cameras at each intersection
#
def command_4(dbConn):
    dbCursor = dbConn.cursor()

    # Calculate total number of rows in RedCameras
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    red_total = dbCursor.fetchone()[0]

    # Calculate total number of rows in SpeedCameras
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    speed_total = dbCursor.fetchone()[0]

    # Get the number of red light cameras at each intersection
    #   if the number of cameras is same, then sort by Intersection_ID
    sql_4_red = """
                SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(RedCameras.Camera_ID) as num_red              
                FROM Intersections
                JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
                GROUP BY Intersections.Intersection, Intersections.Intersection_ID
                ORDER BY num_red DESC, Intersections.Intersection_ID DESC;
                """
    dbCursor.execute(sql_4_red)
    row_red = dbCursor.fetchall()

    print("\nNumber of Red Light Cameras at Each Intersection")
    for name, id, num in row_red:
        if red_total > 0:
            percentage = (num / red_total * 100)
        else:
            percentage = 0
        print(f"  {name} ({id}) : {num:,} ({percentage:.3f}%)")
    # Get the number of speed cameras at each interesection
    #   if the number of cameras is same, then sort by Intersection_ID
    sql_4_speed = """
                SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(SpeedCameras.Camera_ID) as num_speed
                FROM Intersections
                JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
                GROUP BY Intersections.Intersection, Intersections.Intersection_ID
                ORDER BY num_speed DESC, Intersections.Intersection_ID DESC;
                """
    dbCursor.execute(sql_4_speed)
    row_speed = dbCursor.fetchall()

    print("\nNumber of Speed Cameras at Each Intersection")
    for name, id, num in row_speed:
        if speed_total > 0:
            percentage = (num / speed_total * 100)
        else:
            percentage = 0
        print(f"  {name} ({id}) : {num:,} ({percentage:.3f}%)")


#
# Command 5: Number of violations at each intersection, given a year
#
def command_5(dbConn):
    dbCursor = dbConn.cursor()
    command_5_input = input("\nEnter the year that you would like to analyze: ")

    # First, check if the input is valid (is number)
    if command_5_input.isdigit() == False:
        print("Invalid Input.")
        return 0

    # Calculate total number of red light violations
    sql_5_red_total = """
                    SELECT SUM(Num_Violations) 
                    FROM RedViolations
                    WHERE substr(Violation_Date, 1, 4) = ?;
                    """
    dbCursor.execute(sql_5_red_total, (command_5_input,))
    row_red_total = dbCursor.fetchone()

    if (row_red_total and row_red_total[0] is not None):
        red_total = row_red_total[0]
    else:
        red_total = 0

    # Calculate total number of speed violations
    sql_5_speed_total = """
                        SELECT SUM(Num_Violations)
                        FROm SpeedViolations
                        WHERE substr(Violation_Date,1,4) = ?
                        """
    dbCursor.execute(sql_5_speed_total, (command_5_input,))
    row_speed_total = dbCursor.fetchone()

    if (row_speed_total and row_speed_total[0] is not None):
        speed_total = row_speed_total[0]
    else:
        speed_total = 0
    
    # First section: Number of red light violations at each intersection for the year(user input)
    print(f"\nNumber of Red Light Violations at Each Intersection for {command_5_input}")
    if red_total == 0:
        print("No red light violations on record for that year.")
    else: # Outputs exist
        sql_5_red = """
                    SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(RedViolations.Num_Violations) as num_red
                    FROM RedViolations
                    JOIN RedCameras ON RedViolations.Camera_ID = RedCameras.Camera_ID
                    JOIN Intersections ON RedCameras.Intersection_ID = Intersections.Intersection_ID
                    WHERE substr(RedViolations.Violation_Date, 1, 4) = ?
                    GROUP BY Intersections.Intersection_ID
                    ORDER BY num_red DESC, Intersections.Intersection_ID DESC;
                    """
        dbCursor.execute(sql_5_red, (command_5_input,))
        results_red = dbCursor.fetchall()

        for name, id, num in results_red:
            if red_total > 0:
                percentage = (num / red_total * 100.0) 
            else:
                percentage = 0
            print(f"  {name} ({id}) : {num:,} ({percentage:.3f}%)")
        print(f"Total Red Light Violations in {command_5_input} :", f"{red_total:,}")


    # Second section: Number of speed violations at each intersection for the year(user input)
    print(f"\nNumber of Speed Violations at Each Intersection for {command_5_input}")
    if speed_total == 0:
        print("No speed violations on record for that year.")
    else: # Outputs exist
        sql_5_speed = """
                    SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(SpeedViolations.Num_Violations) as num_speed
                    FROM SpeedViolations
                    JOIN SpeedCameras ON SpeedViolations.Camera_ID = SpeedCameras.Camera_ID
                    JOIN Intersections ON SpeedCameras.Intersection_ID = Intersections.Intersection_ID
                    WHERE substr(SpeedViolations.Violation_Date, 1, 4) = ?
                    GROUP BY Intersections.Intersection_ID
                    ORDER BY num_speed DESC, Intersections.Intersection_ID DESC;
                    """
        dbCursor.execute(sql_5_speed, (command_5_input,))
        results_speed = dbCursor.fetchall()

        for name, id, num in results_speed:
            if speed_total > 0:
                percentage = (num / speed_total * 100.0)
            else:
                percentage = 0
            print(f"  {name} ({id}) : {num:,} ({percentage:.3f}%)")
        print(f"Total Speed Violations in {command_5_input} :", f"{speed_total:,}")


#
# Command 6: Number of violations by year, given a camera ID
#
def command_6(dbConn):
    dbCursor = dbConn.cursor()
    command_6_input = input("\nEnter a camera ID: ")

    sql_6_check_match_red = """
                            SELECT Address
                            FROM RedCameras
                            WHERE Camera_ID = ?;
                            """
    dbCursor.execute(sql_6_check_match_red, (command_6_input,))
    row_red = dbCursor.fetchone()
    
    sql_6_check_match_speed = """
                            SELECT Address
                            FROM SpeedCameras
                            WHERE Camera_ID = ?;
                            """
    dbCursor.execute(sql_6_check_match_speed, (command_6_input,))
    row_speed = dbCursor.fetchone()

    if not (row_red or row_speed):
        print("No cameras matching that ID were found in the database.\n")
        return 0
    
    if row_red:
        sql_6 = """
                    SELECT substr(Violation_Date, 1, 4) as year, SUM(Num_Violations) as num_red
                    FROM RedViolations
                    WHERE Camera_ID = ?
                    GROUP BY year
                    ORDER BY year ASC;                 
                """
    else: # if row_red is empty, only matching results found in speed violations
        sql_6 = """
                SELECT substr(Violation_Date, 1, 4) as year, SUM(Num_Violations) as num_speed
                FROM SpeedViolations
                WHERE Camera_ID = ?
                GROUP BY year
                ORDER BY year ASC;
                """

    dbCursor.execute(sql_6, (command_6_input,))
    rows = dbCursor.fetchall()

    print(f"Yearly Violations for Camera {command_6_input}")
    years = []
    nums = []

    for year, num in rows:
        if num is None:
            num = 0
        else:
            years.append(year)
            nums.append(num)
            print(f"{year} : {num:,}")

    YorN = input("\nPlot? (y/n) ")
    if YorN == 'y': # Do not accept 'Y' or other input
        #import already given
        plt.figure()
        plt.plot(years, nums)
        plt.xlabel("Year")
        plt.ylabel("Number of Violations")
        plt.title(f"Yearly Violations for Camera {command_6_input}")
        plt.show()
    else:
        return 0


#
# Command 7: Number of violations by month, given a camera ID and year
#
def command_7(dbConn):
    dbCursor = dbConn.cursor()
    
    command_7_input_id = input("\nEnter a camera ID: ")

    # Check whether the user-entered camera ID exists in the table(RedCameras)
    sql_7_check_match_red = """
                            SELECT *
                            FROM RedCameras
                            WHERE Camera_ID = ?
                            LIMIT 1;
                            """
    dbCursor.execute(sql_7_check_match_red, (command_7_input_id,))
    row_red = dbCursor.fetchone()

    # Check whether the user-entered camera ID exists in the table(SpeedCameras)
    sql_7_check_match_speed = """
                            SELECT *
                            FROM SpeedCameras
                            WHERE Camera_ID = ?
                            LIMIT 1;
                            """
    dbCursor.execute(sql_7_check_match_speed, (command_7_input_id,))
    row_speed = dbCursor.fetchone()

    # Not found on both tables
    if row_red is None and row_speed is None:
        print("No cameras matching that ID were found in the database.")
        return 0
    
    # else: checked that the camera id exists -> now get the year input
    command_7_input_year = input("Enter a year: ")

    # Decide whether the input is valid or not
    if not command_7_input_year.isdigit() or len(command_7_input_year) != 4:
        print("Invalid Input: Manually added: compare with the auto grader!")
        return 0
    
    if row_red is not None:
        # Extract month from Violation_Date
        # Calculate sum of violations by month
        sql_7 = """
                SELECT substr(Violation_Date, 6, 2) as month, SUM(Num_Violations) as num
                FROM RedViolations
                WHERE Camera_ID = ? AND substr(Violation_Date, 1, 4) = ?
                GROUP BY month
                ORDER BY month ASC;
                """
    else: # row_speed is not none
        sql_7 = """
                SELECT substr(Violation_Date, 6, 2) as month, SUM(Num_Violations) as num
                FROM SpeedViolations
                WHERE Camera_ID = ? AND substr(Violation_Date, 1, 4) = ?
                GROUP BY month
                ORDER BY month ASC;
                """
    dbCursor.execute(sql_7, (command_7_input_id, command_7_input_year))
    results = dbCursor.fetchall()

    print(f"Monthly Violations for Camera {command_7_input_id} in {command_7_input_year}")
    months = []
    nums = []

    for month, num in results:
        if num is None:
            num = 0
        else:
            months.append(month)
            nums.append(num)
            print(f"{month}/{command_7_input_year} : {num:,}")
    
    YorN = input("\nPlot? (y/n) ")
    if YorN == 'y': # not accepting even Y
        plt.figure()
        plt.plot(months, nums)
        plt.xlabel("Month")
        plt.ylabel("Number of Violations")
        plt.title(f"Monthly Violations for Camera {command_7_input_id} ({command_7_input_year})")
        plt.show()
    else:
        return 0


#
# Command 8: Compare the number of red light and speed violations, given a year
#
def command_8(dbConn):
    dbCursor = dbConn.cursor()
    command_8_input = input("\nEnter a year: ")
    if not command_8_input.isdigit() or len(command_8_input) != 4:
        print("Invalid Input: Manually added: compare with the auto grader!")
        return 0
    
    # sql for first 5 days of red light violations
    sql_8_red_first5 = """
                    SELECT Violation_Date, SUM(Num_Violations) as num
                    FROM RedViolations
                    WHERE substr(Violation_Date, 1, 4) = ?
                    GROUP BY Violation_Date
                    ORDER BY Violation_Date ASC
                    LIMIT 5;
                    """
    dbCursor.execute(sql_8_red_first5, (command_8_input,))
    results_red_first5 = dbCursor.fetchall()

    # sql for last 5 days of red light violations
    # Note: Since DESC in inner SELECT results in last date coming right after first 5,
    #   another ASC by Violation_Date on the outer SELECT is required. 
    sql_8_red_last5 = """ SELECT Violation_Date, num FROM(
                    SELECT Violation_Date, SUM(Num_Violations) as num
                    FROM RedViolations
                    WHERE substr(Violation_Date, 1, 4) = ?
                    GROUP BY Violation_Date
                    ORDER BY Violation_Date DESC
                    LIMIT 5
                    )
                    ORDER BY Violation_Date ASC;
                    """
    dbCursor.execute(sql_8_red_last5, (command_8_input,))
    results_red_last5 = dbCursor.fetchall()

    #Same for speed, too
    sql_8_speed_first5 = """
                    SELECT Violation_Date, SUM(Num_Violations) as num
                    FROM SpeedViolations
                    WHERE substr(Violation_Date, 1, 4) = ?
                    GROUP BY Violation_Date
                    ORDER BY Violation_Date ASC
                    LIMIT 5;
                    """
    dbCursor.execute(sql_8_speed_first5, (command_8_input,))
    results_speed_first5 = dbCursor.fetchall()

    sql_8_speed_last5 = """ SELECT Violation_Date, num FROM(
                    SELECT Violation_Date, SUM(Num_Violations) as num
                    FROM SpeedViolations
                    WHERE substr(Violation_Date, 1, 4) = ?
                    GROUP BY Violation_Date
                    ORDER BY Violation_Date DESC
                    LIMIT 5
                    )
                    ORDER BY Violation_Date ASC;
                    """
    dbCursor.execute(sql_8_speed_last5, (command_8_input,))
    results_speed_last5 = dbCursor.fetchall()

    #sql done, now formatting output
    print("Red Light Violations:")
    for date, violation_num in results_red_first5:
        print(f"{date} {violation_num}")
    for date, violation_num in results_red_last5:
        print(f"{date} {violation_num}")

    print("Speed Violations:")
    for date, violation_num in results_speed_first5:
        print(f"{date} {violation_num}")
    for date, violation_num in results_speed_last5:
        print(f"{date} {violation_num}")

    # Now, asking for whether to plot or not
    # Note: timedelta is the gap between dates
    YorN = input("\nPlot? (y/n) ")

    if YorN == 'y': # not accepting even Y
        import datetime
        # start_date = date()

        # Set number of red light violations for each date
        dbCursor.execute("""
                        SELECT Violation_Date, SUM(Num_Violations)
                        FROM RedViolations
                        WHERE substr(Violation_Date, 1, 4) = ?
                        GROUP BY Violation_Date;
                        """, (command_8_input,))
        red_results = dict(dbCursor.fetchall())

        # Set number of speed violations for each date
        dbCursor.execute("""
                        SELECT Violation_Date, SUM(Num_Violations)
                        FROM SpeedViolations
                        WHERE substr(Violation_Date, 1, 4) = ?
                        GROUP BY Violation_Date;
                        """, (command_8_input,))
        speed_results = dict(dbCursor.fetchall())

        dates = []
        red_violation_nums = []
        speed_violation_nums = []

        start_date = datetime.datetime(int(command_8_input), 1, 1)
        end_date = datetime.datetime(int(command_8_input), 12, 31)
        curr_date = start_date

        while curr_date <= end_date:
            date_str = curr_date.strftime('%Y-%m-%d')
            dates.append(curr_date)
            red_violation_nums.append(red_results.get(date_str, 0))
            speed_violation_nums.append(speed_results.get(date_str, 0))
            curr_date = curr_date + datetime.timedelta(days = 1)

        days = list(range(1, len(dates) + 1))

        plt.figure()
        plt.plot(days, red_violation_nums, label = 'Red Light', color = 'red')
        plt.plot(days, speed_violation_nums, label = 'Speed', color = 'orange')
        plt.xlabel("Days")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations Each Day of {command_8_input}")
        plt.show()

    else:
        return 0


#
# Command 9: Find cameras located on a street
#
def command_9(dbConn):
    dbCursor = dbConn.cursor()
    command_9_input = input("\nEnter a street name: ")

    # Find red light camera that has user-entered street name in the address
    sql_9_red = """
                SELECT Camera_ID, Address, Latitude, Longitude
                FROM RedCameras
                WHERE Address LIKE ?
                ORDER BY Camera_ID ASC;
                """
    wildCard = f"%{command_9_input}%" # Set an wildcard to find cameras with the street name included in the address

    dbCursor.execute(sql_9_red, (wildCard,))
    rows_red = dbCursor.fetchall()
    # Find speed camera that has user-entered street name in the address
    sql_9_speed = """
                SELECT Camera_ID, Address, Latitude, Longitude
                FROM SpeedCameras
                WHERE Address LIKE ?
                ORDER BY Camera_ID ASC;
                """
    dbCursor.execute(sql_9_speed, (wildCard,))
    rows_speed = dbCursor.fetchall()

    # Result not found on both tables
    if not rows_red and not rows_speed:
        print("There are no cameras located on that street.")
        return 0

    # else: whether rows_red or rows_speed or both contains data
    print(f"\nList of Cameras Located on Street: {command_9_input}")

    if rows_red and not rows_speed:
        print("  Red Light Cameras:")
        for id, address, lat, long in rows_red:
            print(f"     {id} : {address} ({lat}, {long})")
            
        print("  Speed Cameras:")

    if rows_speed and not rows_red:
        print("  Red Light Cameras:")
        print("  Speed Cameras:")
        for id, address, lat, long in rows_speed:
            print(f"     {id} : {address} ({lat}, {long})")

    if rows_red and rows_speed:
        print("  Red Light Cameras:")
        for id, address, lat, long in rows_red:
            print(f"     {id} : {address} ({lat}, {long})")

        print("  Speed Cameras:")
        for id, address, lat, long in rows_speed:
            print(f"     {id} : {address} ({lat}, {long})")

    
    YorN = input("\nPlot? (y/n) ")
    if (YorN == 'y'):
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868] #area covered by map
        plt.imshow(image, extent=xydims)
        
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])

        if rows_red:
            plt.plot([r[3] for r in rows_red], [r[2] for r in rows_red], color = 'red')
            for row in rows_red:
                plt.annotate(str(row[0]), (row[3], row[2]), color = 'black', fontsize = 8)
        if rows_speed:
            plt.plot([r[3] for r in rows_speed], [r[2] for r in rows_speed], color = 'orange')
            for row in rows_speed:
                plt.annotate(str(row[0]), (row[3], row[2]), color = 'black', fontsize = 8)
        
        
        plt.title(f"Cameras on Street: {command_9_input}")
        plt.show()
    else:
        return 0


##################################################################  
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Fall 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

# Infinitely loops until the user enters 'x'
while True:
    print("\nSelect a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")

    user_input = input("Your choice --> ")
    if user_input == 'x':
        print("Exiting program.")
        break
    elif user_input == '1':
        command_1(dbConn)
    elif user_input == '2':
        command_2(dbConn)
    elif user_input == '3':
        command_3(dbConn)
    elif user_input == '4':
        command_4(dbConn)
    elif user_input == '5':
        command_5(dbConn)
    elif user_input == '6':
        command_6(dbConn)
    elif user_input == '7':
        command_7(dbConn)
    elif user_input == '8':
        command_8(dbConn)
    elif user_input == '9':
        command_9(dbConn)
    else:
        print("Error, unknown command, try again...\n")

dbConn.close()

#
# done
#
