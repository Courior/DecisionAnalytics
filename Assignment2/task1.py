import pandas as pd

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