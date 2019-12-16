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
# F. Answer the question how much of each product each factory should order from each supplier [1 point] and how much
# this order will cost including shipping [1 point].
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
            print("--","Total Cost:", factories[factory][supplier]['total'])
    print("")
def G_factory_production_and_cost(materials_sent_to_each_factory, products_sent_from_factories):
    factory_materials_cost = {}
    print("G Product Orders")
    for key, mnbef_value in materials_sent_to_each_factory.items():
        supplier = key[0]
        material = key[1]
        factory = key[2]
        if mnbef_value is not None:
            if factory not in factory_materials_cost:
                factory_materials_cost[factory] = {}
            if material not in factory_materials_cost[factory]:
                factory_materials_cost[factory][material] = {}
                factory_materials_cost[factory][material]['amt'] = 0
                factory_materials_cost[factory][material]['total cost'] = 0
            factory_materials_cost[factory][material]['amt'] += mnbef_value.solution_value()
            factory_materials_cost[factory][material]['total cost'] += mnbef_value.solution_value()* (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier])

    factory_production_amt_cost = {}
    for psff_key, psff_value in products_sent_from_factories.items():
        factory = psff_key[0]
        product = psff_key[1]
        customer = psff_key[2]
        if psff_value is not None:
            if factory not in factory_production_amt_cost:
                factory_production_amt_cost[factory] = {}
            if product not in factory_production_amt_cost[factory]:
                factory_production_amt_cost[factory][product] = {}
                factory_production_amt_cost[factory][product]['amt'] = 0
                factory_production_amt_cost[factory][product]['production cost'] = 0
            factory_production_amt_cost[factory][product]['amt'] += psff_value.solution_value()
            factory_production_amt_cost[factory][product]['production cost'] += psff_value.solution_value() * (production_cost[factory][product])

    total_cost_to_each_factory ={}
    for factory in sorted(factory_production_amt_cost.keys()):
        print("-",factory)
        if factory not in total_cost_to_each_factory:
            total_cost_to_each_factory[factory] = 0
        for product in sorted(factory_production_amt_cost[factory].keys()):
            if factory_production_amt_cost[factory][product]['amt'] != 0:
                print("--", product, "amt:", factory_production_amt_cost[factory][product]['amt'])
                total_cost_to_each_factory[factory] += factory_production_amt_cost[factory][product]['production cost']
        for material in sorted(factory_materials_cost[factory].keys()):
            if factory_materials_cost[factory][material]['amt'] != 0:
                total_cost_to_each_factory[factory] += factory_materials_cost[factory][material]['total cost']
        print("--","Total Cost",total_cost_to_each_factory[factory])
    print("")



def H_factory_production_and_cost(materials_sent_to_each_factory, products_sent_from_factories):
    factory_materials_cost = {}
    print("H Factory Delivery")
    for key, mnbef_value in materials_sent_to_each_factory.items():
        supplier = key[0]
        material = key[1]
        factory = key[2]
        if mnbef_value is not None:
            if factory not in factory_materials_cost:
                factory_materials_cost[factory] = {}
            if material not in factory_materials_cost[factory]:
                factory_materials_cost[factory][material] = {}
                factory_materials_cost[factory][material]['amt'] = 0
                factory_materials_cost[factory][material]['cost'] = 0
            factory_materials_cost[factory][material]['amt'] += mnbef_value.solution_value()
            factory_materials_cost[factory][material]['cost'] += mnbef_value.solution_value()* (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier])

    factory_production_amt_cost = {}
    for psff_key, psff_value in products_sent_from_factories.items():
        factory = psff_key[0]
        product = psff_key[1]
        customer = psff_key[2]
        if psff_value is not None:
            if factory not in factory_production_amt_cost:
                factory_production_amt_cost[factory] = {}
            if product not in factory_production_amt_cost[factory]:
                factory_production_amt_cost[factory][product] = {}
                factory_production_amt_cost[factory][product]['amt'] = 0
                factory_production_amt_cost[factory][product]['production cost'] = 0
            factory_production_amt_cost[factory][product]['amt'] += psff_value.solution_value()
            factory_production_amt_cost[factory][product]['production cost'] += psff_value.solution_value() * (production_cost[factory][product])

    factory_cost_per_product_unit ={}
    for factory in sorted(factory_production_amt_cost.keys()):
        if factory not in factory_cost_per_product_unit:
            factory_cost_per_product_unit[factory] = {}
        for product in sorted(factory_production_amt_cost[factory].keys()):
            if product not in factory_cost_per_product_unit[factory]:
                factory_cost_per_product_unit[factory][product] = factory_production_amt_cost[factory][product]['production cost'] / factory_production_amt_cost[factory][product]['amt']
            for material in materials:
                if not pd.isna(product_requirements[material][product]):
                    material_per_unit_cost = factory_materials_cost[factory][material]['cost'] / factory_materials_cost[factory][material]['amt']
                    amount_of_materials = product_requirements[material][product] * factory_production_amt_cost[factory][product]['amt']
                    cost_of_materials_used = amount_of_materials * material_per_unit_cost
                    cost_of_materials_used_per_product = cost_of_materials_used * factory_production_amt_cost[factory][product]['amt']
                    factory_cost_per_product_unit[factory][product] += cost_of_materials_used_per_product
    customer_order_per_factory = {}
    for psff_key, psff_value in products_sent_from_factories.items():
        factory = psff_key[0]
        product = psff_key[1]
        customer = psff_key[2]
        if psff_value is not None and psff_value.solution_value() !=0:
            if customer not in customer_order_per_factory:
                customer_order_per_factory[customer] = {}
            if product not in customer_order_per_factory[customer]:
                customer_order_per_factory[customer][product] = {}
            if factory not in customer_order_per_factory[customer][product]:
                customer_order_per_factory[customer][product][factory] = {}
            customer_order_per_factory[customer][product][factory]['amt'] = psff_value.solution_value()
            shipping_cost = shipping_costs[customer][factory] * customer_order_per_factory[customer][product][factory]['amt']
            cost_of_goods = factory_cost_per_product_unit[factory][product] * customer_order_per_factory[customer][product][factory]['amt']
            customer_order_per_factory[customer][product][factory]['cost']= cost_of_goods + shipping_cost

    for customer in sorted(customer_order_per_factory.keys()):
        print(customer)
        for product in sorted(customer_order_per_factory[customer].keys()):
            print('-',product)
            total_product_cost = 0
            for factory in sorted(customer_order_per_factory[customer][product].keys()):
                print("--", factory, "amt:", customer_order_per_factory[customer][product][factory]['amt'],
                      "cost:", customer_order_per_factory[customer][product][factory]['cost']
                      )
                total_product_cost += customer_order_per_factory[customer][product][factory]['cost']
            print("-","Total Cost",total_product_cost)

    print('')
    print('')
    print('')

def I_factory_production_and_cost(materials_sent_to_each_factory, products_sent_from_factories):
    factory_materials_cost = {}
    print("I Cost Per Product Unit For Each Customer")
    for key, mnbef_value in materials_sent_to_each_factory.items():
        supplier = key[0]
        material = key[1]
        factory = key[2]
        if mnbef_value is not None:
            if factory not in factory_materials_cost:
                factory_materials_cost[factory] = {}
            if material not in factory_materials_cost[factory]:
                factory_materials_cost[factory][material] = {}
                factory_materials_cost[factory][material]['amt'] = 0
                factory_materials_cost[factory][material]['cost'] = 0
            factory_materials_cost[factory][material]['amt'] += mnbef_value.solution_value()
            factory_materials_cost[factory][material]['cost'] += mnbef_value.solution_value()* (raw_material_costs[material][supplier] + raw_material_shipping[factory][supplier])

    factory_production_amt_cost = {}
    for psff_key, psff_value in products_sent_from_factories.items():
        factory = psff_key[0]
        product = psff_key[1]
        customer = psff_key[2]
        if psff_value is not None:
            if factory not in factory_production_amt_cost:
                factory_production_amt_cost[factory] = {}
            if product not in factory_production_amt_cost[factory]:
                factory_production_amt_cost[factory][product] = {}
                factory_production_amt_cost[factory][product]['amt'] = 0
                factory_production_amt_cost[factory][product]['production cost'] = 0
            factory_production_amt_cost[factory][product]['amt'] += psff_value.solution_value()
            factory_production_amt_cost[factory][product]['production cost'] += psff_value.solution_value() * (production_cost[factory][product])

    factory_cost_per_product_unit ={}
    for factory in sorted(factory_production_amt_cost.keys()):
        if factory not in factory_cost_per_product_unit:
            factory_cost_per_product_unit[factory] = {}
        for product in sorted(factory_production_amt_cost[factory].keys()):
            if product not in factory_cost_per_product_unit[factory]:
                factory_cost_per_product_unit[factory][product] = factory_production_amt_cost[factory][product]['production cost'] / factory_production_amt_cost[factory][product]['amt']
            for material in materials:
                if not pd.isna(product_requirements[material][product]):
                    material_per_unit_cost = factory_materials_cost[factory][material]['cost'] / factory_materials_cost[factory][material]['amt']
                    amount_of_materials = product_requirements[material][product] * factory_production_amt_cost[factory][product]['amt']
                    cost_of_materials_used = amount_of_materials * material_per_unit_cost
                    cost_of_materials_used_per_product = cost_of_materials_used * factory_production_amt_cost[factory][product]['amt']
                    factory_cost_per_product_unit[factory][product] += cost_of_materials_used_per_product
    customer_order_per_factory = {}
    for psff_key, psff_value in products_sent_from_factories.items():
        factory = psff_key[0]
        product = psff_key[1]
        customer = psff_key[2]
        if psff_value is not None and psff_value.solution_value() != 0:
            if customer not in customer_order_per_factory:
                customer_order_per_factory[customer] = {}
            if product not in customer_order_per_factory[customer]:
                customer_order_per_factory[customer][product] = {}
            if factory not in customer_order_per_factory[customer][product]:
                customer_order_per_factory[customer][product][factory] = {}
            customer_order_per_factory[customer][product][factory]['amt'] = psff_value.solution_value()
            shipping_cost = shipping_costs[customer][factory] * customer_order_per_factory[customer][product][factory]['amt']
            cost_of_goods = factory_cost_per_product_unit[factory][product] * customer_order_per_factory[customer][product][factory]['amt']
            customer_order_per_factory[customer][product][factory]['cost'] = cost_of_goods + shipping_cost
    customer_total_order_cost_per_product ={}
    for customer in customer_order_per_factory.keys():
        if customer not in customer_total_order_cost_per_product:
            customer_total_order_cost_per_product[customer] = {}
        for product in customer_order_per_factory[customer].keys():
            if product not in customer_total_order_cost_per_product[customer]:
                customer_total_order_cost_per_product[customer][product] = {}
                customer_total_order_cost_per_product[customer][product]['amt'] = 0
                customer_total_order_cost_per_product[customer][product]['cost'] = 0
            for factory in customer_order_per_factory[customer][product].keys():
                customer_total_order_cost_per_product[customer][product]['amt'] +=  customer_order_per_factory[customer][product][factory]['amt']
                customer_total_order_cost_per_product[customer][product]['cost'] += \
                customer_order_per_factory[customer][product][factory]['cost']

    for customer in sorted(customer_total_order_cost_per_product.keys()):
        print(customer)
        for product in sorted(customer_total_order_cost_per_product[customer].keys()):
            print("--", product, "cost per unit:", customer_total_order_cost_per_product[customer][product]['cost']/customer_total_order_cost_per_product[customer][product]['amt'])
    print('')
    print('')
    print('')




if status == solver.OPTIMAL:
    print("Optimal Solution")
    F_factory_material_orders(materials_sent_to_each_factory)
    G_factory_production_and_cost(materials_sent_to_each_factory,products_sent_from_factories)
    H_factory_production_and_cost(materials_sent_to_each_factory, products_sent_from_factories)
    I_factory_production_and_cost(materials_sent_to_each_factory, products_sent_from_factories)
else:  # No optimal solution was found.
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')