from ortools.sat.python import cp_model

##Problem
# Carol, Elisa, Oliver and Lucas are going to university.
#One of them is going to London.
#Exactly one boy and one girl chose a university in a
#city with the same initial of their names.
#A boy is from Australia, the other studies Architecture.
#A girl goes to Cambridge, the other studies Medicine.
#Oliver studies Law or is from USA. He is not from South Africa.
#The student from Canada is either a history or will go to Oxford.
#The student from South Africa is going to Edinburgh or will study Law.
#
#What is the nationality of the history student?

# Predicates
#   university
#   nationality
#   subject
#   gender
#   name

##Objects
#	Student #1, Student #2,Student #3, Student #4

model = cp_model.CpModel()
students = ["Student #1",
            "Student #2",
            "Student #3",
            "Student #4",
            ]
universities = ["london", "cambridge", "oxford", "edinburgh"]
nationalities= ["Australia", "South Africa", "Canada", "USA"]
subjects = ["architecture", "medicine", "history", "law"]
genders = ["boy", "girl"]
names = ["Carol", "Elisa", "Oliver",  "Lucas"]


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, university, nationality, subject, gender, name):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.university_ = university
        self.nationality_ = nationality
        self.subject_ = subject
        self.gender_ = gender
        self.name_ = name
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        for student in students:
            print(" - " + student + ":")
            for university in universities:
                if self.Value(self.university_[student][university]):
                    print("    - ", university)
            for nationality in nationalities:
                if self.Value(self.nationality_[student][nationality]):
                    print("    - ", nationality)
            for subject in subjects:
                if self.Value(self.subject_[student][subject]):
                    print("    - ", subject)
            for gender in genders:
                if self.Value(self.gender_[student][gender]):
                    print("    - ", gender)
            for name in names:
                if self.Value(self.name_[student][name]):
                    print("    - ", name)

        print()

def main():
    model = cp_model.CpModel()

    student_university = {}
    for student in students:
        variables = {}
        for university in universities:
            variables[university] = model.NewBoolVar(student+university)
        student_university[student] = variables

    student_nationalities ={}
    for student in students:
        variables = {}
        for nationality in nationalities:
            variables[nationality] = model.NewBoolVar(student+nationality)
        student_nationalities[student] = variables

    student_subject = {}
    for student in students:
        variables = {}
        for subject in subjects:
            variables[subject] = model.NewBoolVar(student+subject)
        student_subject[student] = variables

    student_gender={}
    for student in students:
        variables = {}
        for gender in genders:
            variables[gender] = model.NewBoolVar(student+gender)
        student_gender[student] = variables

    student_name={}
    for student in students:
        variables = {}
        for name in names:
            variables[name] = model.NewBoolVar(student+name)
        student_name[student] = variables

    #every student has different property

    for i in range(4):
        for j in range(i+1,4):
            for k in range(4):
                model.AddBoolOr([
                        student_university[students[i]][universities[k]].Not(),
                        student_university[students[j]][universities[k]].Not()])
                model.AddBoolOr([student_nationalities[students[i]][nationalities[k]].Not(),
                                 student_nationalities[students[j]][nationalities[k]].Not()])
                model.AddBoolOr([student_subject[students[i]][subjects[k]].Not(),
                                 student_subject[students[j]][subjects[k]].Not()])
                model.AddBoolOr([student_name[students[i]][names[k]].Not(),
                                 student_name[students[j]][names[k]].Not()])
            for k in range(2):
                model.AddBoolOr([student_gender[students[i]][genders[k]].Not(),
                                 student_gender[students[j]][genders[k]].Not()])
    for student in students:
        # at least one property per student
        variables = []
        for university in universities:
            variables.append(student_university[student][university])
        model.AddBoolOr(variables)

        variables = []
        for nationality in nationalities:
            variables.append(student_nationalities[student][nationality])
        model.AddBoolOr(variables)

        variables = []
        for subject in subjects:
            variables.append(student_subject[student][subject])
        model.AddBoolOr(variables)

        variables = []
        for gender in genders:
            variables.append(student_gender[student][gender])
        model.AddBoolOr(variables)

        variables = []
        for name in names:
            variables.append(student_name[student][name])
        model.AddBoolOr(variables)

        # max one property per student
        for i in range(4):
            for j in range(i + 1, 4):
                model.AddBoolOr([
                    student_university[student][universities[i]].Not(),
                    student_university[student][universities[j]].Not()])
                model.AddBoolOr([
                    student_nationalities[student][nationalities[i]].Not(),
                    student_nationalities[student][nationalities[j]].Not()])
                model.AddBoolOr([
                    student_subject[student][subjects[i]].Not(),
                    student_subject[student][subjects[j]].Not()])
                model.AddBoolOr([
                    student_name[student][names[i]].Not(),
                    student_name[student][names[j]].Not()])
        for i in range(2):
            for j in range(i + 1,2):
                model.AddBoolOr([
                    student_gender[student][genders[i]].Not(),
                    student_gender[student][genders[j]].Not()])

#One of them is going to London.
#∀x ∀y ∀z ∀a: x!=y, x!=z, x!=a, y!=z , y!=a , z!=a:
	#university(x,london) => !university(y,london) ∧ !university(z,london) ∧ !university(a,london)
    other_students= list(students)
    other_students.remove(student)
    model.AddBoolAnd([student_university[other_students[0]]["london"].Not(),
                      student_university[other_students[1]]["london"].Not(),
                      student_university[other_students[2]]["london"].Not(),
                      ]).OnlyEnforceIf(student_university[student]["london"])
#Exactly one boy and one girl chose a university in a city with the same initial of their names.
#Exactly one boy and one girl chose a university in a city with the same initial of their names.
#∀x ∀y: x!=y:
#	gender(x, boy) ∧ gender(y,boy)∧ name(x,Oliver)∧ university(x,oxford)∧ name(y,Lucus) =>
#	!university(y, London)
#	gender(x, boy) ∧ gender(y,boy)∧ name(x,Lucus)∧ university(x,London)∧ name(y,Oliver) =>
#	!university(y, oxford)
#	gender(x, girl) ∧ gender(y,girl)∧ name(x,Elisa)∧ university(x,edinburgh)∧ name(y,Carol) =>
#	!university(y, cambridge)
#	gender(x, girl) ∧ gender(y,girl)∧ name(x,Carol)∧ university(x,cambridge)∧ name(y,Elisa) =>
#	!university(y, edinburgh)
    for other_student in other_students:
        model.AddBoolAnd([
            student_gender[student]["boy"], student_gender[other_student]["boy"], student_name[other_student]["Oliver"], student_university[other_student]["oxford"], student_name[student]["Lucas"]
        ]).OnlyEnforceIf(student_university[student]["london"].Not())
        model.AddBoolAnd([
            student_gender[student]["boy"], student_gender[other_student]["boy"], student_name[other_student]["Lucas"], student_university[other_student]["london"], student_name[student]["Oliver"]
        ]).OnlyEnforceIf(student_university[student]["oxford"].Not())
        model.AddBoolAnd([
            student_gender[student]["girl"], student_gender[other_student]["girl"], student_name[other_student]["Elisa"], student_university[other_student]["edinburgh"], student_name[student]["Carol"]
        ]).OnlyEnforceIf(student_university[student]["cambridge"].Not())
        model.AddBoolAnd([
            student_gender[student]["girl"], student_gender[other_student]["girl"], student_name[other_student]["Carol"], student_university[other_student]["cambridge"], student_name[student]["Elisa"]
        ]).OnlyEnforceIf(student_university[student]["edinburgh"].Not())
#A boy is from Australia, the other studies Architecture.
#∀x ∀y: x!=y:
#	gender(x, boy) ∧ gender(y,boy)∧ nationality(x,Australia) =>
#	subject(y,architecture)
        model.AddBoolAnd([
            student_gender[student]["boy"], student_gender[other_student]["boy"], student_nationalities[student]["Australia"]
        ]).OnlyEnforceIf(student_subject[other_student]["architecture"])
#A girl goes to Cambridge, the other studies Medicine.
#∀x ∀y: x!=y:
#	gender(x, girl) ∧ gender(y,girl)∧ university(x,cambridge) =>
#	subject(y,medicine)
        model.AddBoolAnd([
            student_gender[student]["girl"], student_gender[other_student]["girl"], student_university[student]["cambridge"]
        ]).OnlyEnforceIf(student_subject[other_student]["medicine"])
#Oliver studies Law or is from USA. He is not from South Africa.
#∀x:
#		name(x,Oliver) => (!subject(x, medicine) ∧  nationality(x, USA)) V (subject(x, medicine) ∧  !nationality(x, USA))
#		name(x,Oliver) => !nationality(x, South Africa)
        model.AddBoolXOr([
            student_nationalities[student]["USA"],
            student_subject[student]["medicine"]
        ]).OnlyEnforceIf(student_name[student]["Oliver"])
        model.AddBoolAnd([
            student_nationalities[student]["South Africa"].Not()
        ]).OnlyEnforceIf(student_name[student]["Oliver"])
#The student from Canada is either a history or will go to Oxford.
#∀x:
#		nationality(x,Canada) => (!subject(x, history) ∧  university(x, Oxford)) V (subject(x, history) ∧  !nationality(x, Oxford))
        model.AddBoolXOr([
            student_subject[student]["history"],
            student_university[student]["oxford"]
        ]).OnlyEnforceIf(student_nationalities[student]["Canada"])
#The student from South Africa is going to Edinburgh or will study Law.
#∀x:
#		nationality(x,South Africa) => (!subject(x, law) ∧  university(x, Edinburgh)) V (subject(x, law) ∧  !nationality(x, Edinburgh))
        model.AddBoolXOr([
            student_subject[student]["law"],
            student_university[student]["edinburgh"]
        ]).OnlyEnforceIf(student_nationalities[student]["South Africa"])
    
    solver = cp_model.CpSolver()    
    solver.SearchForAllSolutions(model, SolutionPrinter(student_university, student_nationalities, student_subject, student_gender, student_name))
    
    for student in students:
        if solver.Value(student_subject[student]["history"]):
            for nationality in nationalities:
                if solver.Value(student_nationalities[student][nationality]):
                    print("The nationality of the history student is"+nationality+".")

main()
