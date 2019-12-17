import pandas as pd
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, flight_terminals, arrival_runways, departure_runways):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.flight_terminals_ = flight_terminals
        self.arrival_runways_ = arrival_runways
        self.departure_runways_ = departure_runways
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        for flight in flights:
            print(" - " + flight + ":")
            for terminal in terminals:
                if self.Value(self.flight_terminals_[flight][terminal]):
                    print("    - ", terminal)
            for arrival_runway in runways:
                if self.Value(self.arrival_runways_[flight][arrival_runway]):
                    print("    - ", arrival_runway)
            for departure_runway in runways:
                if self.Value(self.departure_runways_[flight][departure_runway]):
                    print("    - ", departure_runway)

        print()

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
# Flight_Terminal(flight, terminal)
# Flight_Grounded(flight, time)
# Terminal_Occupied(terminal, time)
# Amount_Terminal(time) =  Flight_Grounded(flight, time)T(Flight_Terminal(flight, terminal)
# Constraints
# The same runway cannot be occupied at the same time, neither for arrival nor for departure.
# ∀x ∀y ∀z ∀t: x!=y: x,y ∈ flight: z ∈ runway: t ∈ time:
# Arrival_Time(x,t) ∧ Arrival_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Arrival_Runway(y, z)
# Arrival_Time(x,t) ∧ Departure_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Departure_Time(y, z)
# Departure_Time(x,t) ∧ Arrival_Time(y, t) =>  !Departure_Runway(x, z) ∧ !Arrival_Runway(y, z)
# Departure_Time(x,t) ∧ Departure_Time(y, t) =>  !Departure_Runway(x, z) ∧ !Departure_Time(y, z)
#
# Further to that, planes are occupying their allocated gate the whole timespan between arrival and departure during
# which the gate capacity of the terminal needs to be taken into consideration when allocating terminals
# ∀x, ∀y, ∀t : t ∈ time where t > x.arrival and t < x.departure
# Flight_Terminal(x, y) => Terminal_Occupied(x,y, t)
# sum(Terminal_Occupied(y, t) < terminal max capacity

flights = list(set(flight_schedule.index))
terminals = list(set(terminal_capacity.index))
runways = list(set(taxi_distances.index))
times = set()
for flight in flights:
    times.add(flight_schedule['Arrival'][flight])
    times.add(flight_schedule['Departure'][flight])
print(flights)
print(terminals)
print(runways)
print(times)

model = cp_model.CpModel()
arrival_runways = {}
for flight in flights:
    variables = {}
    for runway in runways:
        variables[runway] = model.NewBoolVar(flight+runway+'arrival')
    arrival_runways[flight] = variables

departure_runways = {}
for flight in flights:
    variables = {}
    for runway in runways:
        variables[runway] = model.NewBoolVar(flight+runway+'departure')
    departure_runways[flight] = variables

arrival_time = {}
for flight in flights:
    variables = {}
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'arrival')
        if flight_schedule['Arrival'][flight] == time:
            model.AddBoolAnd([variables[str(time)]])
    arrival_time[flight] = variables
departure_time = {}
for flight in flights:
    variables={}
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'departure')
        if flight_schedule['Departure'][flight] == time:
            model.AddBoolAnd([variables[str(time)]])
    departure_time[flight] = variables

flight_grounded = {}
for flight in flights:
    variables = {}
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'grounded')
        if flight_schedule['Departure'][flight] >= time and flight_schedule['Arrival'][flight] <= time:
            model.AddBoolAnd([variables[str(time)]])
    flight_grounded[flight] = variables

flight_terminal = {}
for flight in flights:
    variables = {}
    for terminal in terminals:
        variables[terminal] = model.NewBoolVar(flight+terminal)
    flight_terminal[flight] = variables

terminal_capacity_at_given_time = {}
for terminal in terminals:
    terminal_capacity_at_given_time[terminal] = {}
    for time in times:
        terminal_capacity_at_given_time[terminal][str(time)] = model.NewIntVar(0, int(terminal_capacity['Gates'][terminal]),
                                                                               terminal + "_" + str(time)+"_Gates")

for flight in flights:

    # A flight can only have one arrival runway
    variables = []
    for runway in runways:
        variables.append(arrival_runways[flight][runway])
    model.AddBoolOr(variables)

    variables = []
    for runway in runways:
        variables.append(departure_runways[flight][runway])
    model.AddBoolOr(variables)

    variables = []
    for terminal in terminals:
        variables.append(flight_terminal[flight][terminal])
    model.AddBoolOr(variables)

    for i in range(3):
        for j in range(i + 1, 3):
            model.AddBoolOr([arrival_runways[flight][runways[i]].Not(),
                             arrival_runways[flight][runways[j]].Not()])
            model.AddBoolOr([flight_terminal[flight][terminals[i]].Not(),
                             flight_terminal[flight][terminals[j]].Not()])
    # The same runway cannot be occupied at the same time, neither for arrival nor for departure.
    # ∀x ∀y ∀z ∀t: x!=y: x,y ∈ flight: z ∈ runway: t ∈ time:
    # Arrival_Time(x,t) ∧ Arrival_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Arrival_Runway(y, z)
    # Arrival_Time(x,t) ∧ Departure_Time(y, t) =>  !Arrival_Runway(x, z) ∧ !Departure_Time(y, z)
    # Departure_Time(x,t) ∧ Departure_Time(y, t) =>  !Departure_Runway(x, z) ∧ !Departure_Time(y, z)
    other_flights = list(flights)
    other_flights.remove(flight)
    for other_flight in other_flights:
        for runway in runways:
            for time in times:
                time = str(time)
                model.AddBoolAnd([arrival_runways[flight][runway].Not(), arrival_runways[other_flight][runway].Not()
                                  ]).OnlyEnforceIf([arrival_time[flight][time],
                                                   arrival_time[other_flight][time]])
                model.AddBoolAnd([arrival_runways[flight][runway].Not(), departure_runways[other_flight][runway].Not()
                                  ]).OnlyEnforceIf([arrival_time[flight][time],
                                                    departure_time[other_flight][time]])
                model.AddBoolAnd([departure_runways[flight][runway].Not(), departure_runways[other_flight][runway].Not()
                                  ]).OnlyEnforceIf([departure_time[flight][time],
                                                    departure_time[other_flight][time]])

for terminal in terminals:
    for time in times:
        gates_in_use = []
        for flight in flights:
            time = str(time)
            var = model.NewBoolVar(flight + terminal + 'gate')
            model.AddBoolAnd([var]).OnlyEnforceIf([flight_terminal[flight][terminal],
                              flight_grounded[flight][time]])
        model.Add(sum(gates_in_use) <= terminal_capacity_at_given_time[terminal][time])
total_taxi_distace = model.NewIntVar()
for flight in flights:


solver = cp_model.CpSolver()
status = solver.SearchForAllSolutions(model, SolutionPrinter(flight_terminal, arrival_runways, departure_runways))

if status == solver.OPTIMAL:
    print("Optimal Solution")
else:  # No optimal solution was found.
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')