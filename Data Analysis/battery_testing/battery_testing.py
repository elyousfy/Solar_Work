from battery import Battery


Battery_10MW_100MWh = Battery(power_capacity=10, energy_capacity=100)


for i in range(0,10):
    Battery_10MW_100MWh.charge(power=3.5)
    print(f"state of charge of battery {Battery_10MW_100MWh.get_charge()}")

for i in range(0,10):
    Battery_10MW_100MWh.discharge(power=100)
    print(f"state of charge of battery {Battery_10MW_100MWh.get_charge()}")
    