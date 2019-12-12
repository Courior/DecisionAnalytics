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
        c = None
        if not pd.isna(production_capacity[factory][product]):
            c = solver.Constraint(0, float(production_capacity[factory][product]))
        for customer in customers:
            if not pd.isna(production_capacity[factory][product]):
                products_sent_from_factories[(factory, product, customer)] = solver.NumVar(0, solver.infinity(),
                                                                                           factory + "_" + product + "_"
                                                                                           + customer)
                # Production Capacity per factory coefficient
                c.SetCoefficient(products_sent_from_factories[(factory, product, customer)], 1)
            else:
                products_sent_from_factories[(factory, product, customer)] = None

for customer in customers:
    for product in products:
        if not pd.isna(customer_demand[customer][product]):
            c = solver.Constraint(float(customer_demand[customer][product]), solver.infinity())
            for factory in factories:
                if products_sent_from_factories[(factory, product, customer)] is not None:
                    c.SetCoefficient(products_sent_from_factories[(factory, product, customer)],1)


cost = solver.Objective()
for customer in customers:
    for product in products:
        for factory in factories:
            if products_sent_from_factories[(factory, product, customer)] is not None :
                cost.SetCoefficient(products_sent_from_factories[(factory, product, customer)],
                                    float(shipping_costs[customer][factory]) +
                                    float(production_cost[factory][product]))



# Materials sent from supplier to each factory
materials_sent_to_each_factory = {}
for supplier in suppliers:
    c = None
    for material in materials:
        if not pd.isna(supplier_stock[material][supplier]):
            c = solver.Constraint(0, float(supplier_stock[material][supplier]))
        for factory in factories:
            if not pd.isna(supplier_stock[material][supplier]):
                materials_sent_to_each_factory[(supplier, material, factory)] = solver.NumVar(0, solver.infinity(),
                                                                                              supplier + "_" + material + "_"
                                                                                              + factory)
                # Supplier stock Coefficient
                c.SetCoefficient(materials_sent_to_each_factory[(supplier, material, factory)], 1)
            else:
                materials_sent_to_each_factory[(supplier, material, factory)] = None

for factory in factories:
    c = None
    for material in materials:
        c = solver.Constraint(0, 0)
        for supplier in suppliers:
            if materials_sent_to_each_factory[(supplier, material, factory)] is not None:
                c.SetCoefficient(materials_sent_to_each_factory[(supplier, material, factory)], 1)
                for product in products:
                    if not pd.isna(production_capacity[factory][product]) and not pd.isna(product_requirements[material][product]):
                        for customer in customers:
                            if products_sent_from_factories[(factory, product, customer)] is not None:
                                c.SetCoefficient(products_sent_from_factories[(factory, product, customer)],
                                                 -product_requirements[material][product])



for mnbef_key, mnbef_value in materials_sent_to_each_factory.items():
    supplier = mnbef_key[0]
    material = mnbef_key[1]
    factory = mnbef_key[2]
    if mnbef_value is not None:
        cost.SetCoefficient(mnbef_value,
                            float(raw_material_costs[material][supplier]) +
                            float(raw_material_shipping[factory][supplier]))

cost.SetMinimization()



status = solver.Solve()

def F_factory_material_orders(materials_sent_to_each_factory):
    factories = {}
    print("F Material Orders")
    for key, mnbef_value in materials_sent_to_each_factory.items():
        supplier = key[0]
        material = key[1]
        factory = key[2]
        if mnbef_value is not None:
            if factory not in factories:
                factories[factory] = {}
            if supplier not in factories[factory]:
                factories[factory][supplier] = {}
                factories[factory][supplier]['total'] = 0
            if material not in factories[factory][supplier]:
                factories[factory][supplier][material] = {}
            factories[factory][supplier][material]['amt'] = mnbef_value.solution_value()
            factories[factory][supplier][material]['cost'] = mnbef_value.solution_value()* (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier])
            factories[factory][supplier]['total'] += factories[factory][supplier][material]['cost']

    for factory in sorted(factories.keys()):
        print(factory)
        for supplier in sorted(factories[factory].keys()):
            print("-",supplier)
            for material in sorted(factories[factory][supplier].keys()):
                if material != "total" and factories[factory][supplier][material]['amt'] != 0:
                    print("--", material, "amt:", factories[factory][supplier][material]['amt'], "cost", factories[factory][supplier][material]['cost'])
            print("Total Cost:", factories[factory][supplier]['total'])
        print('')
        print('')






if status == solver.OPTIMAL:
    print("Optimal Solution")
    product_cost_per_customer = {}
    for key, value in products_sent_from_factories.items():
        factory = key[0]
        product = key[1]
        customer = key[2]
        if value is not None:
            if value.solution_value() != 0.0:
                print(key, value.solution_value(), value.solution_value() *
                      (
                              shipping_costs[customer][factory] + production_cost[factory][product])
                      )
    for key, mnbef_value in materials_sent_to_each_factory.items():
        supplier = key[0]
        material = key[1]
        factory = key[2]
        if mnbef_value is not None:
            if mnbef_value.solution_value() != 0.0:
                material_value = mnbef_value.solution_value() * (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier])
                print(key, mnbef_value.solution_value(), material_value)
    F_factory_material_orders(materials_sent_to_each_factory)
else:  # No optimal solution was found.
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')