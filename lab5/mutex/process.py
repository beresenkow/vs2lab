import logging
import random
import time

from constMutex import ENTER, RELEASE, ALLOW, ACTIVE, REMOVE


class Process:
    """
    Implements access management to a critical section (CS) via fully
    distributed mutual exclusion (MUTEX).

    Processes broadcast messages (ENTER, ALLOW, RELEASE) timestamped with
    logical (lamport) clocks. All messages are stored in local queues sorted by
    logical clock time.

    Processes follow different behavioral patterns. An ACTIVE process competes 
    with others for accessing the critical section. A PASSIVE process will never 
    request to enter the critical section itself but will allow others to do so.

    A process broadcasts an ENTER request if it wants to enter the CS. A process
    that doesn't want to ENTER replies with an ALLOW broadcast. A process that
    wants to ENTER and receives another ENTER request replies with an ALLOW
    broadcast (which is then later in time than its own ENTER request).

    A process enters the CS if a) its ENTER message is first in the queue (it is
    the oldest pending message) AND b) all other processes have sent messages
    that are younger (either ENTER or ALLOW). RELEASE requests purge
    corresponding ENTER requests from the top of the local queues.

    Message Format:

    <Message>: (Timestamp, Process_ID, <Request_Type>)

    <Request Type>: ENTER | ALLOW  | RELEASE | REMOVE

    """

    def __init__(self, chan):
        self.channel = chan  # Create ref to actual channel
        self.process_id = self.channel.join('proc')  # Find out who you are
        self.all_processes: list = []  # All procs in the proc group
        self.other_processes: list = []  # Needed to multicast to others
        self.queue = []  # The request queue list
        self.clock = 0  # The current logical clock
        self.peer_name = 'unassigned'  # The original peer name
        self.peer_type = 'unassigned'  # A flag indicating behavior pattern
        self.logger = logging.getLogger("vs2lab.lab5.mutex.process.Process")
        self.working_processes = []
        self.timeout_count = 0

    def __mapid(self, id='-1'):
        # format channel member address
        if id == '-1':
            id = self.process_id
        return 'Proc-'+str(id)

    def __cleanup_queue(self):
        if len(self.queue) > 0:
            # self.queue.sort(key = lambda tup: tup[0])
            self.queue.sort()
            # There should never be old ALLOW messages at the head of the queue
            while self.queue[0][2] == ALLOW:
                del (self.queue[0])
                if len(self.queue) == 0:
                    break

    def __request_to_enter(self):
        self.clock = self.clock + 1  # Increment clock value
        request_msg = (self.clock, self.process_id, ENTER)
        self.queue.append(request_msg)  # Append request to queue
        self.__cleanup_queue()  # Sort the queue
        self.channel.send_to(self.other_processes, request_msg)  # Send request

    def __allow_to_enter(self, requester):
        if not self.queue:
            return False
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, ALLOW)
        self.channel.send_to([requester], msg)  # Permit other
    
    # BEGIN NEW
    # Erhöcht die eigene clock und sendet Nachricht mit Prozess der entfernt werden soll
    def __remove_failed_process(self, failed_process):
        self.clock += 1
        msg = (self.clock, failed_process, REMOVE)
        self.channel.send_to(self.other_processes, msg)
        self.logger.info(f"Broadcasted removal of failed process: {self.__mapid(failed_process)}")
    # END NEW

    def __release(self):
        # need to be first in queue to issue a release
        assert self.queue[0][1] == self.process_id, 'State error: inconsistent local RELEASE'

        # construct new queue from later ENTER requests (removing all ALLOWS)
        tmp = [r for r in self.queue[1:] if r[2] == ENTER]
        self.queue = tmp  # and copy to new queue
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, RELEASE)
        # Multicast release notification
        self.channel.send_to(self.other_processes, msg)

    def __allowed_to_enter(self):
        if not self.queue:
            return False
        first_in_queue = self.queue[0][1] == self.process_id

        if not self.queue:
            self.logger.warning(f"Queue is empty for process {self.process_id}. Cannot enter critical section.")
            return False
        """
        try:
            first_in_queue = self.queue[0][1] == self.process_id
            return first_in_queue
        except IndexError as e:
            self.logger.error(f"Error accessing queue for process {self.process_id}: {e}")
            return False
        """
        # See who has sent a message (the set will hold at most one element per sender)
        processes_with_later_message = set([req[1] for req in self.queue[1:]])
        # Access granted if this process is first in queue and all others have answered (logically) later
        first_in_queue = self.queue[0][1] == self.process_id
        all_have_answered = len(self.other_processes) == len(
            processes_with_later_message)
        return first_in_queue and all_have_answered
    
    def __receive(self):
        _receive = self.channel.receive_from(self.other_processes, 3)
        if _receive:
            msg = _receive[1]
            self.clock = max(self.clock, msg[0]) + 1
            self.logger.debug(f"{self.__mapid()} received {msg[2]} from {self.__mapid(msg[1])}")

            if msg[2] == ENTER:
                self.queue.append(msg)
                self.__allow_to_enter(msg[1])
            elif msg[2] == ALLOW:
                self.queue.append(msg)
            elif msg[2] == RELEASE:
                if self.queue and self.queue[0][1] == msg[1]:
                    self.queue.pop(0)
            elif msg[2] == REMOVE:
                self.queue = [item for item in self.queue if item[1] != msg[1]]
                if msg[1] in self.other_processes:
                    self.other_processes.remove(msg[1])
                self.logger.info(f"Removed failed process: {self.__mapid(msg[1])}")
            self.__cleanup_queue()
        else:
            self.logger.warning(f"{self.__mapid()} timed out. Local queue: {self.queue}")
            self.__handle_timeout()

    def __handle_timeout(self):
        if not self.queue:
            return
        failed_process = self.queue[0][1]
        self.logger.warning(f"Detected failure of process: {self.__mapid(failed_process)}")
        self.__remove_failed_process(failed_process)
        if failed_process in self.other_processes:
            self.other_processes.remove(failed_process)
        self.queue = [item for item in self.queue if item[1] != failed_process]
        self.__cleanup_queue()
        self.logger.info(f"Removed failed process: {self.__mapid(failed_process)}")
        self.__cleanup_queue()
    
    def init(self, peer_name, peer_type):
        self.channel.bind(self.process_id)

        self.all_processes = list(self.channel.subgroup('proc'))
        # sort string elements by numerical order
        self.all_processes.sort(key=lambda x: int(x))

        self.other_processes = list(self.channel.subgroup('proc'))
        self.other_processes.remove(self.process_id)

        self.peer_name = peer_name  # assign peer name
        self.peer_type = peer_type  # assign peer behavior

        self.logger.info("{} joined channel as {}.".format(
            peer_name, self.__mapid()))

    def run(self):
        while True:
            # Enter the critical section if
            # 1) there are more than one process left and
            # 2) this peer has active behavior and
            # 3) random is true
            if len(self.all_processes) > 1 and \
                    self.peer_type == ACTIVE and \
                    random.choice([True, False]):
                self.logger.debug("{} wants to ENTER CS at CLOCK {}."
                                    .format(self.__mapid(), self.clock))

                self.__request_to_enter()
                while not self.__allowed_to_enter():
                    self.__receive()

                # Stay in CS for some time ...
                sleep_time = random.randint(0, 2000)
                self.logger.debug("{} enters CS for {} milliseconds."
                                    .format(self.__mapid(), sleep_time))
                print(" CS <- {}".format(self.__mapid()))
                time.sleep(sleep_time/1000)

                # ... then leave CS
                print(" CS -> {}".format(self.__mapid()))
                self.__release()
                continue

            # Occasionally serve requests to enter (
            if random.choice([True, False]):
                self.__receive()
