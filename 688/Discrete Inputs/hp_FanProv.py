'''
Created on
@author:
'''
import logging.config
import time
import sys
import os
import multiprocessing

sys.path.append(os.getcwd()) 

from multiprocessing import Process, Queue, Event
from SystemConfig.logging_configs import LoggingConfigs
from econet_driver.econet_constants import ReturnCodes, SystemValues
from econet_driver.econet_utilities import econet_read_write_process, logging_process,\
    pre_parse_util, end_process
from SystemConfig.sys_setup import sys_setup
from SystemConfig.test_case_logger import TestCaseLogger
from econet_driver.econet_exceptions import ConfigError, CommPortError, ReadObjError, ValueCompareError,\
    WriteObjError, TerminateError
from econet_driver.econet_system_config import ConfigFile
 
TEST_CASE_NAME = "hp_FanProv"
TEST_CASE_VERSION = "01.00.00"
 
#use the first def in case of prompt user needed
#def tc_xxxx(bench_test, log_config, cmd_msg_que, response_que, econet_write_obj_que, econet_read_obj_que, kill_que, prompt_que):
def tc_xxxx(bench_test, log_config, log_lock, response_que, econet_write_obj_que, econet_read_obj_que, kill_que):
    """
     Test Case Requirement:
    ACHPC-SR-218 - Fan Proving Switch
 
    Test Case Purpose:
        The purpose of this test case is to test the functionality of the Fan Proving Switch.
 
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
 
    User input required: xxxx
 
    Error Injection: xxxx
 
    Test Group: xxxx
 
    System Config:
        Indoor Unit: xxxx Valid values: Variable Speed Air Handler, Modulating Furnace, 2-Stage Furnace, Constant Torque Air Handler
        Outdoor Unit: xxxx Valid values: Gen 1 RP2036, RA17 2 Stage, RP17 3 Speed
        Water Heater: xxxx Valid values: HPWH1, HPWH2, HPWH3
 
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
        sys_setup(tc_logger, response_que, econet_write_obj_que, econet_read_obj_que, system_config, file_name, True, bench_test)
       
        #****************************************************************************************************************
        #****************************************************************************************************************
        #  xxxx Put code here...
        #
        # Example of a read object command for the EcoNet object SPT
        # read_resp = read_obj(tc_logger, response_que, econet_read_obj_que, "SPT")
        # current_temp = read_resp[1][0]
        #
        # Example of a read object with a compare command and a +/- 0.5 tolerance
        # read_obj_compare(tc_logger, response_que, econet_read_obj_que, "SPT", current_temp, 0.5)
        #
        # Example of a write object command to set the EcoNet object COOLSETP to 70.0 degrees
        # Write the value for the COOLSETP
        # obj_value = 70.0
        # tc_logger.log_entry(f'***** Setting COOLSETP to {obj_value:2.1f}')
        # write_obj(tc_logger, response_que, econet_write_obj_que, "COOLSETP", obj_value)
        # tc_logger.log_entry(f'***** COOLSETP set to {obj_value:2.1f}')
        #
        # Byte Stream Read
        # Example of byte stream read, and access specific object within the bytestream. Here we are reading the
        # bytestream HWELMODL, and accessing the objects mdprtnum and cfmdhuma.
        # With read_obj returning a bytestream class, we have access to all the object within as
        # instance variables (in lowercase).
        # tc_logger.log_entry("***** Reading HWELMODL")
        # obj_read = read_obj(tc_logger, response_que, econet_read_obj_que, "HWELMODL", NetworkAddresses.ECONET_FURNACE)
        # hwelmodl_obj = obj_read[1]
        # tc_logger.log_entry(f'***** HWELMODL.MDPRTNUM: {hwelmodl_obj.mdprtnum}')
        # tc_logger.log_entry(f'***** HWELMODL.CFMDHUMA: {hwelmodl_obj.cfmdhuma}')
        #
        # For byte stream write, we have two ways of writing to a bytestream. First we have single write.
        # Example of single-object write, no previous byte stream read is needed.
        # Note that the last parameter in write_bytestream is the string of the object in lowercase
        # tc_logger.log_entry(f'***** changing HWELMODL.mdprtnum to 1234567890123456')
        # write_bytestream(tc_logger, response_que,  econet_read_obj_que, econet_write_obj_que, "HWELMODL",
        #                   '1234567890123456', NetworkAddresses.ECONET_FURNACE, False, "mdprtnum")
        #
        # For the multi-object write to work, a bytestream read must be performed beforehand so you can have access to
        # the bytestream class.Note instead of passing in a value as the object value to be written,
        # we make changes directly to the class attributes, and pass in the actuall bytestream class (hwelmodl_obj)    
        # tc_logger.log_entry(f'***** changing HWELMODL.mdprtnum to 1234567890123456')
        # tc_logger.log_entry(f'***** changing HWELMODL.cfmdhuma to 20')
        # hwelmodl_obj.mdprtnum = '1234567890123456'
        # hwelmodl_obj.cfmdhuma  = 20        
        # write_obj(tc_logger, response_que, econet_write_obj_que, "HWELMODL", hwelmodl_obj, NetworkAddresses.ECONET_FURNACE)
        #
        # Example of how to prompt the user for user input.  Note if using prompts, comment in all uses of prompt_que
        # Prompt the user to verify that the outdoor ambient sensor is setup properly
        # user_prompt = (f'Is the outdoor ambient sensor setup? (Y/N) ==>')
        # if not prompt_user(tc_logger, prompt_que, user_prompt):
        #     raise UserInputIndicatedError(f'System not setup properly', logging.CRITICAL)
        #
        #****************************************************************************************************************
        #****************************************************************************************************************
       
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
        test_case_proc = Process(target=hp_FanProv, name=TEST_CASE_NAME,
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
