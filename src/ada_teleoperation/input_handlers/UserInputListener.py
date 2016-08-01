import numpy as np
from threading import Lock
import time
import rospy

from abc import ABCMeta, abstractmethod


class UserInputListener(object):
  __metaclass__ = ABCMeta

  def __init__(self):
    self.inputlock = Lock()
    self.init_listener()
    self.most_recent_message = None

    #keep track of the last state of buttons we returned
    #in order to keep track of when button states change
    self.last_buttons_returned = None

  def callback(self, data):
    with self.inputlock:
      self.most_recent_message = data
      
  def init_listener(self):
    rospy.Subscriber(self.input_topic_name, self.input_message_type, self.callback)

  #TODO handle case of no most_recent_message without infinite loop
  def get_most_recent_cmd(self):
    while self.most_recent_message is None:
      print 'Error: No user input to return'
      time.sleep(0)

    with self.inputlock:
      data = self.message_to_data(self.most_recent_message)

    #set the change between the last buttons returned as data
    #and the currently pressed buttons
    if self.last_buttons_returned is None:
      data.button_changes = np.zeros(len(data.buttons))
    else:
      data.button_changes = data.buttons - self.last_buttons_returned
    self.last_buttons_returned = data.buttons

    return data

  @abstractmethod
  def message_to_data(self, message):
    raise NotImplementedError("Must override message_to_data")


#axes and buttons should have a consistent order for different inputs
#axes should be forward-backward, then left-right.
#first button should correspond to switching modes
#second button (if applicable) should correspond to toggling assistance
class UserInputData(object):
  def __init__(self, axes=list(), buttons=list(), button_changes=list()):
    self.axes = axes
    self.buttons = buttons
    self.button_changes = button_changes

  def __str__(self):
    return 'axes: ' + str(self.axes) + '  buttons: ' + str(self.buttons)