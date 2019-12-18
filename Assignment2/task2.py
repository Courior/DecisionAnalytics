import pandas as pd
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, flight_terminals, arrival_runways, departure_runways, arrival_time, departure_time,flight_using_terminal_at_given_time):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.flight_terminals_ = flight_terminals
        self.arrival_runways_ = arrival_runways
        self.departure_runways_ = departure_runways
        self.arrival_time_ = arrival_time
        self.departure_time_ = departure_time
        self.flight_using_terminal_at_given_time_ = flight_using_terminal_at_given_time
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)
        terminal_a ="a"
        terminal_b ="b"
        terminal_c ="c"
        arrival_a = "a"
        arrival_b = "b"
        working = True
        under_capacity_terminal_a = True
        under_capacity_terminal_b = True
        under_capacity_terminal_c = True
        departure_b = "b"
        departure_h = "h"
        flight_a_arrival = "a"
        for terminal in sorted(terminals):
            print("-"+terminal,"Capacity:")
            for time in sorted(times):
                print("    - ", str(time),
                      ",".join(flight for flight in flights if self.Value(self.flight_using_terminal_at_given_time_[(terminal,str(time))][flight] )))
                if terminal == "Terminal A" and sum([self.Value(self.flight_using_terminal_at_given_time_[(terminal,str(time))][flight]) for flight in flights]) > 2:
                    under_capacity_terminal_a = False
                if terminal == "Terminal B" and sum([self.Value(self.flight_using_terminal_at_given_time_[(terminal,str(time))][flight]) for flight in flights])  > 4:
                    under_capacity_terminal_b = False
                if terminal == "Terminal C" and sum([self.Value(self.flight_using_terminal_at_given_time_[(terminal,str(time))][flight]) for flight in flights])  > 5:
                    under_capacity_terminal_c = False

        for flight in sorted(flights):
            print(" - " + flight + ":")
            for terminal in sorted(terminals):
                if self.Value(self.flight_terminals_[flight][terminal]):
                    print("    - ", terminal)
                    if terminal == "Terminal A":
                        if flight == "Flight A":
                            terminal_a = terminal
                        if flight == "Flight B":
                            terminal_b = terminal
                        if flight == "Flight C":
                            terminal_c = terminal
            for arrival_runway in sorted(runways):
                if self.Value(self.arrival_runways_[flight][arrival_runway]):
                    print("    - ", arrival_runway)
                    if flight == "Flight A":
                        arrival_a = arrival_runway
                    if flight == "Flight B":
                        arrival_b = arrival_runway
            for departure_runway in sorted(runways):
                if self.Value(self.departure_runways_[flight][departure_runway]):
                    print("    - ", departure_runway)
                    if flight == "Flight B":
                        departure_b = departure_runway
                    if flight == "Flight H":
                        departure_h = departure_runway
            for time in sorted(times):
                if self.Value(self.arrival_time_[flight][str(time)]):
                    print("    - ", "Arrival:",str(time))
                    if flight == "Flight A":
                        flight_a_arrival = str(time)
                if self.Value(self.departure_time_[flight][str(time)]):
                    print("    - ", "Departure:", str(time))
        if terminal_a == terminal_b and terminal_b == terminal_c:
            working = False
        assert(working), "Flight A, B and C should all have different Terminals"
        assert(arrival_a != arrival_b), "Flight A and B must have different runway arrivals"
        assert(under_capacity_terminal_a), "Terminal A capacity exceeded 2 at some time"
        assert(under_capacity_terminal_b), "Terminal A capacity exceeded 4 at some time"
        assert(under_capacity_terminal_c), "Terminal A capacity exceeded 5 at some time"
        assert(departure_b != departure_h), "Fight B and H can not have the same departure runway"
        assert(flight_a_arrival == "08:00:00"), "Flight A can only arrive at 08:00:00"

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
actual_arrivals = []
for flight in flights:
    variables = {}
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'arrival')
        if flight_schedule['Arrival'][flight] == time:
            actual_arrivals.append(variables[str(time)])
        else:
            actual_arrivals.append(variables[str(time)].Not())
    arrival_time[flight] = variables
model.AddBoolAnd(actual_arrivals)
departure_time = {}
actual_departures = []
for flight in flights:
    variables={}
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'departure')
        if flight_schedule['Departure'][flight] == time:
            actual_departures.append(variables[str(time)])
        else:
            actual_departures.append(variables[str(time)].Not())
    departure_time[flight] = variables
model.AddBoolAnd(actual_departures)

flight_grounded = {}
for flight in flights:
    variables = {}
    grounded_times = []
    for time in times:
        variables[str(time)] = model.NewBoolVar(flight+str(time)+'grounded')
        if flight_schedule['Departure'][flight] > time and flight_schedule['Arrival'][flight] <= time:
            grounded_times.append(variables[str(time)])
        else:
            grounded_times.append(variables[str(time)].Not())
    model.AddBoolAnd(grounded_times)
    flight_grounded[flight] = variables

flight_terminal = {}
for flight in flights:
    variables = {}
    for terminal in terminals:
        variables[terminal] = model.NewBoolVar(flight+terminal)
    flight_terminal[flight] = variables

#terminal_capacity_at_given_time = {}
#for terminal in terminals:
    #terminal_capacity_at_given_time[terminal] = {}
    #for time in times:
        #terminal_capacity_at_given_time[terminal][str(time)] = model.NewIntVar(int(terminal_capacity['Gates'][terminal]), int(terminal_capacity['Gates'][terminal]),
        #                                                                       terminal + "_" + str(time)+"_Gates")
flight_using_terminal_at_given_time = {}
for terminal in terminals:
    for time in times:
        time = str(time)
        variables = {}
        for flight in flights:
            variables[flight] = model.NewBoolVar(flight + terminal + 'gate' + time)
        flight_using_terminal_at_given_time[(terminal, time)] = variables

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
            model.AddBoolOr([departure_runways[flight][runways[i]].Not(),
                             departure_runways[flight][runways[j]].Not()])
            model.AddBoolOr([flight_terminal[flight][terminals[i]].Not(),
                             flight_terminal[flight][terminals[j]].Not()])
    # The same runway cannot be occupied at the same time, neither for arrival nor for departure.
    # ∀x ∀y ∀z ∀t: x!=y: x,y ∈ flight: z ∈ runway: t ∈ time:
    # Arrival_Time(x,t) ∧ Arrival_Time(y, t) =>  !Arrival_Runway(x, z) V !Arrival_Runway(y, z)
    # Arrival_Time(x,t) ∧ Departure_Time(y, t) =>  !Arrival_Runway(x, z) V !Departure_Time(y, z)
    # Departure_Time(x,t) ∧ Departure_Time(y, t) =>  !Departure_Runway(x, z) V !Departure_Runway(y, z)
    other_flights = list(flights)
    other_flights.remove(flight)
    for other_flight in other_flights:
        for runway in runways:
            for time in times:
                time = str(time)
                model.AddBoolOr([arrival_runways[flight][runway].Not(),
                                 arrival_runways[other_flight][runway].Not()]).OnlyEnforceIf([
                    arrival_time[flight][time], arrival_time[other_flight][time]
                ])
                model.AddBoolOr([arrival_runways[flight][runway].Not(),
                                 departure_runways[other_flight][runway].Not()]).OnlyEnforceIf([
                    arrival_time[flight][time], departure_time[other_flight][time]
                ])
                model.AddBoolOr([departure_runways[flight][runway].Not(),
                                 departure_runways[other_flight][runway].Not()]).OnlyEnforceIf([
                    departure_time[flight][time], departure_time[other_flight][time]
                ])

for terminal in terminals:
    for time in times:
        for flight in flights:
            time = str(time)
            model.AddBoolAnd([flight_using_terminal_at_given_time[(terminal,time)][flight]]).OnlyEnforceIf([flight_terminal[flight][terminal],
                              flight_grounded[flight][time]])
            model.AddBoolAnd([flight_using_terminal_at_given_time[(terminal, time)][flight].Not()]).OnlyEnforceIf(
                [flight_terminal[flight][terminal].Not()])
        model.Add(sum(list(flight_using_terminal_at_given_time[(terminal, time)].values())) <= int(terminal_capacity['Gates'][terminal]))
total_taxi_distances = []
for terminal in terminals:
    for flight in flights:
        for runway in runways:
            taxi_to_terminal = model.NewBoolVar(terminal+flight+runway+"taxi_to")
            model.AddBoolAnd([taxi_to_terminal]).OnlyEnforceIf([flight_terminal[flight][terminal], arrival_runways[flight][runway]])
            total_taxi_distances.append(taxi_to_terminal * taxi_distances[terminal][runway])
            taxi_from_terminal = model.NewBoolVar(terminal+flight+runway+"taxi_from")
            model.AddBoolAnd([taxi_to_terminal]).OnlyEnforceIf([flight_terminal[flight][terminal], departure_runways[flight][runway]])
            total_taxi_distances.append(taxi_to_terminal * taxi_distances[terminal][runway])

total_taxi_distance = sum(total_taxi_distances)
model.Minimize(total_taxi_distance)

solver = cp_model.CpSolver()
#status = solver.SearchForAllSolutions(model, SolutionPrinter(flight_terminal, arrival_runways, departure_runways, arrival_time,departure_time, flight_using_terminal_at_given_time))
status = solver.Solve(model)

if status == 0:
    print("Optimal Solution")
else:  # No optimal solution was found.
    if status == 1:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.', status)

print('Statistics')
print('  - conflicts : %i' % solver.NumConflicts())
print('  - branches  : %i' % solver.NumBranches())
print('  - wall time : %f s' % solver.WallTime())