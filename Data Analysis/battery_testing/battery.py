from typing import Self


class Battery:
    def __init__(self, power_capacity, energy_capacity,efficiency=1):
        self.power_capacity = power_capacity  # in MW
        self.energy_capacity = energy_capacity  # in MWh
        self.state_of_charge = 0  # Initial state of charge (SOC)
        self.efficiency=efficiency
        self.percentage=0

    def charge(self, power):
        """
        Charge the battery at the specified power rate.

        Args:
            power (float): Power rate of charging in MW.
        """
        # Calculate the maximum charge allowed based on current SOC and energy capacity
        max_charge = self.energy_capacity - self.state_of_charge

        # Calculate the actual charge based on power capacity and available energy
        actual_charge = min(power, self.power_capacity, max_charge)

        # Update the state of charge
        
        self.state_of_charge += (actual_charge*self.efficiency)
        
        return actual_charge  # Return the actual charge performed

    def discharge(self, power):
        """
        Discharge the battery at the specified power rate.

        Args:
            power (float): Power rate of discharging in MW.
        """
        # Calculate the maximum discharge allowed based on current SOC
        max_discharge = self.state_of_charge

        # Calculate the actual discharge based on power capacity and available energy
        actual_discharge = min(power, self.power_capacity, max_discharge)

        # Update the state of charge
        self.state_of_charge -= (actual_discharge*self.efficiency)

        return actual_discharge  # Return the actual discharge performed
    
    def get_charge(self):
        """
        Get the current state of charge of the battery.

        Returns:
            float: The current state of charge.
        """
        
        return self.state_of_charge
    