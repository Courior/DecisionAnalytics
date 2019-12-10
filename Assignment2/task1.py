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
# Products Produced by Each Factory
# Products sent from Factory to each Customer

# Constraints
# Suppliers Stock of each Material
# Production Capacity of each Factory
# Materials Needed for each Factory to create Products
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

production = {}

for factory in factories:
    for product in products:
        production[(factory, product)] = solver.NumVar(0, solver.infinity(), factory + "_" + product)

delivery = {}
