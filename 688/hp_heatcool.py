'''
Created on Jan 5, 2021

@author: Carter.Freeze
'''

import logging.config
import time
import sys
import os
import multiprocessing

sys.path.append(os.getcwd())

from multiprocessing import Process, Queue, Event
from SystemConfig.logging_configs import LoggingConfigs
from econet_driver.econet_constants import ArcFlags, NetworkAddresses, ReturnCodes, SystemValues
from econet_driver.econet_utilities import econet_read_write_process, logging_process,\
    pre_parse_util, end_process, read_obj, read_obj_compare, write_obj
from SystemConfig.sys_setup import sys_setup
from SystemConfig.test_case_logger import TestCaseLogger
from econet_driver.econet_exceptions import ConfigError, CommPortError, ReadObjError, ValueCompareError,\
    WriteObjError, TerminateError
from econet_driver.econet_system_config import ConfigFile


TEST_CASE_NAME = "m1ah_heatCool"
TEST_CASE_VERSION = "01.00.00"

#use the first def in case of prompt user needed
#def tc_xxxx(bench_test, log_config, cmd_msg_que, response_que, econet_write_obj_que, econet_read_obj_que, kill_que, prompt_que):
def m1ah_heatCool(bench_test, log_config, log_lock, response_que, econet_write_obj_que, econet_read_obj_que, kill_que):
    """
     Test Case Requirement:
    SSR-12/SSR-19/SR-50 - Legacy Basic Functionality (Coolling and Heat-Pump)

    Test Case Purpose:
        The purpose of this test case is to test the unit low and high cooling and heating call.

         Monitor the following Objects on the EcoNet monitor:
            modeldata.coolhcfm, modeldata.hpmphcfm, modeldata.hpmplcfm, modeldata.coollcfm, TE_IMC_1, TE_IMC_2, W1DISCIN, W2DISCIN 
            1.) Model Data Settings
            Test Setup:
            Low Cool call:
            Give the unit a low cool call by applying 24 VAC to the Y1 (TE_IMC_1) terminal
            Test Verification:
            Validate that the unit cfm reaches the value of modeldata.coollcfm
            High Cool call:
            Give the unit a high cool call by applying 24 VAC to the Y1 & Y2 (TE_IMC_1, TE_IMC_2) terminals
            Test Verification:
            Validate that the unit cfm reaches the value of modeldata.coolhcfm
            Low Heat call:
            Give the unit a low heat call by applying 24 VAC to the (Y1&B)  terminal
            Test Verification:
            Validate that the unit cfm reaches the value of modeldata.hpmplcfm
            High Heat call:
            Give the unit a high heat call by writing Y1 (TE_IMC_1), Y2 (TE_IMC_2), and B (TE_IMC_4) to 1.
            Test Verification:
            Validate that the unit cfm reaches the value of modeldata.hpmphcfm

    Args:
        bench_test: Boolean variable to run bench testing and not worry about system being present
        log_config: Logging configuration for this process
        log_lock: Lock for the logging thread
        response_que: Queue that will contain the response to be sent back to the queuing process.  
                      Also doubles as a queue that will return the return code from the test case. 
        econet_write_obj_que: Queue that will receive objects and values to write to the bus
        econet_read_obj_que:  Queue that will receive objects to read from the bus
        kill_que:  Queue that will receive signal to stop this process

    Returns:
        tuple (see error codes defined above)

    Objects used:
        Read: N/A
        Written: N/A

    User input required: No

    Error Injection: No

    Test Group: M1 Air Handler

    System Config:
        Indoor Unit: M1 Air Handler
        Outdoor Unit: RP2036
        Water Heater: HPWH1

    Raises:
        ConfigError
        ReadObjError
        WriteObjError
        ValueCompareError
        TerminateError

    """
    # Get a test case logger to log all entries
    tc_logger = TestCaseLogger(log_config, TEST_CASE_NAME)

    # Set the return code and create log entries for this test case
    tc_logger.log_entry(f'***** Executing test case \'{TEST_CASE_NAME}\'')
    if bench_test:
        tc_logger.log_entry("Bench Testing")
    
    # Set the return code to default to "GOOD" and only change it if there is a failure
    return_code = (TEST_CASE_NAME, ReturnCodes.ALL_GOOD[1], ReturnCodes.ALL_GOOD[2])
    
    # Get the filename that is executing and pass this as a parameter to the pre-parser.  The pre-parser will
    # parse the file and put the relevant data to the log file
    file_name = os.path.realpath(__file__)
    req_trace_csv_data = pre_parse_util(tc_logger, file_name)

    # Create the system configuration class, and populate it with values from the sys_config.ini
    system_config = ConfigFile(SystemValues.SYS_CONFIG_FILE)

    try:
        #Make sure that the test case is setup to run the specific system according to the test case header
        # sys_setup(tc_logger, response_que, econet_write_obj_que, econet_read_obj_que, system_config, file_name, True, bench_test)

        # Disabling comm with the CC for end process
        tc_logger.log_entry(f'Disabling communications with the control center')
        if not bench_test:
            tc_logger.log_entry(f"Writing STOPCOMM to {SystemValues.YES}")
            write_obj(tc_logger, response_que, econet_write_obj_que, "STOPCOMM", SystemValues.YES)
        
        #Grab Air Handler Model data
        tc_logger.log_entry(f"***** Collecting Model Data")
        modeldata = read_obj(tc_logger, response_que, econet_read_obj_que, 'MODLDATA', NetworkAddresses.ECONET_AIR_HANDLER)[1]

        #Cooling Section
        #Low call
        # This is going to be a legacy call. We use the ARCBOARD to apply 24VAC to the correct terminal
        tc_logger.log_entry(f'****** Applying Signal to Y1 terminal')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_1", ArcFlags.RELAY_CLOSED, NetworkAddresses.ECONET_ARC_BOARD)

        tc_logger.log_entry('***** Allowing the system to stabilize for 5 minutes')
        if not bench_test:
            time.sleep(2 * 60)

        tc_logger.log_entry(f'Checking unit CFM')
        if not bench_test:
            read_obj_compare(tc_logger, response_que, econet_read_obj_que, 'CFM_CURR', modeldata.coollcfm, 50, NetworkAddresses.ECONET_AIR_HANDLER)

        #High cool call
        # This is going to be a legacy call. We use the ARCBOARD to apply 24VAC to the correct terminal
        tc_logger.log_entry(f'****** Applying Signal to Y2 terminal')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_2", ArcFlags.RELAY_CLOSED, NetworkAddresses.ECONET_ARC_BOARD)

        tc_logger.log_entry('***** Allowing the system to stabilize for 5 minutes')
        if not bench_test:
            time.sleep(2 * 60)

        tc_logger.log_entry(f'Checking unit CFM')
        if not bench_test:
            read_obj_compare(tc_logger, response_que, econet_read_obj_que, 'CFM_CURR', modeldata.coolhcfm, 50, NetworkAddresses.ECONET_AIR_HANDLER)

        #Getting unit for next test
        tc_logger.log_entry(f'***** Resetting unit')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_1", ArcFlags.RELAY_OPEN, NetworkAddresses.ECONET_ARC_BOARD)
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_2", ArcFlags.RELAY_OPEN, NetworkAddresses.ECONET_ARC_BOARD)
            tc_logger.log_entry(f'Waiting 3 minutes for unit to shut down')
            time.sleep(3 * 60)
        
        #Heat-Pump
        #We set up the B terminal to put the system into heatpump mode
        tc_logger.log_entry(f'****** Applying Signal to B terminal')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_4", ArcFlags.RELAY_CLOSED, NetworkAddresses.ECONET_ARC_BOARD)

        #Low call
        # This is going to be a legacy call. We use the ARCBOARD to apply 24VAC to the correct terminal
        tc_logger.log_entry(f'****** Applying Signal to Y1 terminal')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_1", ArcFlags.RELAY_CLOSED, NetworkAddresses.ECONET_ARC_BOARD)

        tc_logger.log_entry('***** Allowing the system to stabilize for 5 minutes')
        if not bench_test:
            time.sleep(2 * 60)

        tc_logger.log_entry(f'Checking unit CFM')
        if not bench_test:
            read_obj_compare(tc_logger, response_que, econet_read_obj_que, 'CFM_CURR', modeldata.hpmplcfm, SystemValues.AIRFLOW_TOLERANCE, NetworkAddresses.ECONET_AIR_HANDLER)

        #High cool call
        # This is going to be a legacy call. We use the ARCBOARD to apply 24VAC to the correct terminal
        tc_logger.log_entry(f'****** Applying Signal to Y2 terminal')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_2", ArcFlags.RELAY_CLOSED, NetworkAddresses.ECONET_ARC_BOARD)

        tc_logger.log_entry('***** Allowing the system to stabilize for 5 minutes')
        if not bench_test:
            time.sleep(2 * 60)

        tc_logger.log_entry(f'Checking unit CFM')
        if not bench_test:
            read_obj_compare(tc_logger, response_que, econet_read_obj_que, 'CFM_CURR', modeldata.hpmphcfm, SystemValues.AIRFLOW_TOLERANCE, NetworkAddresses.ECONET_AIR_HANDLER)

        #Starting a "stopwatch"
        start = time.perf_counter()
        
        tc_logger.log_entry(f'***** Resetting unit')
        if not bench_test:
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_1", ArcFlags.RELAY_OPEN, NetworkAddresses.ECONET_ARC_BOARD)
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_2", ArcFlags.RELAY_OPEN, NetworkAddresses.ECONET_ARC_BOARD)
            write_obj(tc_logger, response_que, econet_write_obj_que, "TE_IMC_4", ArcFlags.RELAY_OPEN, NetworkAddresses.ECONET_ARC_BOARD)

        #Waiting for unit to stop
        tc_logger.log_entry(f'***** Waiting for unit to turn off.')
        if not bench_test:
            pwm = read_obj(tc_logger, response_que, econet_read_obj_que, "PWM_FANC", NetworkAddresses.ECONET_AIR_HANDLER)[1][0]
            
            while pwm > 0:
                time.sleep(1)
                pwm = read_obj(tc_logger, response_que, econet_read_obj_que, "PWM_FANC", NetworkAddresses.ECONET_AIR_HANDLER)[1][0]

        #Unit off! Stop the timer
        finish = time.perf_counter()
        time_to_finish = round(finish-start, 2)

        #Validating time is correct length
        if not bench_test:
            tc_logger.log_entry(f'***** Time for unit to shut down: {time_to_finish} seconds. Expected time: {modeldata.aboffdly} seconds.')
            read_obj_compare(tc_logger, response_que, econet_read_obj_que, 'ABOFFDLY', time_to_finish, 20, NetworkAddresses.ECONET_AIR_HANDLER)

        #Enabling comm with the CC for end process
        tc_logger.log_entry(f'Resuming communications with the control center')
        if not bench_test:
            tc_logger.log_entry(f"Writing STOPCOMM to {SystemValues.NO}")
            write_obj(tc_logger, response_que, econet_write_obj_que, "STOPCOMM", SystemValues.NO)

        tc_logger.log_entry(f'{req_trace_csv_data}Pass')
        tc_logger.log_entry(f'***** *** {TEST_CASE_NAME} successfully completed ***\n')
        return_code = (TEST_CASE_NAME, ReturnCodes.ALL_GOOD[1], ReturnCodes.ALL_GOOD[2])
        
    except ConfigError as config_err:
        tc_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {config_err} ***', logging.CRITICAL)
        tc_logger.log_entry(f'{req_trace_csv_data} Fail', logging.CRITICAL)
        return_code = (TEST_CASE_NAME, ReturnCodes.INVALID_SYS_CONFIG[1], ReturnCodes.INVALID_SYS_CONFIG[2])

    except ReadObjError as read_obj_err:
        tc_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {read_obj_err} ***', logging.CRITICAL)
        tc_logger.log_entry(f'{req_trace_csv_data} Fail', logging.CRITICAL)
        return_code = (TEST_CASE_NAME, ReturnCodes.READ_OBJ_ERROR[1], ReturnCodes.READ_OBJ_ERROR[2])

    except WriteObjError as write_obj_err:
        tc_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {write_obj_err} ***', logging.CRITICAL)
        tc_logger.log_entry(f'{req_trace_csv_data} Fail', logging.CRITICAL)
        return_code = (TEST_CASE_NAME, ReturnCodes.WRITE_OBJ_ERROR[1], ReturnCodes.WRITE_OBJ_ERROR[2])

    except ValueCompareError as value_err:
        tc_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {value_err} ***', logging.CRITICAL)
        tc_logger.log_entry(f'{req_trace_csv_data} Fail', logging.CRITICAL)
        return_code = (TEST_CASE_NAME, ReturnCodes.VALUE_COMPARE_ERROR[1], ReturnCodes.VALUE_COMPARE_ERROR[2])
        
    except TerminateError as terminate_err:
        tc_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {terminate_err} ***', logging.CRITICAL)
        tc_logger.log_entry(f'{req_trace_csv_data} Fail', logging.CRITICAL)
        return_code = (TEST_CASE_NAME, ReturnCodes.TERMINATE_ERROR[1], ReturnCodes.TERMINATE_ERROR[2])

    finally:
        #Ends the read/write process, shut system off(if necessary), and satisfies locktimr
        end_process(tc_logger, bench_test, kill_que, response_que, econet_read_obj_que, econet_write_obj_que, turn_system_off=True)
        response_que.put(return_code)  
        # prompt_que.put(SystemFlags.PROMPTS_FINISHED)
    

# Run the main() function to setup all of the processes and queues
def main(bench_test = False):
    '''
    This function will:
        Setup all of the processes (EcoNet bus read/write, logger, and the test process) and start them
        Setup the following queue's:
            response_queue used to send/receive response from EcoNet bus
            econet_write_obj_que: Used for writing objects
            econet_read_obj_que: Used for reading objects
            kill_que: Used for killing the econet_read_write_process

        Setup a log_lock for the logging queue
        Start all of the processes going
            Logging process: Used for logging all of the messages to the console and to a file
            bus_read_write_process: Used for writing to, and reading from the EcoNet bus which opens up the serial port
            test_case_process: Used to run the test case in

    Args:
        bench_test: True or False variable for bench testing only.

    Returns:
        None

    Objects used:
        None

    Raises:
        None
    '''
    #log_lock = Lock()
    log_que = Queue()
    log_configs = LoggingConfigs(log_que)

    # Log the initial message for the test case to start
    main_logger = TestCaseLogger(log_configs.main_logging_config, TEST_CASE_NAME,
                                "***** *** Starting " + TEST_CASE_NAME + " Version " + TEST_CASE_VERSION + " ***")

    # Create an event to stop the logger
    logger_stop_event = Event()
    
    # Create the logging process
    log_process = Process(target=logging_process, name='logger_process',
                          args=(log_configs.logging_process_config, log_que, logger_stop_event))
    log_process.start()
    main_logger.log_entry(f'Started process: {log_process.name}')

    # Create the following queues:
    # response_que - Que that holds the response from the EcoNet bus
    # econet_write_que - Que that holds the object to write.  It is a tuple with the object name and object value
    # econet_read_que - Que that holds the object to read.  It is a tuple with the object name,
    # kill_que: - Que that will be used to terminate the bus_read_write_proc
    response_queue = multiprocessing.Queue()
    econet_write_obj_que = multiprocessing.Queue()
    econet_read_obj_que = multiprocessing.Queue()
    kill_que = multiprocessing.Queue()
    cmd_msg_que = multiprocessing.Queue()
    #prompt_que = multiprocessing.Queue()
    try:
        bus_read_write_proc = Process(target=econet_read_write_process, name='bus_read_write_process',
                                      args=(log_configs.read_write_logging_config, cmd_msg_que, response_queue,
                                            econet_write_obj_que, econet_read_obj_que, kill_que))
        bus_read_write_proc.start()
        main_logger.log_entry(f'Started process: {bus_read_write_proc.name}')

        # Check to see if the bus_read_write_proc is running.  The only failure it can have is if the comm. port can't
        # be opened.  We need a small delay to allow the process to try and open the port and make sure that
        # everything is good before continuing
        time.sleep(1)
        if not bus_read_write_proc.is_alive():
            #main_logger.error('Error in process: %s', bus_read_write_proc.name)
            main_logger.log_entry(f'Error in process: {bus_read_write_proc.name}')
            # Stop the logging process
            #main_logger.info('Stopping process: logger_process...\n\n')
            main_logger.log_entry("Stopping process: logger_process...\n\n")
            logger_stop_event.set()
            log_process.join()
            sys.exit(ReturnCodes.COMM_PORT_ERROR[1])
        

        # Create and start the test case process
        test_case_proc = Process(target=m1ah_heatCool, name=TEST_CASE_NAME,
                                 args=(bench_test, log_configs.test_case_logging_config, cmd_msg_que, 
                                       response_queue, econet_write_obj_que, econet_read_obj_que, kill_que))

        test_case_proc.start()
        main_logger.log_entry(f'Started process: {test_case_proc.name}')
        time.sleep(0.5)

        # Create a user prompt queue.  When a process is created, the stdin is closed.  Therefore, you cannot prompt
        # the user for input.  The main process has the stdin (keyboard input) still open.  So, a queue is created
        # to pass messages and responses back and forth to facilitate getting user input
        #while True:
        #    if prompt_que.qsize() > 0:
        #        user_prompt = prompt_que.get()
        #        # Check to see if we want to end the script
        #        #main_logger.info('prompt_queue data: %s', user_prompt)
        #        if user_prompt == SystemFlags.PROMPTS_FINISHED:
        #            break
        #        # Get the user input and then send it back to the process through the queue
        #        user_response = get_yes_or_no_input(user_prompt)
        #        prompt_que.put(user_response)

        # We now wait for the processes to finish their work.
        bus_read_write_proc.join()
        test_case_proc.join()

        # All processes are done, so the logger can now stop.
        main_logger.log_entry("Telling logger to stop ...\n\n")
        logger_stop_event.set()
        log_process.join()
    
        # Return the return code in the response queue that was put in there by the test case process
        #return(response_queue.get())
        rc = response_queue.get()
        sys.exit(rc[1])
    
    except CommPortError as comm_err:
        main_logger.log_entry(f'***** *** Fatal error in {TEST_CASE_NAME}: {comm_err} ***', logging.CRITICAL)
        sys.exit(-1)

if __name__ == '__main__':
    bad_format = False
    #main(sys.argv[1], sys.argv[2], sys.argv[3])
    num_args = len(sys.argv)
    if num_args == 1:
        main()
    elif num_args == 2:
        # Check the incoming variables and change from strings to boolean values
        if sys.argv[1] == "True":
            main(True)
        elif sys.argv[1] == "False":
            main(False)
        else:
            bad_format = True
    else:
        bad_format = True
        
    if bad_format:
        print("Incorrect number of command line arguments or incorrect values")
        print("Format:  module_name.py True|False")
        print("Example:>python " + TEST_CASE_NAME + ".py True")                
