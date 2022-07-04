# Task 3 Script - Harley Hill
from netmiko import ConnectHandler  # imports connecthandler from netmiko
import getpass  # can prompt the user for a password without printing it in the terminal

print('-------------------------------------')
print('-----Compare Configuration Files-----')
print('------------------&------------------')
print('----Configure Loopback Interfaces----')
print('--------Script by Harley Hill--------')
print('-------------------------------------')
print('')
print('Remember to check the file directories in the code are correct!')
print('')

#  !!! change these file directories but keep the 'r' in front of the directory !!! #
running_config_file_location = r"C:\Users\harle\Desktop\python_files\running_config.txt"
startup_config_file_location = r"C:\Users\harle\Desktop\python_files\startup_config.txt"
offline_config_file_location = r"C:\Users\harle\Desktop\python_files\offline_config.txt"
loopback_addresses_file_location = r"C:\Users\harle\Desktop\python_files\loopback_addresses.txt"


# this function compares running config to either the start-up config or an offline config
def compare_run_to_start_or_offline(running_config_file, second_config_file):
    with open(running_config_file, "r") as infile:  # opens the running config text file
        running_config_lines = infile.readlines()  # reads each line and stores in variable

    with open(second_config_file, "r") as infile:  # opens the second config text file
        second_config_lines = infile.readlines()  # reads each line and stores in variable

    # goes through line by line through both files checking to see if that line exists in the other file (variable)
    # if the line isn't found in the other file then it is unique and is saved to the variable: only_in_...
    only_in_running_config_lines = [i for i in running_config_lines if i not in second_config_lines]
    only_in_second_config_lines = [i for i in second_config_lines if i not in running_config_lines]

    if only_in_running_config_lines:  # checks that the variable isn't empty if it is then skip
        print('Only in running config:')
        print('')  # formatting
        for line in only_in_running_config_lines:
            print(line)  # goes through each unique line and prints

    if only_in_second_config_lines:  # checks that the variable isn't empty if it is then skip
        print('')  # formatting
        if second_config_file == offline_config_file_location:  # decides whether to print offline or config based on second config file
            print('Only in offline config:')
        else:
            print('Only in start-up config:')
        print('')  # formatting
        for line in only_in_second_config_lines:
            print(line)  # goes through each unique line and prints


# this section can be used instead of the above section if you want to write the differences to a file as opposed to printing them
#    with open(r"C:\Users\harle\Desktop\python_files\difference.txt", "w") as outfile:
#        if only_in_running_config_lines:
#            outfile.write('Only in running config:')
#            outfile.write('')  # formatting
#            for line in only_in_running_config_lines:
#                outfile.write(line)  # writes each line to file
#
#        if only_in_second_config_lines:
#            outfile.write('')
#            if second_config_file == offline_config_file_location:  # decides whether to write offline or config based on second config file
#                outfile.write('Only in offline config:')
#            else:
#                outfile.write('Only in start-up config:')
#            outfile.write('')  # formatting
#            for line in only_in_second_config_lines:
#                outfile.write(line)  # writes each line to file


# allows user to enter details and establishes connection to a router using netmiko
def setup():
    # takes login information from the user and stores in variables
    print('Enter the details of the device you want to configure.')
    ip_address = input('Enter device IP address: ')
    username = input('Enter Username: ')
    password = getpass.getpass(prompt='Enter Password: ')  # getpass is used to hide the text as the password is entered
    secret = getpass.getpass(prompt='Enter enable password: ')  # getpass is used to hide the text as the password is entered

    # ConnectHandler is an inbuilt class that allows you to parse information into the device login process
    session = ConnectHandler(device_type='cisco_ios', ip=ip_address, username=username, password=password, secret=secret)

    # attempts to connect to the device with the specified info above
    session.enable()  # enters privileged mode for the session object
    return session  # returns session object (instantiation of ConnectHandler)


# this function allows the user to configure a loopback interface-
# either for a specific device manually or multiple devices from a file
def configure_loopback(loopback_addresses_file):
    print('Choose loopback configuration method: 1. Configure loopback manually for a single router')
    print('                                      2. Configure loopback address(es) from file')
    print('OR                                    3. To go back')
    choice = input('Enter: ')

    if choice == '1':  # configures a loopback address for a single router
        session = setup()
        ip_addr = input("Enter the loopback IP address: ")  # ask the user which ip address they would like to assign to the loopback interface
        sub_mask = input("Enter the subnet mask (x.x.x.x): ")  # subnet mask must be entered as x.x.x.x
        config_commands = ["int loopback 1", "ip address " + ip_addr + ' ' + sub_mask]  # list of commands to be entered
        session.send_config_set(config_commands)  # sends commands in config mode
        print('Configuring loopback address: ' + ip_addr)
        print('Loopback address ' + ip_addr + ' configured')
        session.disconnect()  # disconnects from session
        main()  # returns to main decision loop

    elif choice == '2':
        loopback_list = []  # list that will store information from file
        with open(loopback_addresses_file_location, 'r') as infile:  # opens the loopback_addresses file
            for line in infile:
                if "ip address," not in line:  # excludes the first line
                    line = line.split(',')  # splits the line up at ever comma
                    loopback_list.append(line)  # adds the split items to the list

            for i in range(1, len(loopback_list)):  # for each line in the list
                # config_commands iterates through each line in the list and holds a list of commands to be entered
                config_commands = ["int loopback 1", "ip address " + loopback_list[i][4] + ' ' + loopback_list[i][5]]
                # creates a connection to a new device each iteration of the loop
                session = ConnectHandler(device_type='cisco_ios', ip=loopback_list[i][0], username=loopback_list[i][1], password=loopback_list[i][2], secret=loopback_list[i][3])
                print('Connecting to device: ' + loopback_list[i][0])  # prints which device is being connected too
                session.enable()  # enters privileged mode
                session.send_config_set(config_commands)  # enters config_commands in global configuration mode
                print('Assigning loopback address: ' + loopback_list[i][4])  # prints the loopback address being assigned

            print('All loopback addresses on all devices successfully configured!')
            session.disconnect()  # diconnects from last connected router
            main()  # returns to main decision loop

    elif choice == '3':
        main()  # returns to main decision loop

    else:  # any other input
        print('Invalid input, try again')
        configure_loopback(loopback_addresses_file)  # restart configure loopback


# this function saves the running config of the open session to the file
def running_conf_setup(session):
    # stores the output of 'show running-config' in run_conf
    run_conf = session.send_command("show running-config")
    # opens running_config.txt and then writes into it the contents of run_conf (show running config)
    running_conf_file = open(running_config_file_location, "w")
    running_conf_file.write(run_conf)
    running_conf_file.close()  # closes the file


# contains the main decision loop
def main():
    print('Please select: 1. compare the running config to the start up config')
    print('               2. compare the running config to an offline config')
    print('               3. configure loopback address on router(s)')
    print('               4. exit')
    decision = input('Enter choice: ')  # takes user input

    if decision == '1':  # compares running config to start-up config
        session = setup()  # runs initial connection to router
        running_conf_setup(session)
        # stores the output of 'show startup-config' in start_conf
        start_conf = session.send_command("show startup-config")  # makes use of the session object
        # opens a text file and then writes into it the contents of start_conf
        start_conf_file = open(startup_config_file_location, "w")
        start_conf_file.write(start_conf)
        start_conf_file.close()  # closes the file
        # calls the comparison function passing in the running and start-up config
        compare_run_to_start_or_offline(running_config_file_location, startup_config_file_location)
    elif decision == '2':  # compares running config to offline config file
        session = setup()
        running_conf_setup(session)
        # calls the comparison function passing in the running and offline config
        compare_run_to_start_or_offline(running_config_file_location, offline_config_file_location)
    elif decision == '3':  # allows the user to configure loopback interfaces
        # passes the loopback addresses file location as an argument
        configure_loopback(loopback_addresses_file_location)
    elif decision == '4':  # stops the program
        exit()
    else:  # any other input
        print('Invalid input, try again')
        main()  # if the user enters an invalid input start main again


main()  # runs the main decision loop function
