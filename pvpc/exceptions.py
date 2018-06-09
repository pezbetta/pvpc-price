class DateError(Exception):
    def __init__(self):
       Exception.__init__(
           self,"The information for this date can not be recover"
       )