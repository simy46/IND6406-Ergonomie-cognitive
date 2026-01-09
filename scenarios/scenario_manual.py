def run_manual_mode(context):
    vehicle = context["vehicle"]
    wheel = context["wheel"]

    control = wheel.get_control()
    vehicle.apply_control(control)