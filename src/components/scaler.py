
from components.configurator import Configurator

class Scaler:
    """
    Scaler class will scale the system to a new configuration.
    """
    def __init__(self, starting_mcl: int, configurator: Configurator ) -> None:
        self.mcl = starting_mcl
        self.configurator = configurator


    def process_request(self, target_mcl) -> None:
        """
        Process a scaling request.
    
        Arguments
        -----------
        target_mcl -> the target mcl to reach 
        """
        config = self.configurator.calculate_configuration(target_mcl)

        # TODO: Apply the configuration
        new_mcl = self.apply_configuration(config)

        # TODO: Return the new mcl 
        return new_mcl


    def apply_configuration(self, configuration_file) -> None:
        """
        Apply the new configuration.

        Arguments
        -----------
        configuration_file -> the target mcl to reach 
        """
        pass