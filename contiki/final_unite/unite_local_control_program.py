
__author__ = "Kostas Kolomvatsos"
__copyright__ = "Copyright (c) 2015, Department of Informatics and Telecommunications, UoA"
__version__ = "0.1.0"
__email__ = "kostasks@di.uoa.gr"


#Definition of Local Control Program
def my_local_control_program(controller):
    #do all needed imports here!!!
    import time
    import datetime
    import gevent
    from libunite.fuzzy import calculate_fuzzy
    from libunite.algorithms import cycle_predictor, moving_average, round_average, seasonal_naive_predictor, \
                       helper_exponential, exponential, drift, extrapolation,geometric_moving_average, \
                       triangular_moving_average, polynomial, parabolic_average_predictor, linear_regression, \
                       linear_prediction, fusion, KDE
    MAX_THRESHOLD = 20
    MIN_THRESHOLD = 0
    NUMBER_MEASUREMENTS = 6

    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))
        result = controller.radio.iface("lowpan0").get_channel()
        print(("{} Channel is: {}".format(datetime.datetime.now(), result)))
        controller.send_upstream({"myChannel":result})

    def calculate_percentage(value):
        return ((abs(value) - MIN_THRESHOLD)/(MAX_THRESHOLD-MIN_THRESHOLD)) * 10


    #control loop
    print(("\nLocal Control Program - Name: {}, Id: {} - STARTED".format(controller.name, controller.id)))
    print("UNITE")
    starting_list = [ ]
    measurements = []
    threashold = 0.7
    prediction_results = {}
    t = 0
    expected_value_a = 0
    last_value=0
    b_last_value = 0

    while not controller.is_stopped():
        result = controller.radio.iface("lowpan0").get_measurements(["IEEE802154_measurement_macStats"])
        current_value = int(result['IEEE802154_measurement_macStats'][8]) + int(result['IEEE802154_measurement_macStats'][7])
        measurements.append(current_value - last_value)
        last_value = current_value
        gevent.sleep(0.5)

        # calculate Forecasting Values
        if len(measurements) > NUMBER_MEASUREMENTS:
            measurements.pop(0)
            prediction_results['cycle'] =  cycle_predictor(measurements, 3)
            prediction_results['moving_average'] = moving_average(measurements, 3)
            prediction_results['round_average'] = round_average(measurements, 3)
            prediction_results['seasonal_naive_predictor'] = seasonal_naive_predictor(measurements, 2)
            prediction_results['exponential'] = exponential(measurements, 0.6, 2)
            prediction_results['drift'] = drift(measurements)
            prediction_results['extrapolation'] = extrapolation(measurements)
            prediction_results['geometric_moving_average'] = geometric_moving_average(measurements, 4)
            prediction_results['triangular_moving_average'] = triangular_moving_average(measurements, 4)
            prediction_results['parabolic_average_predictor'] = parabolic_average_predictor(measurements, 0.04, 0.22)
            prediction_results['linear_regression'] = linear_regression(measurements)
            prediction_results['linear_prediction'] = linear_prediction(measurements)
            prediction_results['polynomial'] = polynomial(measurements)
            # *********************************************
            results_table = list(prediction_results.values())
            after_fusion = fusion(results_table)
            t += 1
            expected_value_a = KDE(t, expected_value_a, measurements[-1])
            PoV = calculate_fuzzy(calculate_percentage(after_fusion), calculate_percentage(expected_value_a), calculate_percentage(measurements[-1]))
            print("PoV --> {}".format(PoV))
            if PoV > threashold:
                val = controller.blocking(True).net.iface("lowpan0").get_parameters_net(['app_send_interval'])
                current_value = int(val['app_send_interval']) - 1
                if current_value > 0:
                    val = controller.blocking(True).net.iface("lowpan0").set_parameters_net({'app_send_interval': current_value})
                    print(val)
            controller.send_upstream({"PoV": PoV})
            while not controller.is_stopped():
                msg = controller.recv(timeout=7)
                if msg:
                    dif = msg["decrease_payload"]
                    val = controller.blocking(True).net.iface("lowpan0").get_parameters_net(['app_payload_length'])
                    current_value = int(val['app_payload_length'])
                    newValue = current_value - dif
                    if newValue > 6:
                        val = controller.blocking(True).net.iface("lowpan0").set_parameters_net({'app_payload_length': newValue})
                        print(val)

                else:
                    print(("{} Waiting for message".format(datetime.datetime.now())))


    print(("Local Control Program - Name: {}, Id: {} - STOPPED".format(controller.name, controller.id)))
