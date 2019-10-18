from ortools.sat.python import cp_model

## Problem
# There are five houses.
# The Englishman lives in the red house.
# The Spaniard owns the dog.
# Coffee is drunk in the green house.
# The Ukrainian drinks tea.
# The green house is immediately to the right of the ivory house.
# The Old Gold smoker owns snails.
# Kools are smoked in the yellow house.
# Milk is drunk in the middle house.
# The Norwegian lives in the first house.
# The man who smokes Chesterfields lives in the house next to the man with the fox.
# Kools are smoked in the house next to the house where the horse is kept.
# The Lucky Strike smoker drinks orange juice.
# The Japanese smokes Parliaments.
# The Norwegian lives next to the blue house.
# Now, who drinks water? Who owns the zebra?

# Predicates
#   colour
#   nationality
#   pet
#   drink
#   cigarette
model = cp_model.CpModel()
houses = ["House #1",
          "House #2",
          "House #3",
          "House #4",
          "House #5"
          ]
colours = ["Red",
           "Green",
           "Ivory",
           "Yellow",
           "Blue"
           ]

nationalities =["English",
                "Spanish",
                "Ukrainian",
                "Norwegian",
                "Japanese"
                ]

pets =["Dog",
      "Fox",
      "Horse",
      "Snail",
      "Zebra"
      ]
drinks =["Coffee",
        "Tea",
        "Milk",
        "Orange Juice",
        "Water"]
cigarettes =["Old Gold",
            "Kools",
            "Chesterfields",
            "Lucky Strike",
            "Parliaments"]
house_colour = {}

for house in houses:
    variables = {}
    for colour in colours:
        variables[colour] = model.NewBoolVar(house+colour)
    house_colour[house] = variables
    
house_nationality ={}
for house in houses:
    variables = {}
    for nationality in nationalities:
        variables[nationality] = model.NewBoolVar(house+nationality)
    house_nationality[house] = variables    

house_pet ={}
for house in houses:
    variables = {}
    for pet in pets:
        variables[pet] = model.NewBoolVar(house+pet)
    house_pet[house] = variables

house_drink ={}
for house in houses:
    variables = {}
    for drink in drinks:
        variables[drink] = model.NewBoolVar(house+drink)
    house_drink[house] = variables

house_cigarette ={}
for house in houses:
    variables = {}
    for cigarette in cigarettes:
        variables[cigarette] = model.NewBoolVar(house+cigarette)
    house_cigarette[house] = variables

for house in houses:
    model.AddBoolAnd([house_colour[house]["Red"]]).OnlyEnforceIf(house_nationality[house]["English"])

for house in houses:
    model.AddBoolAnd([house_pet[house]["Dog"]]).OnlyEnforceIf(house_nationality[house]["Spanish"])

for house in houses:
    model.AddBoolAnd([house_drink[house]["Coffee"]]).OnlyEnforceIf(house_colour[house]["Green"])

for house in houses:
    model.AddBoolAnd([house_drink[house]["Tea"]]).OnlyEnforceIf(house_nationality[house]["Ukrainian"])

for i in range(4):
    model.AddBoolAnd([house_colour[houses[i+1]]["Green"]]).OnlyEnforceIf(house_colour[houses[i]]["Ivory"])
model.AddBoolAnd([house_colour[houses[4]]["Ivory"].Not()])

for house in houses:
    model.AddBoolAnd([house_pet[house]["Snail"]]).OnlyEnforceIf(house_cigarette[house]["Old Gold"])

for house in houses:
    model.AddBoolAnd([house_colour[house]["Yellow"]]).OnlyEnforceIf(house_cigarette[house]["Kools"])

model.AddBoolAnd([house_drink["House #3"]["Milk"]])
model.AddBoolAnd([house_nationality["House #1"]["Norwegian"]])

for i in range(1,4):
    model.AddBoolOr([
        house_pet[houses[i+1]]["Fox"],
        house_pet[houses[i-1]]["Fox"],
        ]).OnlyEnforceIf(house_cigarette[houses[i]]["Chesterfields"])
model.AddBoolOr([house_pet[houses[1]]["Fox"]]).OnlyEnforceIf(house_cigarette[houses[0]]["Chesterfields"])
model.AddBoolOr([house_pet[houses[3]]["Fox"]]).OnlyEnforceIf(house_cigarette[houses[4]]["Chesterfields"])

for i in range(1,4):
    model.AddBoolOr([
        house_pet[houses[i+1]]["Horse"],
        house_pet[houses[i-1]]["Horse"],
        ]).OnlyEnforceIf(house_cigarette[houses[i]]["Kools"])
model.AddBoolOr([house_pet[houses[1]]["Horse"]]).OnlyEnforceIf(house_cigarette[houses[0]]["Kools"])
model.AddBoolOr([house_pet[houses[3]]["Horse"]]).OnlyEnforceIf(house_cigarette[houses[4]]["Kools"])

for house in houses:
    model.AddBoolAnd([house_drink[house]["Orange Juice"]]).OnlyEnforceIf(house_cigarette[house]["Lucky Strike"])

for house in houses:
    model.AddBoolAnd([house_cigarette[house]["Parliaments"]]).OnlyEnforceIf(house_nationality[house]["Japanese"])

for i in range(1,4):
    model.AddBoolOr([
        house_nationality[houses[i+1]]["Norwegian"],
        house_nationality[houses[i-1]]["Norwegian"],
        ]).OnlyEnforceIf(house_colour[houses[i]]["Blue"])
model.AddBoolOr([house_nationality[houses[1]]["Norwegian"]]).OnlyEnforceIf(house_colour[houses[0]]["Blue"])
model.AddBoolOr([house_nationality[houses[3]]["Norwegian"]]).OnlyEnforceIf(house_colour[houses[4]]["Blue"])

for house in houses:
    variables = []
    for colour in colours:
        variables.append(house_colour[house][colour])
    model.AddBoolOr(variables)

for house in houses:
    variables = []
    for nationality in nationalities:
        variables.append(house_nationality[house][nationality])
    model.AddBoolOr(variables)
    
for house in houses:
    variables = []
    for pet in pets:
        variables.append(house_pet[house][pet])
    model.AddBoolOr(variables)  
    
for house in houses:
    variables = []
    for drink in drinks:
        variables.append(house_drink[house][drink])
    model.AddBoolOr(variables)

for house in houses:
    variables = []
    for cigarette in cigarettes:
        variables.append(house_cigarette[house][cigarette])
    model.AddBoolOr(variables)

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_colour[house][colours[i]].Not(),
                house_colour[house][colours[j]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_nationality[house][nationalities[i]].Not(),
                house_nationality[house][nationalities[j]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_pet[house][pets[i]].Not(),
                house_pet[house][pets[j]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_drink[house][drinks[i]].Not(),
                house_drink[house][drinks[j]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_cigarette[house][cigarettes[i]].Not(),
                house_cigarette[house][cigarettes[j]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            for k in range(5):
                model.AddBoolOr([
                    house_colour[houses[i]][colours[k]].Not(),
                    house_colour[houses[j]][colours[k]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            model.AddBoolOr([
                house_nationality[houses[i]][nationalities[k]].Not(),
                house_nationality[houses[j]][nationalities[k]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            for k in range(5):
                model.AddBoolOr([
                house_pet[houses[i]][pets[k]].Not(),
                house_pet[houses[j]][pets[k]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            for k in range(5):
                model.AddBoolOr([
                house_drink[houses[i]][drinks[k]].Not(),
                house_drink[houses[j]][drinks[k]].Not()])

for house in houses:
    for i in range(5):
        for j in range(i+1, 5):
            for k in range(5):
                model.AddBoolOr([
                house_cigarette[houses[i]][cigarettes[k]].Not(),
                house_cigarette[houses[j]][cigarettes[k]].Not()])

solver = cp_model.CpSolver()
solver.Solve(model)

for house in houses:
     if solver.Value(house_drink[house]["Water"]):
         for nationality in nationalities:
             if solver.Value(house_nationality[house][nationality]):
                 print("The "+ nationality +"drinks water.")
     if solver.Value(house_pet[house]["Zebra"]):
        for nationality in nationalities:
            if solver.Value(house_nationality[house][nationality]):
                print("The " + nationality + "owns the Zebra.")