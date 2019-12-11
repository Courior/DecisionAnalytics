import pandas as pd
from ortools.linear_solver import pywraplp

supplier_stock = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Supplier stock', index_col=0)
print(supplier_stock)

raw_material_costs = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Raw material costs', index_col=0)
print(raw_material_costs)

raw_material_shipping = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Raw material shipping', index_col=0)
print(raw_material_shipping)

product_requirements = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Product requirements', index_col=0)
print(product_requirements)

production_capacity = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Production capacity', index_col=0)
print(production_capacity)

production_cost = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Production cost', index_col=0)
print(production_cost)

customer_demand = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Customer demand', index_col=0)
print(customer_demand)

shipping_costs = pd.read_excel('Assignment_DA_2_a_data.xlsx', 'Shipping costs', index_col=0)
print(shipping_costs)

# Decision Variables
# Materials sent from supplier to each factory
# Products sent from Factory to each Customer

# Constraints
# Suppliers Stock of each Material
# Production Capacity of each Factory
# Factories only need materials Required for the products they are creating
# Products Demanded by each customer

# Cost Function
# Raw Material Cost of materials from each supplier
# Raw Material shipping cost to each Factory
# Production Cost of product created in each factory
# Shipping Cost from factory to customer

suppliers = set(supplier_stock.index)
customers = set(customer_demand.columns)
factories = set(shipping_costs.index)
products = set(production_capacity.index)
materials = set(supplier_stock.columns)

print(suppliers)
print(customers)
print(products)
print(materials)

## Simple Version with only production cost per factory and consumer need

solver = pywraplp.Solver('LPWrapper', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

# Materials sent from supplier to each factory
#supplies_to_factory = {}
#for supplier in suppliers:
    #for material in materials:
        #if not pd.isna(supplier_stock[material][supplier]):
            #for factory in factories:
                #supplies_to_factory[(supplier, material, factory)] = solver.NumVar(0, solver.infinity(),
                                                                       #supplier + "_" + material + "_" + factory)
#print(supplies_to_factory)

# Products sent from factory to each
#for factory in factories:

# simplify problem to Products sent from factories to consumers and shipping costs

# products produced by factories and sent to users
products_sent_from_factories = {}
for factory in factories:
    for product in products:
        if not pd.isna(production_capacity[factory][product]):
            c = solver.Constraint(0, float(production_capacity[factory][product]))
        for customer in customers:
            if not pd.isna(production_capacity[factory][product]):
                products_sent_from_factories[(factory, product, customer)] = solver.NumVar(0, solver.infinity(),
                                                                                           factory + "_" + product + "_"
                                                                                           + customer)
            else:
                products_sent_from_factories[(factory, product, customer)] = None

for customer in customers:
    for product in products:
        if not pd.isna(customer_demand[customer][product]):
            c = solver.Constraint(float(customer_demand[customer][product]), solver.infinity())
            for factory in factories:
                if products_sent_from_factories[(factory, product, customer)] is not None :
                    c.SetCoefficient(products_sent_from_factories[(factory, product, customer)],
                                     float(customer_demand[customer][product]))

cost = solver.Objective()
for customer in customers:
    for product in products:
        for factory in factories:
            if products_sent_from_factories[(factory, product, customer)] is not None :
                cost.SetCoefficient(products_sent_from_factories[(factory, product, customer)],
                                    float(shipping_costs[customer][factory]) +
                                    float(production_cost[factory][product]))


# Materials sent from supplier to each factory
def Materials():
    materials_sent_to_factories = {}

    for supplier in suppliers:
        for material in materials:
            if not pd.isna(supplier_stock[material][supplier]):
                c = solver.Constraint(0, float(supplier_stock[material][supplier]))
            for factory in factories:
                if not pd.isna(supplier_stock[material][supplier]):
                    materials_sent_to_factories[(supplier, material)][factory] = solver.NumVar(0, solver.infinity(),
                                                                                               supplier + "_" + material + "_"
                                                                                               + factory)
                else:
                    materials_sent_to_factories[(supplier, material)][factory] = None


cost.SetMinimization()
status = solver.Solve()
if status == solver.OPTIMAL:
    print("Optimal Solution")
    product_cost_per_customer = {}
    for key, value in products_sent_from_factories.items():
        factory = key[0]
        product = key[1]
        customer = key[2]
        if value is not None:
            print(key, value.solution_value(), value.solution_value() *
                  (
                          shipping_costs[customer][factory] + production_cost[factory][product])
                  )
else:  # No optimal solution was found.
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')