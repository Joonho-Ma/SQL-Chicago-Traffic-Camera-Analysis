# SQL-Chicago-Traffic-Camera-Analysis
Console-operated program to analyze Chicago's Traffic Cameras

The program is implemented using 'chicago-traffic-cameras' database

# Database structure
Intersections  
Intersection_ID  
Intersection  

# RedCameras
Camera_ID
Intersection_ID  
Address  
Latitude  
Longitude  

# SpeedCameras
Camera_ID  
Intersection_ID  
Address  
Latitude  
Longitude  

# RedViolations
Camera_ID  
Violation_Date  
Num_Violations  

# SpeedViolations
Camera_ID  
Violation_Date  
Num_Violations  
  
# Comment
The program provides 9 types of command  
1. Find an intersection by name
2. Find all cameras at an intersection
3. Percentage of violations for a specific date
4. Number of cameras at each intersection
5. Number of violations at each intersection, given a year
6. Number of violations by year, given a camera ID
7. Number of violations by month, given a camera ID and year
8. Compare the number of red light and speed violations, given a year
9. Find cameras located on a street

Particularly, command 6,7,8 provides plotting options through python and command 9 provides plots on a map.
