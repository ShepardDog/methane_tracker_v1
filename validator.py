def validate_time_horizon(time:int):
    #time can not be negative 
    if time < 0:
        raise ValueError(f"time_horizon must be positive, got {time}")
    return

def validate_emission_adjustement_value(emission_adjustement:float):
    if emission_adjustement < -1:
        raise ValueError(f"Adjustement must be >= -1, got {emission_adjustement}")
    return

