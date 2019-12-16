import pandas as pd
from ortools.linear_solver import pywraplp

flight_schedule = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Flight schedule', index_col=0)
print(flight_schedule)

taxi_distances = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Taxi distances', index_col=0)
print(taxi_distances)

terminal_capacity = pd.read_excel('Assignment_DA_2_b_data.xlsx', 'Terminal capacity', index_col=0)
print(terminal_capacity)

# Decision Variables
# Arrival_Runway(flight, runway)
# Arrival_Time(flight, time)
# Departure_Time(flight, time)
# Departure_Runway(flight, runway)
# Runway_In_Use(time, runway)
# Flights_Overlap(flight, flight)
# Flight_Terminal(flight, terminal)

# Constraints
# The same runway cannot be occupied at the same time, neither for arrival nor for departure.
# ∀x ∀y ∀z ∀t: x!=y: x,y ∈ flight: z ∈ runway: t ∈ time:
# Arrival_Time(x,t) ∧ Arrival_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Arrival_Runway(y, z)
# Arrival_Time(x,t) ∧ Departure_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Departure_Time(y, z)
# Departure_Time(x,t) ∧ Arrival_Time(y, t) =>  !Departure_Runway(x, z) ∧ !Arrival_Runway(y, z)
# Departure_Time(x,t) ∧ Departure_Time(y, t) =>  !Departure_Runway(x, z) ∧ !Departure_Time(y, z)