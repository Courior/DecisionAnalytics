from ortools.sat.python import cp_model
# A. define the set of variables you need for modelling this constrained optimisation problem
# Honestly Im having a lot of trouble with telling the difference between variables, objects and attributtes in this
# class, it seems obvious up until I have to put them down on paper and then with the diference between the paper maths
# and the or-tools im finding it really hard to keep it all straight.
# Project= <project_1,project_2,project_3,project_4,project_5,project_6,project_7,project_8,project_9,project_10>
# Value= <18,51,32,80,65,44,91,65,92,69>
# Cost= <12,43,80,76,42,43,87,43,65,62>
#
# B. Define the constraints to model the incompatibilities between projects
# project_4=> ¬project_1
# project_7=> ¬project_1∧¬project_2
# project_10=> ¬project_4
# #
# C. Define the constraints to model the prerequisites of projects
# project_3=> project_1∧project_2
# project_5=> project_3∧project_4
# project_8=> project_3∧project_6
# project_9=> project_3∧project_5
#
# D. Define the constraint to model the overall budget restriction
#
# E. Define the maximisation criterion for the problem [1 point]
# ^x∈ Profit ∀^x∈Profit:-f(^x)<= f(x)
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, items, project_planned, total_cost, total_value):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.items_ = items
        self.project_planned_ = project_planned
        self.total_cost_ = total_cost
        self.total_value_ = total_value

    def OnSolutionCallback(self):
        print("Feasible solution:")
        for i in range(0,len(self.items_)):
            if self.Value(self.project_planned_[i]):
                print("  - Project "+str(i+1)+" (value="+str(self.items_[i][0])+",cost="+str(self.items_[i][1])+")")
        print("  - Total weight: "+str(self.Value(self.total_cost_)))
        print("  - Total value: "+str(self.Value(self.total_value_)))


def main():
    #F
    model = cp_model.CpModel()

    #    knapsack_size = 15
    #    projects = [(18,12,[],[]),(51,43,[],[]),(32,80,[1,2],[]),(80,76,[],[1]),(65,42,[3,4],[]),(44,43,[],[]),(91,87,[],[1,2]),(65,43,[3,6],[]),(92,65,[3,5],[]),(69,62,[],[4])]

    maximum_budget = 400
    projects = [(18, 12, [], []),
                (51, 43, [], []),
                (32, 12, [1, 2], []),
                (80, 76, [], [1]),
                (65, 42, [3, 4], []),
                (44, 43, [], []),
                (91, 87, [], [1, 2]),
                (65, 43, [3, 6], []),
                (92, 65, [3, 5], []),
                (69, 62, [], [4])]

    project_planned = []
    cost_of_projects = []
    value_of_projects = []
    profit_of_projects = []
    for i in range(0, len(projects)):
        project_planned.append(model.NewBoolVar("project_" + str(i)))
        cost_of_projects.append(projects[i][0] * project_planned[i])
        value_of_projects.append(projects[i][1] * project_planned[i])
        profit_of_projects.append((projects[i][1] - projects[i][0])* project_planned[i])
    for i in range(0, len(projects)):
        # G
        for required in projects[i][2]:
            model.AddBoolAnd([project_planned[required-1]]).OnlyEnforceIf(project_planned[i])
        # H
        for incompatible in projects[i][3]:
            model.AddBoolAnd([project_planned[incompatible-1].Not()]).OnlyEnforceIf(project_planned[i])

    total_cost = sum(cost_of_projects)
    # I
    model.Add(total_cost <= maximum_budget)

    total_value = sum(value_of_projects)
    # J
    total_profit = sum(profit_of_projects)
    model.Maximize(total_profit)

    # model.AddDecisionStrategy(in_knapsack, cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE)
    solver = cp_model.CpSolver()
  #  solver.SearchForAllSolutions(model, SolutionPrinter(projects, project_planned, total_cost, total_value))

    print()
    model.Maximize(total_value)
    status = solver.Solve(model)
    print(solver.StatusName(status))
    for i in range(0, len(projects)):
        if solver.Value(project_planned[i]):
            print("  - Project " + str(i + 1) + " (value=" + str(projects[i][0]) + ",cost=" + str(projects[i][1]) + ")")
    print("Total cost: " + str(solver.Value(total_cost)))
    print("Total value: " + str(solver.Value(total_value)))
    print("Total profit: " + str(solver.Value(total_profit)))


#    print()
#    print('Statistics')
#    print('  - conflicts       : %i' % solver.NumConflicts())
#    print('  - branches        : %i' % solver.NumBranches())
#    print('  - wall time       : %f s' % solver.WallTime())


main()