from components.configurator import Configurator

class SysScaler:
    """
    SysScaler class will scale the system to a new configuration.
    """
    def __init__(self, starting_mcl: int, configurator: Configurator) -> None:
        self.mcl = starting_mcl
        self.configurator = configurator

    def get_mcl(self) -> int:
        """
        Return the current mcl of the system.
        """
        return self.mcl

    def process_request(self, target_mcl) -> int:
        """
        Process a scaling request.
    
        Arguments
        -----------
        target_mcl -> the target mcl to reach 
        """
        config = self.configurator.calculate_configuration(target_mcl)

        # TODO: Apply the configuration
        self.mcl = self.apply_configuration(config)

        # TODO: Return the new mcl 
        return self.mcl

    def apply_configuration(self, configuration_file) -> None:
        """
        Apply the new configuration.

        Arguments
        -----------
        configuration_file -> the target mcl to reach 
        """
        pass